from django.db import models
from users.models import Faculty, Student

class Department(models.Model):
    """Department model."""
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Course(models.Model):
    """Course model."""
    
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    credits = models.PositiveSmallIntegerField()
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='courses')
    students = models.ManyToManyField(Student, through='Enrollment', related_name='courses')
    semester = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code}: {self.name}"

class Enrollment(models.Model):
    """Enrollment model for student-course relationship."""
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student} enrolled in {self.course}"

class Module(models.Model):
    """Module model for course modules."""
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField()
    
    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')
    
    def __str__(self):
        return f"{self.course.code} - Module {self.order}: {self.title}"

class Topic(models.Model):
    """Topic model for module topics."""
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField()
    
    class Meta:
        ordering = ['order']
        unique_together = ('module', 'order')
    
    def __str__(self):
        return f"{self.module.course.code} - {self.module.title} - Topic {self.order}: {self.title}"

class AcademicYear(models.Model):
    """Academic year model."""
    
    name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Semester(models.Model):
    """Semester model."""
    
    SEMESTER_CHOICES = (
        ('Fall', 'Fall'),
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Winter', 'Winter'),
    )
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    name = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('academic_year', 'name')
    
    def __str__(self):
        return f"{self.name} {self.academic_year.name}"
