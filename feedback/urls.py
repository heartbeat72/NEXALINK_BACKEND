from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeedbackViewSet, FeedbackReplyViewSet,
    FeedbackQuestionViewSet, QuestionResponseViewSet
)

router = DefaultRouter()
router.register(r'feedbacks', FeedbackViewSet)  # renamed from ''
router.register(r'replies', FeedbackReplyViewSet)
router.register(r'questions', FeedbackQuestionViewSet)
router.register(r'responses', QuestionResponseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
