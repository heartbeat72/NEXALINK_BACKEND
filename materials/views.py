from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Material, MaterialVersion
from .serializers import MaterialSerializer, MaterialVersionSerializer
from users.permissions import IsAdminUser, IsFacultyUser, IsStudentUser

class MaterialViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing study materials."""
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'module', 'topic', 'file_type', 'uploaded_by', 'is_active']
    search_fields = ['title', 'description', 'keywords']
    ordering_fields = ['uploaded_at', 'title']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser | IsFacultyUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set the uploaded_by field to the current faculty user."""
        if self.request.user.role == 'faculty':
            serializer.save(uploaded_by=self.request.user.faculty_profile)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def new_version(self, request, pk=None):
        """Upload a new version of a material."""
        material = self.get_object()
        
        # Check if the user is the faculty who uploaded the material or an admin
        if request.user.role == 'faculty' and request.user.faculty_profile != material.uploaded_by:
            return Response(
                {"detail": "You are not authorized to update this material."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if file is provided
        if 'file' not in request.data:
            return Response(
                {"detail": "File is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a new version
        new_version = material.version + 1
        
        # Save the current version to version history
        MaterialVersion.objects.create(
            material=material,
            file=material.file,
            version=material.version,
            uploaded_by=material.uploaded_by
        )
        
        # Update the material with the new file
        material.file = request.data['file']
        material.version = new_version
        
        if request.user.role == 'faculty':
            material.uploaded_by = request.user.faculty_profile
        
        material.save()
        
        serializer = self.get_serializer(material)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_materials(self, request):
        """Get materials for the current user based on role."""
        user = request.user
        
        if user.role == 'student':
            # Get materials for courses the student is enrolled in
            student = user.student_profile
            courses = student.courses.all()
            materials = Material.objects.filter(course__in=courses, is_active=True)
        elif user.role == 'faculty':
            # Get materials uploaded by the faculty
            faculty = user.faculty_profile
            materials = Material.objects.filter(uploaded_by=faculty)
        else:
            # Admin can see all materials
            materials = Material.objects.all()
        
        # Apply filters
        course_id = request.query_params.get('course_id')
        if course_id:
            materials = materials.filter(course_id=course_id)
        
        module_id = request.query_params.get('module_id')
        if module_id:
            materials = materials.filter(module_id=module_id)
        
        topic_id = request.query_params.get('topic_id')
        if topic_id:
            materials = materials.filter(topic_id=topic_id)
        
        file_type = request.query_params.get('file_type')
        if file_type:
            materials = materials.filter(file_type=file_type)
        
        serializer = self.get_serializer(materials, many=True)
        return Response(serializer.data)

class MaterialVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing material versions."""
    queryset = MaterialVersion.objects.all()
    serializer_class = MaterialVersionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['material', 'version', 'uploaded_by']
    ordering_fields = ['version', 'uploaded_at']
    
    @action(detail=False, methods=['get'])
    def material_history(self, request):
        """Get version history for a specific material."""
        material_id = request.query_params.get('material_id')
        if not material_id:
            return Response(
                {"detail": "Material ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        versions = MaterialVersion.objects.filter(material_id=material_id)
        serializer = self.get_serializer(versions, many=True)
        return Response(serializer.data)
