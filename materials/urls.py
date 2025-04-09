from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, MaterialVersionViewSet

router = DefaultRouter()
router.register(r'', MaterialViewSet)
router.register(r'versions', MaterialVersionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
