from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import IAComponent, IAMark, IATotal
from .serializers import (
    IAComponentSerializer, IAMarkSerializer, IATotalSerializer, BulkIAMarkSerializer
)
from academics.models import Course
from users.models import Student
from users.permissions import IsAdminUser, IsFacultyUser, IsStudentUser

class IAComponentViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing IA components."""
    queryset = IAComponent.objects.all()
    serializer_class = IAComponentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course']
    ordering_fields = ['order', 'name']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser | IsFacultyUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def course_components(self, request):
        """Get IA components for a specific course."""
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {"detail": "Course ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        components = IAComponent.objects.filter(course_id=course_id).order_by('order')
        serializer = self.get_serializer(components, many=True)
        return Response(serializer.data)

class IAMarkViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing IA marks."""
    queryset = IAMark.objects.all()
    serializer_class = IAMarkSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'component', 'component__course']
    ordering_fields = ['marked_at']
    
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
        """Create multiple IA marks at once."""
        serializer = BulkIAMarkSerializer(data=request.data)
        
        if serializer.is_valid():
            component_id = serializer.validated_data['component_id']
            marks_data = serializer.validated_data['marks_data']
            
            try:
                component = IAComponent.objects.get(id=component_id)
            except IAComponent.DoesNotExist:
                return Response(
                    {"detail": "IA Component not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if the user is the faculty assigned to this course or an admin
            if request.user.role == 'faculty':
                if request.user.faculty_profile != component.course.faculty:
                    return Response(
                        {"detail": "You are not authorized to mark IA for this course."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Process IA marks
            created_marks = []
            errors = []
            
            for record in marks_data:
                try:
                    student = Student.objects.get(id=record['student_id'])
                    
                    # Check if student is enrolled in the course
                    if not student.courses.filter(id=component.course.id).exists():
                        errors.append({
                            "student_id": record['student_id'],
                            "error": "Student is not enrolled in this course."
                        })
                        continue
                    
                    # Validate marks
                    marks = float(record['marks'])
                    if marks &lt; 0 or marks > float(component.max_marks):
                        errors.append({
                            "student_id": record['student_id'],
                            "error": f"Marks must be between 0 and {component.max_marks}."
                        })
                        continue
                    
                    # Create or update IA mark
                    ia_mark, created = IAMark.objects.update_or_create(
                        student=student,
                        component=component,
                        defaults={
                            'marks': marks,
                            'remarks': record.get('remarks', ''),
                            'marked_by': request.user.faculty_profile if request.user.role == 'faculty' else None
                        }
                    )
                    
                    created_marks.append(ia_mark)
                    
                except Student.DoesNotExist:
                    errors.append({
                        "student_id": record['student_id'],
                        "error": "Student not found."
                    })
            
            # Update IA totals
            self._update_ia_totals(component.course)
            
            return Response({
                "created_count": len(created_marks),
                "errors": errors
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_marks(self, request):
        """Get IA marks for the current student."""
        if request.user.role != 'student':
            return Response(
                {"detail": "Only students can access their IA marks."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user.student_profile
        
        # Filter by course if provided
        course_id = request.query_params.get('course_id')
        if course_id:
            marks = IAMark.objects.filter(student=student, component__course_id=course_id)
        else:
            marks = IAMark.objects.filter(student=student)
        
        serializer = self.get_serializer(marks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def course_marks(self, request):
        """Get IA marks for a specific course."""
        if request.user.role not in ['faculty', 'admin']:
            return Response(
                {"detail": "Only faculty and admin can access course IA marks."},
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
                    {"detail": "You are not authorized to view IA marks for this course."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Filter by component if provided
            component_id = request.query_params.get('component_id')
            if component_id:
                marks = IAMark.objects.filter(component__course=course, component_id=component_id)
            else:
                marks = IAMark.objects.filter(component__course=course)
            
            serializer = self.get_serializer(marks, many=True)
            return Response(serializer.data)
            
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _update_ia_totals(self, course):
        """Update IA totals for all students in a course."""
        students = course.students.all()
        components = IAComponent.objects.filter(course=course)
        total_weightage = components.aggregate(total=Sum('weightage'))['total'] or 0
        
        for student in students:
            # Get all marks for this student in this course
            marks = IAMark.objects.filter(student=student, component__course=course)
            
            if marks.exists():
                # Calculate weighted total
                weighted_total = 0
                for mark in marks:
                    weighted_total += (mark.marks / mark.component.max_marks) * mark.component.weightage
                
                # Calculate percentage
                percentage = (weighted_total / total_weightage) * 100 if total_weightage > 0 else 0
                
                # Update or create IA total
                IATotal.objects.update_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'total_marks': weighted_total,
                        'out_of': total_weightage,
                        'percentage': percentage
                    }
                )

class IATotalViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing IA totals."""
    queryset = IATotal.objects.all()
    serializer_class = IATotalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'course']
    ordering_fields = ['percentage', 'last_updated']
    
    @action(detail=False, methods=['get'])
    def my_totals(self, request):
        """Get IA totals for the current student."""
        if request.user.role != 'student':
            return Response(
                {"detail": "Only students can access their IA totals."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user.student_profile
        
        # Filter by course if provided
        course_id = request.query_params.get('course_id')
        if course_id:
            totals = IATotal.objects.filter(student=student, course_id=course_id)
        else:
            totals = IATotal.objects.filter(student=student)
        
        serializer = self.get_serializer(totals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def course_totals(self, request):
        """Get IA totals for a specific course."""
        if request.user.role not in ['faculty', 'admin']:
            return Response(
                {"detail": "Only faculty and admin can access course IA totals."},
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
                    {"detail": "You are not authorized to view IA totals for this course."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            totals = IATotal.objects.filter(course=course)
            serializer = self.get_serializer(totals, many=True)
            return Response(serializer.data)
            
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND
            )
