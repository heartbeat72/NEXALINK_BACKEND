from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Department, Course, Enrollment, Module, Topic, AcademicYear, Semester
from .serializers import (
    DepartmentSerializer, CourseSerializer, EnrollmentSerializer,
    ModuleSerializer, TopicSerializer, AcademicYearSerializer, SemesterSerializer
)
from users.permissions import IsAdminUser, IsFacultyUser, IsStudentUser

class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing department instances."""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'head']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing course instances."""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'department', 'faculty', 'semester', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    
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
    def my_courses(self, request):
        """Get courses for the current user based on role."""
        user = request.user
        
        if user.role == 'student':
            # Get courses for student
            student = user.student_profile
            courses = Course.objects.filter(enrollment__student=student, enrollment__is_active=True)
        elif user.role == 'faculty':
            # Get courses for faculty
            faculty = user.faculty_profile
            courses = Course.objects.filter(faculty=faculty)
        else:
            # Admin can see all courses
            courses = Course.objects.all()
        
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

class EnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing enrollment instances."""
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'is_active']
    ordering_fields = ['enrollment_date']
    
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
    def my_enrollments(self, request):
        """Get enrollments for the current student."""
        if request.user.role != 'student':
            return Response(
                {"detail": "Only students can access their enrollments."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user.student_profile
        enrollments = Enrollment.objects.filter(student=student)
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)

class ModuleViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing module instances."""
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'title']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser | IsFacultyUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class TopicViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing topic instances."""
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['module']
    search_fields = ['title', 'description', 'content']
    ordering_fields = ['order', 'title']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser | IsFacultyUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class AcademicYearViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing academic year instances."""
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_current']
    ordering_fields = ['start_date', 'name']
    
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
    def current(self, request):
        """Get the current academic year."""
        try:
            current_year = AcademicYear.objects.get(is_current=True)
            serializer = self.get_serializer(current_year)
            return Response(serializer.data)
        except AcademicYear.DoesNotExist:
            return Response(
                {"detail": "No current academic year set."},
                status=status.HTTP_404_NOT_FOUND
            )

class SemesterViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing semester instances."""
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['academic_year', 'name', 'is_current']
    ordering_fields = ['start_date', 'name']
    
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
    def current(self, request):
        """Get the current semester."""
        try:
            current_semester = Semester.objects.get(is_current=True)
            serializer = self.get_serializer(current_semester)
            return Response(serializer.data)
        except Semester.DoesNotExist:
            return Response(
                {"detail": "No current semester set."},
                status=status.HTTP_404_NOT_FOUND
            )
