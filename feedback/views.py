from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Feedback, FeedbackReply, FeedbackQuestion, QuestionResponse
from .serializers import (
    FeedbackSerializer, FeedbackCreateSerializer, FeedbackReplySerializer,
    FeedbackReplyCreateSerializer, FeedbackQuestionSerializer, QuestionResponseSerializer
)
from users.permissions import IsAdminUser, IsFacultyUser, IsStudentUser

class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing feedback."""
    queryset = Feedback.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'faculty', 'status', 'sentiment']
    search_fields = ['subject', 'content', 'keywords']
    ordering_fields = ['timestamp', 'rating']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FeedbackCreateSerializer
        return FeedbackSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [IsStudentUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set the student field to the current student user."""
        if self.request.user.role == 'student':
            serializer.save(student=self.request.user.student_profile)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def my_feedback(self, request):
        """Get feedback submitted by the current student."""
        if request.user.role != 'student':
            return Response(
                {"detail": "Only students can access their feedback."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user.student_profile
        feedback = Feedback.objects.filter(student=student)
        
        # Filter by course if provided
        course_id = request.query_params.get('course_id')
        if course_id:
            feedback = feedback.filter(course_id=course_id)
        
        # Filter by status if provided
        status_param = request.query_params.get('status')
        if status_param:
            feedback = feedback.filter(status=status_param)
        
        serializer = self.get_serializer(feedback, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def received_feedback(self, request):
        """Get feedback received by the current faculty."""
        if request.user.role != 'faculty':
            return Response(
                {"detail": "Only faculty can access received feedback."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        faculty = request.user.faculty_profile
        feedback = Feedback.objects.filter(faculty=faculty)
        
        # Filter by course if provided
        course_id = request.query_params.get('course_id')
        if course_id:
            feedback = feedback.filter(course_id=course_id)
        
        # Filter by status if provided
        status_param = request.query_params.get('status')
        if status_param:
            feedback = feedback.filter(status=status_param)
        
        serializer = self.get_serializer(feedback, many=True)
        return Response(serializer.data)

class FeedbackReplyViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing feedback replies."""
    queryset = FeedbackReply.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['feedback', 'author_type']
    ordering_fields = ['timestamp']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FeedbackReplyCreateSerializer
        return FeedbackReplySerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set the author type and ID based on the current user."""
        user = self.request.user
        
        if user.role == 'student':
            author_type = 'student'
            author_id = user.student_profile.id
        elif user.role == 'faculty':
            author_type = 'faculty'
            author_id = user.faculty_profile.id
        else:
            author_type = 'admin'
            author_id = user.admin_profile.id
        
        serializer.save(author_type=author_type, author_id=author_id)

class FeedbackQuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing feedback questions."""
    queryset = FeedbackQuestion.objects.all()
    serializer_class = FeedbackQuestionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'is_active']
    ordering_fields = ['order']
    
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
    def course_questions(self, request):
        """Get feedback questions for a specific course."""
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {"detail": "Course ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        questions = FeedbackQuestion.objects.filter(course_id=course_id, is_active=True)
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)

class QuestionResponseViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing question responses."""
    queryset = QuestionResponse.objects.all()
    serializer_class = QuestionResponseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['feedback', 'question']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsStudentUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
