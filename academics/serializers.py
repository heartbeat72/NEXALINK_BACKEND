from rest_framework import serializers
from .models import Department, Course, Enrollment, Module, Topic, AcademicYear, Semester
from users.serializers import FacultySerializer, StudentSerializer

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'title', 'description', 'content', 'order']

class ModuleSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'topics']

class CourseSerializer(serializers.ModelSerializer):
    faculty_details = FacultySerializer(source='faculty', read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'description', 'department', 'department_name', 
                  'credits', 'faculty', 'faculty_details', 'semester', 'is_active', 
                  'created_at', 'updated_at', 'modules', 'student_count']
    
    def get_student_count(self, obj):
        return obj.students.count()

class EnrollmentSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    course_details = CourseSerializer(source='course', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'student_details', 'course', 'course_details', 
                  'enrollment_date', 'is_active']

class DepartmentSerializer(serializers.ModelSerializer):
    head_details = FacultySerializer(source='head', read_only=True)
    course_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'head', 'head_details', 'course_count']
    
    def get_course_count(self, obj):
        return obj.courses.count()

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'academic_year', 'name', 'start_date', 'end_date', 'is_current']

class AcademicYearSerializer(serializers.ModelSerializer):
    semesters = SemesterSerializer(many=True, read_only=True)
    
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current', 'semesters']
