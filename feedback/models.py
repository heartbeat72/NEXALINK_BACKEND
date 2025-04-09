from django.db import models
from academics.models import Course
from users.models import Student, Faculty

class Feedback(models.Model):
    """Feedback model."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('responded', 'Responded'),
        ('resolved', 'Resolved'),
    )
    
    SENTIMENT_CHOICES = (
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='feedback')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedback')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='received_feedback')
    subject = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, null=True, blank=True)
    keywords = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Feedback from {self.student} for {self.course}"

class FeedbackReply(models.Model):
    """Feedback reply model."""
    
    AUTHOR_TYPE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    author_type = models.CharField(max_length=10, choices=AUTHOR_TYPE_CHOICES)
    author_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sentiment = models.CharField(max_length=10, choices=Feedback.SENTIMENT_CHOICES, null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Reply to {self.feedback} by {self.author_type}"

class FeedbackQuestion(models.Model):
    """Feedback question model for structured feedback."""
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedback_questions')
    question = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')
    
    def __str__(self):
        return f"Question for {self.course}: {self.question}"

class QuestionResponse(models.Model):
    """Question response model for structured feedback."""
    
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='question_responses')
    question = models.ForeignKey(FeedbackQuestion, on_delete=models.CASCADE, related_name='responses')
    rating = models.PositiveSmallIntegerField()
    
    class Meta:
        unique_together = ('feedback', 'question')
    
    def __str__(self):
        return f"Response to {self.question} in {self.feedback}"
