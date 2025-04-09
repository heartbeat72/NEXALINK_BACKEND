from rest_framework import serializers
from .models import Material, MaterialVersion
from academics.serializers import CourseSerializer, ModuleSerializer, TopicSerializer
from users.serializers import FacultySerializer

class MaterialVersionSerializer(serializers.ModelSerializer):
    uploaded_by_details = FacultySerializer(source='uploaded_by', read_only=True)
    
    class Meta:
        model = MaterialVersion
        fields = ['id', 'version', 'file', 'uploaded_by', 'uploaded_by_details', 'uploaded_at']

class MaterialSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)
    module_details = ModuleSerializer(source='module', read_only=True)
    topic_details = TopicSerializer(source='topic', read_only=True)
    uploaded_by_details = FacultySerializer(source='uploaded_by', read_only=True)
    versions = MaterialVersionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Material
        fields = ['id', 'title', 'description', 'file', 'file_type', 
                  'course', 'course_details', 'module', 'module_details', 
                  'topic', 'topic_details', 'uploaded_by', 'uploaded_by_details', 
                  'uploaded_at', 'version', 'keywords', 'is_active', 'versions']
