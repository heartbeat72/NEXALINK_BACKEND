from django.urls import path, include
from rest_framework.routers import Default


```python file="analytics/urls.py"
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EngagementRecordViewSet, PerformanceRecordViewSet, AnalyticsReportViewSet

router = DefaultRouter()
router.register(r'engagement', EngagementRecordViewSet)
router.register(r'performance', PerformanceRecordViewSet)
router.register(r'reports', AnalyticsReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
