from django.db.models import Avg, Count, Sum, F, Q, Case, When, Value, IntegerField
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import EngagementRecord, PerformanceRecord, AnalyticsReport
from .serializers import (
    EngagementRecordSerializer, PerformanceRecordSerializer, AnalyticsReportSerializer,
    AttendanceAnalyticsSerializer, PerformanceAnalyticsSerializer,
    EngagementAnalyticsSerializer, FeedbackAnalyticsSerializer
)
from users.permissions import IsAdminUser, IsFacultyUser, IsStudentUser
from attendance.models import AttendanceRecord
from feedback.models import Feedback

class EngagementRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing engagement records."""
    queryset = EngagementRecord.objects.all()
    serializer_class = EngagementRecordSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAdminUser]
        elif self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set the user and user_type fields based on the current user."""
        user = self.request.user
        
        if user.role == 'student':
            user_type = 'student'
        elif user.role == 'faculty':
            user_type = 'faculty'
        else:
            user_type = 'admin'
        
        serializer.save(user=user, user_type=user_type)

class PerformanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing performance records."""
    queryset = PerformanceRecord.objects.all()
    serializer_class = PerformanceRecordSerializer
    
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
    def my_performance(self, request):
        """Get performance records for the current student."""
        if request.user.role != 'student':
            return Response(
                {"detail": "Only students can access their performance records."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user.student_profile
        records = PerformanceRecord.objects.filter(student=student)
        
        # Filter by course if provided
        course_id = request.query_params.get('course_id')
        if course_id:
            records = records.filter(course_id=course_id)
        
        # Filter by score type if provided
        score_type = request.query_params.get('score_type')
        if score_type:
            records = records.filter(score_type=score_type)
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            records = records.filter(date__gte=start_date)
        
        if end_date:
            records = records.filter(date__lte=end_date)
        
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)

class AnalyticsReportViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing analytics reports."""
    queryset = AnalyticsReport.objects.all()
    serializer_class = AnalyticsReportSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def attendance_analytics(self, request):
        """Get attendance analytics."""
        serializer = AttendanceAnalyticsSerializer(data=request.query_params)
        
        if serializer.is_valid():
            course_id = serializer.validated_data.get('course_id')
            student_id = serializer.validated_data.get('student_id')
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            
            # Check permissions
            if student_id and request.user.role == 'student' and request.user.student_profile.id != student_id:
                return Response(
                    {"detail": "You can only view your own attendance analytics."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if course_id and request.user.role == 'faculty':
                # Check if the faculty teaches this course
                if not request.user.faculty_profile.courses.filter(id=course_id).exists():
                    return Response(
                        {"detail": "You can only view attendance analytics for courses you teach."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
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
            
            # Calculate overall statistics
            overall_stats = query.aggregate(
                total=Count('id'),
                present=Count(Case(When(status='present', then=1), output_field=IntegerField())),
                absent=Count(Case(When(status='absent', then=1), output_field=IntegerField())),
                late=Count(Case(When(status='late', then=1), output_field=IntegerField()))
            )
            
            # Calculate percentages
            if overall_stats['total'] > 0:
                overall_stats['present_percentage'] = (overall_stats['present'] / overall_stats['total']) * 100
                overall_stats['absent_percentage'] = (overall_stats['absent'] / overall_stats['total']) * 100
                overall_stats['late_percentage'] = (overall_stats['late'] / overall_stats['total']) * 100
            else:
                overall_stats['present_percentage'] = 0
                overall_stats['absent_percentage'] = 0
                overall_stats['late_percentage'] = 0
            
            # Get attendance by date
            attendance_by_date = query.values('date').annotate(
                total=Count('id'),
                present=Count(Case(When(status='present', then=1), output_field=IntegerField())),
                absent=Count(Case(When(status='absent', then=1), output_field=IntegerField())),
                late=Count(Case(When(status='late', then=1), output_field=IntegerField()))
            ).order_by('date')
            
            # Get attendance by course (if not filtered by course)
            attendance_by_course = []
            if not course_id:
                attendance_by_course = query.values('course__code', 'course__name').annotate(
                    total=Count('id'),
                    present=Count(Case(When(status='present', then=1), output_field=IntegerField())),
                    absent=Count(Case(When(status='absent', then=1), output_field=IntegerField())),
                    late=Count(Case(When(status='late', then=1), output_field=IntegerField()))
                ).order_by('course__code')
            
            # Get attendance by student (if not filtered by student)
            attendance_by_student = []
            if not student_id and (request.user.role == 'faculty' or request.user.role == 'admin'):
                attendance_by_student = query.values(
                    'student__user__first_name', 
                    'student__user__last_name', 
                    'student__enrollment_number'
                ).annotate(
                    total=Count('id'),
                    present=Count(Case(When(status='present', then=1), output_field=IntegerField())),
                    absent=Count(Case(When(status='absent', then=1), output_field=IntegerField())),
                    late=Count(Case(When(status='late', then=1), output_field=IntegerField()))
                ).order_by('student__user__first_name')
            
            # Prepare response
            response_data = {
                'overall': overall_stats,
                'by_date': attendance_by_date,
                'by_course': attendance_by_course,
                'by_student': attendance_by_student
            }
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def performance_analytics(self, request):
        """Get performance analytics."""
        serializer = PerformanceAnalyticsSerializer(data=request.query_params)
        
        if serializer.is_valid():
            course_id = serializer.validated_data.get('course_id')
            student_id = serializer.validated_data.get('student_id')
            score_type = serializer.validated_data.get('score_type')
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            
            # Check permissions
            if student_id and request.user.role == 'student' and request.user.student_profile.id != student_id:
                return Response(
                    {"detail": "You can only view your own performance analytics."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if course_id and request.user.role == 'faculty':
                # Check if the faculty teaches this course
                if not request.user.faculty_profile.courses.filter(id=course_id).exists():
                    return Response(
                        {"detail": "You can only view performance analytics for courses you teach."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Base query
            query = PerformanceRecord.objects.all()
            
            # Apply filters
            if course_id:
                query = query.filter(course_id=course_id)
            
            if student_id:
                query = query.filter(student_id=student_id)
            
            if score_type:
                query = query.filter(score_type=score_type)
            
            if start_date:
                query = query.filter(date__gte=start_date)
            
            if end_date:
                query = query.filter(date__lte=end_date)
            
            # Calculate overall statistics
            overall_stats = query.aggregate(
                total=Count('id'),
                avg_score=Avg(F('score') / F('max_score') * 100),
                min_score=Avg(F('score') / F('max_score') * 100),
                max_score=Avg(F('score') / F('max_score') * 100)
            )
            
            # Get performance by score type
            performance_by_type = query.values('score_type').annotate(
                total=Count('id'),
                avg_score=Avg(F('score') / F('max_score') * 100)
            ).order_by('score_type')
            
            # Get performance by date
            performance_by_date = query.values('date').annotate(
                total=Count('id'),
                avg_score=Avg(F('score') / F('max_score') * 100)
            ).order_by('date')
            
            # Get performance by course (if not filtered by course)
            performance_by_course = []
            if not course_id:
                performance_by_course = query.values('course__code', 'course__name').annotate(
                    total=Count('id'),
                    avg_score=Avg(F('score') / F('max_score') * 100)
                ).order_by('course__code')
            
            # Get performance by student (if not filtered by student)
            performance_by_student = []
            if not student_id and (request.user.role == 'faculty' or request.user.role == 'admin'):
                performance_by_student = query.values(
                    'student__user__first_name', 
                    'student__user__last_name', 
                    'student__enrollment_number'
                ).annotate(
                    total=Count('id'),
                    avg_score=Avg(F('score') / F('max_score') * 100)
                ).order_by('student__user__first_name')
            
            # Prepare response
            response_data = {
                'overall': overall_stats,
                'by_type': performance_by_type,
                'by_date': performance_by_date,
                'by_course': performance_by_course,
                'by_student': performance_by_student
            }
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def engagement_analytics(self, request):
        """Get engagement analytics."""
        serializer = EngagementAnalyticsSerializer(data=request.query_params)
        
        if serializer.is_valid():
            user_id = serializer.validated_data.get('user_id')
            user_type = serializer.validated_data.get('user_type')
            action = serializer.validated_data.get('action')
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            
            # Check permissions
            if user_id and request.user.id != user_id and request.user.role != 'admin':
                return Response(
                    {"detail": "You can only view your own engagement analytics."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Base query
            query = EngagementRecord.objects.all()
            
            # Apply filters
            if user_id:
                query = query.filter(user_id=user_id)
            
            if user_type:
                query = query.filter(user_type=user_type)
            
            if action:
                query = query.filter(action=action)
            
            if start_date:
                query = query.filter(timestamp__gte=start_date)
            
            if end_date:
                query = query.filter(timestamp__lte=end_date)
            
            # Calculate overall statistics
            overall_stats = {
                'total_records': query.count(),
                'unique_users': query.values('user').distinct().count(),
                'unique_actions': query.values('action').distinct().count()
            }
            
            # Get engagement by action
            engagement_by_action = query.values('action').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Get engagement by user type
            engagement_by_user_type = query.values('user_type').annotate(
                count=Count('id')
            ).order_by('user_type')
            
            # Get engagement by time (hourly)
            engagement_by_hour = query.extra(
                select={'hour': "EXTRACT(hour FROM timestamp)"}
            ).values('hour').annotate(
                count=Count('id')
            ).order_by('hour')
            
            # Get engagement by day of week
            engagement_by_day = query.extra(
                select={'day': "EXTRACT(dow FROM timestamp)"}
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            
            # Get top users by engagement
            top_users = []
            if request.user.role == 'admin':
                top_users = query.values('user__email', 'user_type').annotate(
                    count=Count('id')
                ).order_by('-count')[:10]
            
            # Prepare response
            response_data = {
                'overall': overall_stats,
                'by_action': engagement_by_action,
                'by_user_type': engagement_by_user_type,
                'by_hour': engagement_by_hour,
                'by_day': engagement_by_day,
                'top_users': top_users
            }
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def feedback_analytics(self, request):
        """Get feedback analytics."""
        serializer = FeedbackAnalyticsSerializer(data=request.query_params)
        
        if serializer.is_valid():
            course_id = serializer.validated_data.get('course_id')
            faculty_id = serializer.validated_data.get('faculty_id')
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            
            # Check permissions
            if faculty_id and request.user.role == 'faculty' and request.user.faculty_profile.id != faculty_id:
                return Response(
                    {"detail": "You can only view your own feedback analytics."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Base query
            query = Feedback.objects.all()
            
            # Apply filters
            if course_id:
                query = query.filter(course_id=course_id)
            
            if faculty_id:
                query = query.filter(faculty_id=faculty_id)
            
            if start_date:
                query = query.filter(timestamp__date__gte=start_date)
            
            if end_date:
                query = query.filter(timestamp__date__lte=end_date)
            
            # Calculate overall statistics
            overall_stats = {
                'total_feedback': query.count(),
                'avg_rating': query.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0,
                'pending_count': query.filter(status='pending').count(),
                'responded_count': query.filter(status='responded').count(),
                'resolved_count': query.filter(status='resolved').count()
            }
            
            # Get feedback by sentiment
            feedback_by_sentiment = query.values('sentiment').annotate(
                count=Count('id')
            ).order_by('sentiment')
            
            # Get feedback by course
            feedback_by_course = []
            if not course_id:
                feedback_by_course = query.values('course__code', 'course__name').annotate(
                    count=Count('id'),
                    avg_rating=Avg('rating')
                ).order_by('course__code')
            
            # Get feedback by faculty
            feedback_by_faculty = []
            if not faculty_id and request.user.role == 'admin':
                feedback_by_faculty = query.values(
                    'faculty__user__first_name', 
                    'faculty__user__last_name'
                ).annotate(
                    count=Count('id'),
                    avg_rating=Avg('rating')
                ).order_by('faculty__user__first_name')
            
            # Get feedback by status
            feedback_by_status = query.values('status').annotate(
                count=Count('id')
            ).order_by('status')
            
            # Get feedback by rating
            feedback_by_rating = query.values('rating').annotate(
                count=Count('id')
            ).order_by('rating')
            
            # Prepare response
            response_data = {
                'overall': overall_stats,
                'by_sentiment': feedback_by_sentiment,
                'by_course': feedback_by_course,
                'by_faculty': feedback_by_faculty,
                'by_status': feedback_by_status,
                'by_rating': feedback_by_rating
            }
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard analytics for the current user."""
        user = request.user
        
        if user.role == 'student':
            # Student dashboard
            student = user.student_profile
            
            # Get attendance data
            attendance_records = AttendanceRecord.objects.filter(student=student)
            total_attendance = attendance_records.count()
            present_count = attendance_records.filter(status__in=['present', 'late']).count()
            attendance_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0
            
            # Get performance data
            performance_records = PerformanceRecord.objects.filter(student=student)
            avg_performance = performance_records.aggregate(
                avg=Avg(F('score') / F('max_score') * 100)
            )['avg'] or 0
            
            # Get course data
            courses = student.courses.all()
            course_data = []
            
            for course in courses:
                course_attendance = AttendanceRecord.objects.filter(student=student, course=course)
                course_attendance_total = course_attendance.count()
                course_attendance_present = course_attendance.filter(status__in=['present', 'late']).count()
                course_attendance_percentage = (course_attendance_present / course_attendance_total * 100) if course_attendance_total > 0 else 0
                
                course_performance = PerformanceRecord.objects.filter(student=student, course=course)
                course_avg_performance = course_performance.aggregate(
                    avg=Avg(F('score') / F('max_score') * 100)
                )['avg'] or 0
                
                course_data.append({
                    'id': course.id,
                    'code': course.code,
                    'name': course.name,
                    'attendance_percentage': course_attendance_percentage,
                    'performance_percentage': course_avg_performance
                })
            
            # Get recent activities
            recent_activities = EngagementRecord.objects.filter(user=user).order_by('-timestamp')[:5]
            activities = []
            
            for activity in recent_activities:
                activities.append({
                    'action': activity.action,
                    'resource': activity.resource,
                    'timestamp': activity.timestamp
                })
            
            # Prepare response
            response_data = {
                'attendance': {
                    'percentage': attendance_percentage,
                    'total_classes': total_attendance,
                    'present': present_count,
                    'absent': total_attendance - present_count
                },
                'performance': {
                    'average': avg_performance
                },
                'courses': course_data,
                'recent_activities': activities
            }
            
            return Response(response_data)
        
        elif user.role == 'faculty':
            # Faculty dashboard
            faculty = user.faculty_profile
            
            # Get courses taught by faculty
            courses = faculty.courses.all()
            course_data = []
            
            for course in courses:
                course_attendance = AttendanceRecord.objects.filter(course=course)
                course_attendance_total = course_attendance.count()
                course_attendance_present = course_attendance.filter(status__in=['present', 'late']).count()
                course_attendance_percentage = (course_attendance_present / course_attendance_total * 100) if course_attendance_total > 0 else 0
                
                course_students = course.students.count()
                
                course_feedback = Feedback.objects.filter(course=course, faculty=faculty)
                course_feedback_count = course_feedback.count()
                course_avg_rating = course_feedback.aggregate(avg=Avg('rating'))['avg'] or 0
                
                course_data.append({
                    'id': course.id,
                    'code': course.code,
                    'name': course.name,
                    'students': course_students,
                    'attendance_percentage': course_attendance_percentage,
                    'feedback_count': course_feedback_count,
                    'avg_rating': course_avg_rating
                })
            
            # Get pending feedback
            pending_feedback = Feedback.objects.filter(faculty=faculty, status='pending').count()
            
            # Get recent activities
            recent_activities = EngagementRecord.objects.filter(user=user).order_by('-timestamp')[:5]
            activities = []
            
            for activity in recent_activities:
                activities.append({
                    'action': activity.action,
                    'resource': activity.resource,
                    'timestamp': activity.timestamp
                })
            
            # Prepare response
            response_data = {
                'courses': course_data,
                'pending_feedback': pending_feedback,
                'recent_activities': activities
            }
            
            return Response(response_data)
        
        else:  # Admin dashboard
            # Get system-wide statistics
            total_students = Student.objects.count()
            total_faculty = faculty = user.faculty_profile.objects.count()
            total_courses = Course.objects.count()
            
            # Get attendance statistics
            attendance_records = AttendanceRecord.objects.all()
            total_attendance = attendance_records.count()
            present_count = attendance_records.filter(status__in=['present', 'late']).count()
            attendance_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0
            
            # Get feedback statistics
            feedback = Feedback.objects.all()
            total_feedback = feedback.count()
            avg_rating = feedback.aggregate(avg=Avg('rating'))['avg'] or 0
            
            # Get engagement statistics
            engagement = EngagementRecord.objects.all()
            total_engagement = engagement.count()
            
            # Get recent activities
            recent_activities = EngagementRecord.objects.order_by('-timestamp')[:10]
            activities = []
            
            for activity in recent_activities:
                activities.append({
                    'user_type': activity.user_type,
                    'action': activity.action,
                    'resource': activity.resource,
                    'timestamp': activity.timestamp
                })
            
            # Prepare response
            response_data = {
                'users': {
                    'students': total_students,
                    'faculty': total_faculty
                },
                'courses': total_courses,
                'attendance': {
                    'percentage': attendance_percentage,
                    'total': total_attendance
                },
                'feedback': {
                    'total': total_feedback,
                    'avg_rating': avg_rating
                },
                'engagement': {
                    'total': total_engagement
                },
                'recent_activities': activities
            }
            
            return Response(response_data)
