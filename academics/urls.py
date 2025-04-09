from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, CourseViewSet, EnrollmentViewSet,
    ModuleViewSet, TopicViewSet, AcademicYearViewSet, SemesterViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'semesters', SemesterViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
