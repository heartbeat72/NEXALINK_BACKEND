from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, CustomTokenObtainPairView, UserPreferenceViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')  # optional: use 'users' instead of ''
router.register(r'preferences', UserPreferenceViewSet, basename='user-preference')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # fixed
]
