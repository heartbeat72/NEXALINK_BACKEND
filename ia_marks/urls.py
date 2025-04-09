from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IAComponentViewSet, IAMarkViewSet, IATotalViewSet

router = DefaultRouter()
router.register(r'components', IAComponentViewSet)
router.register(r'marks', IAMarkViewSet)
router.register(r'totals', IATotalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
