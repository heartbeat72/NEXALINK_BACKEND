from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse  # <-- Add this

# Root welcome view
def index(request):
    return JsonResponse({"message": "Welcome to NexaLink Academic Management System API"})  # <-- Root response

# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="NexaLink Academic API",
        default_version='v1',
        description="API for NexaLink Academic Management System",
        terms_of_service="https://www.nexalink.com/terms/",
        contact=openapi.Contact(email="contact@nexalink.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Root
    path('', index),  # <-- Add this line to avoid 404 at root
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    path('api/v1/users/', include('users.urls')),
    path('api/v1/academics/', include('academics.urls')),
    path('api/v1/attendance/', include('attendance.urls')),
    path('api/v1/materials/', include('materials.urls')),
    path('api/v1/feedback/', include('feedback.urls')),
    path('api/v1/analytics/', include('analytics.urls')),
    path('api/v1/ia-marks/', include('ia_marks.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
