from rest_framework import serializers
from .models import Feedback, FeedbackReply, FeedbackQuestion, QuestionResponse
from academics.serializers import CourseSerializer
from users.serializers import StudentSerializer, FacultySerializer

class QuestionResponseSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question', read_only=True)
    
    class Meta:
        model = QuestionResponse
        fields = ['id', 'question', 'question_text', 'rating']

class FeedbackQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackQuestion
        fields = ['id', 'course', 'question', 'order', 'is_active']

class FeedbackReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackReply
        fields = ['id', 'feedback', 'content', 'author_type', 'author_id', 'timestamp', 'sentiment']
        read_only_fields = ['timestamp', 'sentiment']

class FeedbackSerializer(serializers.ModelSerializer):
    student_details = StudentSerializer(source='student', read_only=True)
    course_details = CourseSerializer(source='course', read_only=True)
    faculty_details = FacultySerializer(source='faculty', read_only=True)
    replies = FeedbackReplySerializer(many=True, read_only=True)
    question_responses = QuestionResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'student', 'student_details', 'course', 'course_details', 
                  'faculty', 'faculty_details', 'subject', 'content', 'rating', 
                  'timestamp', 'status', 'sentiment', 'keywords', 'replies', 
                  'question_responses']
        read_only_fields = ['timestamp', 'sentiment', 'keywords']

class FeedbackCreateSerializer(serializers.ModelSerializer):
    question_responses = QuestionResponseSerializer(many=True, required=False)
    
    class Meta:
        model = Feedback
        fields = ['student', 'course', 'faculty', 'subject', 'content', 'rating', 'question_responses']
    
    def create(self, validated_data):
        question_responses_data = validated_data.pop('question_responses', [])
        feedback = Feedback.objects.create(**validated_data)
        
        for response_data in question_responses_data:
            QuestionResponse.objects.create(feedback=feedback, **response_data)
        
        return feedback

class FeedbackReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackReply
        fields = ['feedback', 'content', 'author_type', 'author_id']
    
    def create(self, validated_data):
        reply = FeedbackReply.objects.create(**validated_data)
        
        # Update feedback status if it's a faculty reply
        if reply.author_type == 'faculty':
            feedback = reply.feedback
            if feedback.status == 'pending':
                feedback.status = 'responded'
                feedback.save()
        
        return reply
