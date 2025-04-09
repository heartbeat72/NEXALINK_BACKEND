from rest_framework import serializers
from .models import IAComponent, IAMark, IATotal
from academics.serializers import CourseSerializer
from users.serializers import StudentSerializer, FacultySerializer

class IAComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IAComponent
        fields = ['id', 'course', 'name', 'description', 'max_marks', 'weightage', 'order']

class IAMarkSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    component_details = serializers.SerializerMethodField()
    marked_by_details = FacultySerializer(source='marked_by', read_only=True)
    
    class Meta:
        model = IAMark
        fields = ['id', 'student', 'student_details', 'component', 'component_details', 
                  'marks', 'remarks', 'marked_by', 'marked_by_details', 'marked_at']
        read_only_fields = ['marked_at']
    
    def get_component_details(self, obj):
        return {
            'id': obj.component.id,
            'name': obj.component.name,
            'max_marks': obj.component.max_marks,
            'weightage': obj.component.weightage,
            'course': {
                'id': obj.component.course.id,
                'code': obj.component.course.code,
                'name': obj.component.course.name
            }
        }

class IATotalSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    course_details = CourseSerializer(source='course', read_only=True)
    
    class Meta:
        model = IATotal
        fields = ['id', 'student', 'student_details', 'course', 'course_details', 
                  'total_marks', 'out_of', 'percentage', 'last_updated']
        read_only_fields = ['last_updated']

class BulkIAMarkSerializer(serializers.Serializer):
    component_id = serializers.IntegerField()
    marks_data = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            allow_empty=False
        ),
        allow_empty=False
    )
    
    def validate_marks_data(self, value):
        """
        Check that each mark record has the required fields.
        """
        for record in value:
            if 'student_id' not in record or 'marks' not in record:
                raise serializers.ValidationError("Each mark record must have student_id and marks fields")
            
            try:
                marks = float(record['marks'])
            except ValueError:
                raise serializers.ValidationError(f"Invalid marks value: {record['marks']}")
        
        return value
