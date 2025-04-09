from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceRecordViewSet, AttendancePercentageViewSet

router = DefaultRouter()
router.register(r'records', AttendanceRecordViewSet)
router.register(r'percentages', AttendancePercentageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
