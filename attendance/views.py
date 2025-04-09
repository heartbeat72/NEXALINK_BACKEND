from django.db.models import Count, Case, When, IntegerField, F, Q
from django.utils import timezone
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import AttendanceRecord, AttendancePercentage
from .serializers import (
    AttendanceRecordSerializer, AttendancePercentageSerializer,
    BulkAttendanceSerializer, AttendanceStatisticsSerializer
)
from academics.models import Course
from users.models import Student, Faculty
from users.permissions import IsAdminUser, IsFacultyUser, IsStudentUser

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing attendance records."""
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'date', 'status']
    ordering_fields = ['date', 'marked_at']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'bulk_create']:
            permission_classes = [IsAdminUser | IsFacultyUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set the marked_by field to the current faculty user."""
        if self.request.user.role == 'faculty':
            serializer.save(marked_by=self.request.user.faculty_profile)
        else:
            serializer.save()
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple attendance records at once."""
        serializer = BulkAttendanceSerializer(data=request.data)
        
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            date = serializer.validated_data['date']
            attendance_data = serializer.validated_data['attendance_data']
            
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return Response(
                    {"detail": "Course not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if the user is the faculty assigned to this course or an admin
            if request.user.role == 'faculty' and request.user.faculty_profile != course.faculty:
                return Response(
                    {"detail": "You are not authorized to mark attendance for this course."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Process attendance records
            created_records = []
            errors = []
            
            for record in attendance_data:
                try:
                    student = Student.objects.get(id=record['student_id'])
                    
                    # Check if student is enrolled in the course
                    if not student.courses.filter(id=course.id).exists():
                        errors.append({
                            "student_id": record['student_id'],
                            "error": "Student is not enrolled in this course."
                        })
                        continue
                    
                    # Create or update attendance record
                    attendance, created = AttendanceRecord.objects.update_or_create(
                        student=student,
                        course=course,
                        date=date,
                        defaults={
                            'status': record['status'],
                            'remarks': record.get('remarks', ''),
                            'marked_by': request.user.faculty_profile if request.user.role == 'faculty' else None
                        }
                    )
                    
                    created_records.append(attendance)
                    
                except Student.DoesNotExist:
                    errors.append({
                        "student_id": record['student_id'],
                        "error": "Student not found."
                    })
            
            # Update attendance percentages
            self._update_attendance_percentages(course)
            
            return Response({
                "created_count": len(created_records),
                "errors": errors
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_attendance(self, request):
        """Get attendance records for the current student."""
        if request.user.role != 'student':
            return Response(
                {"detail": "Only students can access their attendance."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user.student_profile
        
        # Filter by course if provided
        course_id = request.query_params.get('course_id')
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                attendance = AttendanceRecord.objects.filter(student=student, course=course)
            except Course.DoesNotExist:
                return Response(
                    {"detail": "Course not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            attendance = AttendanceRecord.objects.filter(student=student)
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            attendance = attendance.filter(date__gte=start_date)
        
        if end_date:
            attendance = attendance.filter(date__lte=end_date)
        
        serializer = self.get_serializer(attendance, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def course_attendance(self, request):
        """Get attendance records for a specific course."""
        if request.user.role not in ['faculty', 'admin']:
            return Response(
                {"detail": "Only faculty and admin can access course attendance."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {"detail": "Course ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            course = Course.objects.get(id=course_id)
            
            # Check if the user is the faculty assigned to this course or an admin
            if request.user.role == 'faculty' and request.user.faculty_profile != course.faculty:
                return Response(
                    {"detail": "You are not authorized to view attendance for this course."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Filter by date if provided
            date = request.query_params.get('date')
            if date:
                attendance = AttendanceRecord.objects.filter(course=course, date=date)
            else:
                attendance = AttendanceRecord.objects.filter(course=course)
            
            serializer = self.get_serializer(attendance, many=True)
            return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get attendance statistics."""
        serializer = AttendanceStatisticsSerializer(data=request.query_params)
        
        if serializer.is_valid():
            course_id = serializer.validated_data.get('course_id')
            student_id = serializer.validated_data.get('student_id')
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            
            # Base query
            query = AttendanceRecord.objects.all()
            
            # Apply filters
            if course_id:
                query = query.filter(course_id=course_id)
            
            if student_id:
                query = query.filter(student_id=student_id)
            
            if start_date:
                query = query.filter(date__gte=start_date)
            
            if end_date:
                query = query.filter(date__lte=end_date)
            
            # Calculate statistics
            stats = query.aggregate(
                total=Count('id'),
                present=Count(Case(When(status='present', then=1), output_field=IntegerField())),
                absent=Count(Case(When(status='absent', then=1), output_field=IntegerField())),
                late=Count(Case(When(status='late', then=1), output_field=IntegerField()))
            )
            
            # Calculate percentage
            if stats['total'] > 0:
                stats['present_percentage'] = (stats['present'] / stats['total']) * 100
                stats['absent_percentage'] = (stats['absent'] / stats['total']) * 100
                stats['late_percentage'] = (stats['late'] / stats['total']) * 100
            else:
                stats['present_percentage'] = 0
                stats['absent_percentage'] = 0
                stats['late_percentage'] = 0
            
            return Response(stats)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _update_attendance_percentages(self, course):
        """Update attendance percentages for all students in a course."""
        students = course.students.all()
        
        for student in students:
            total_records = AttendanceRecord.objects.filter(student=student, course=course).count()
            
            if total_records > 0:
                present_records = AttendanceRecord.objects.filter(
                    student=student, 
                    course=course, 
                    status__in=['present', 'late']
                ).count()
                
                percentage = (present_records / total_records) * 100
                
                AttendancePercentage.objects.update_or_create(
                    student=student,
                    course=course,
                    defaults={'percentage': percentage}
                )

class AttendancePercentageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing attendance percentages."""
    queryset = AttendancePercentage.objects.all()
    serializer_class = AttendancePercentageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'course']
    ordering_fields = ['percentage', 'last_updated']
    
    @action(detail=False, methods=['get'])
    def my_percentages(self, request):
        """Get attendance percentages for the current student."""
        if request.user.role != 'student':
            return Response(
                {"detail": "Only students can access their attendance percentages."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user.student_profile
        percentages = AttendancePercentage.objects.filter(student=student)
        
        serializer = self.get_serializer(percentages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def course_percentages(self, request):
        """Get attendance percentages for a specific course."""
        if request.user.role not in ['faculty', 'admin']:
            return Response(
                {"detail": "Only faculty and admin can access course attendance percentages."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {"detail": "Course ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            course = Course.objects.get(id=course_id)
            
            # Check if the user is the faculty assigned to this course or an admin
            if request.user.role == 'faculty' and request.user.faculty_profile != course.faculty:
                return Response(
                    {"detail": "You are not authorized to view attendance for this course."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            percentages = AttendancePercentage.objects.filter(course=course)
            serializer = self.get_serializer(percentages, many=True)
            return Response(serializer.data)
            
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )
