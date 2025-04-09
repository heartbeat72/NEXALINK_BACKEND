from django.db import models
from academics.models import Course
from users.models import Student, Faculty

class IAComponent(models.Model):
    """Internal Assessment Component model."""
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ia_components')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)
    weightage = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage of total IA
    order = models.PositiveSmallIntegerField()
    
    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')
    
    def __str__(self):
        return f"{self.course.code} - {self.name} ({self.max_marks} marks)"

class IAMark(models.Model):
    """Internal Assessment Mark model."""
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ia_marks')
    component = models.ForeignKey(IAComponent, on_delete=models.CASCADE, related_name='marks')
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True)
    marked_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='marked_ia')
    marked_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'component')
    
    def __str__(self):
        return f"{self.student} - {self.component.name} - {self.marks}/{self.component.max_marks}"

class IATotal(models.Model):
    """Internal Assessment Total model for caching purposes."""
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ia_totals')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ia_totals')
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    out_of = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student} - {self.course.code} - {self.total_marks}/{self.out_of} ({self.percentage}%)"
