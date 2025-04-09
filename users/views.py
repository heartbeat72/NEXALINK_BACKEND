from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Student, Faculty, Admin, UserPreference
from .serializers import (
    UserSerializer, UserCreateSerializer, CustomTokenObtainPairSerializer,
    ChangePasswordSerializer, ProfilePictureSerializer, UserPreferenceSerializer
)
from .permissions import IsAdminUser, IsFacultyUser, IsStudentUser, IsOwnerOrAdmin

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that returns user details with tokens."""
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing user instances."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'list':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'upload_profile_picture':
            return ProfilePictureSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's details."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def change_password(self, request, pk=None):
        """Change user password."""
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"status": "password changed successfully"})
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def upload_profile_picture(self, request, pk=None):
        """Upload user profile picture."""
        user = self.get_object()
        serializer = ProfilePictureSerializer(user, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing user preferences."""
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Get the current user's preferences."""
        preference, created = UserPreference.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(preference)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_preferences(self, request):
        """Update the current user's preferences."""
        preference, created = UserPreference.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(preference, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
