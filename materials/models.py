from django.db import models
from academics.models import Course, Module, Topic
from users.models import Faculty

class Material(models.Model):
    """Study material model."""
    
    FILE_TYPE_CHOICES = (
        ('pdf', 'PDF Document'),
        ('video', 'Video Lecture'),
        ('image', 'Image'),
        ('document', 'Document'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='materials/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='materials', null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='materials', null=True, blank=True)
    uploaded_by = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='uploaded_materials')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    version = models.PositiveSmallIntegerField(default=1)
    keywords = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_file_type_display()})"

class MaterialVersion(models.Model):
    """Material version history model."""
    
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='versions')
    file = models.FileField(upload_to='materials/versions/')
    version = models.PositiveSmallIntegerField()
    uploaded_by = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='uploaded_versions')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('material', 'version')
        ordering = ['-version']
    
    def __str__(self):
        return f"{self.material.title} - v{self.version}"
