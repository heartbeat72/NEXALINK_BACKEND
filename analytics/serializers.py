from rest_framework import serializers
from .models import EngagementRecord, PerformanceRecord, AnalyticsReport

class EngagementRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngagementRecord
        fields = ['id', 'user', 'user_type', 'action', 'resource', 'timestamp', 'metadata']
        read_only_fields = ['timestamp']

class PerformanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceRecord
        fields = ['id', 'student', 'course', 'score_type', 'score', 'max_score', 'date']

class AnalyticsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsReport
        fields = ['id', 'report_type', 'course', 'student', 'data', 'generated_at']
        read_only_fields = ['generated_at']

class AttendanceAnalyticsSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False)
    student_id = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

class PerformanceAnalyticsSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False)
    student_id = serializers.IntegerField(required=False)
    score_type = serializers.CharField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

class EngagementAnalyticsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)
    user_type = serializers.CharField(required=False)
    action = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)

class FeedbackAnalyticsSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False)
    faculty_id = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
