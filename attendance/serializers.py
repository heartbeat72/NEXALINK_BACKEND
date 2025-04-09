from rest_framework import serializers
from .models import AttendanceRecord, AttendancePercentage
from academics.serializers import CourseSerializer
from users.serializers import StudentSerializer, FacultySerializer

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    course_details = CourseSerializer(source='course', read_only=True)
    marked_by_details = FacultySerializer(source='marked_by', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = ['id', 'student', 'student_details', 'course', 'course_details', 
                  'date', 'status', 'marked_by', 'marked_by_details', 
                  'marked_at', 'remarks']

class AttendancePercentageSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    course_details = CourseSerializer(source='course', read_only=True)
    
    class Meta:
        model = AttendancePercentage
        fields = ['id', 'student', 'student_details', 'course', 'course_details', 
                  'percentage', 'last_updated']

class BulkAttendanceSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    date = serializers.DateField()
    attendance_data = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            allow_empty=False
        ),
        allow_empty=False
    )
    
    def validate_attendance_data(self, value):
        """
        Check that each attendance record has the required fields.
        """
        for record in value:
            if 'student_id' not in record or 'status' not in record:
                raise serializers.ValidationError("Each attendance record must have student_id and status fields")
            
            if record['status'] not in dict(AttendanceRecord.STATUS_CHOICES).keys():
                raise serializers.ValidationError(f"Invalid status: {record['status']}")
        
        return value

class AttendanceStatisticsSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False)
    student_id = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
