from django.db import models
from academics.models import Course
from users.models import Student, Faculty

class AttendanceRecord(models.Model):
    """Attendance record model."""
    
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='marked_attendance')
    marked_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('student', 'course', 'date')
        ordering = ['-date', 'student__user__first_name']
    
    def __str__(self):
        return f"{self.student} - {self.course} - {self.date} - {self.status}"

class AttendancePercentage(models.Model):
    """Attendance percentage model for caching purposes."""
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_percentages')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_percentages')
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student} - {self.course} - {self.percentage}%"
