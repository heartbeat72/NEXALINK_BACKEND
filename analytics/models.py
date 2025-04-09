from django.db import models
from academics.models import Course
from users.models import Student, User

class EngagementRecord(models.Model):
    """Engagement record model for tracking user activity."""
    
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engagement_records')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"

class PerformanceRecord(models.Model):
    """Performance record model for tracking student performance."""
    
    SCORE_TYPE_CHOICES = (
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('exam', 'Exam'),
        ('project', 'Project'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performance_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='performance_records')
    score_type = models.CharField(max_length=20, choices=SCORE_TYPE_CHOICES)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student} - {self.course} - {self.score_type} - {self.score}/{self.max_score}"

class AnalyticsReport(models.Model):
    """Analytics report model for caching aggregated data."""
    
    REPORT_TYPE_CHOICES = (
        ('attendance', 'Attendance'),
        ('performance', 'Performance'),
        ('engagement', 'Engagement'),
        ('feedback', 'Feedback'),
    )
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='analytics_reports', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='analytics_reports', null=True, blank=True)
    data = models.JSONField()
    generated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.report_type} Report - {self.generated_at}"
