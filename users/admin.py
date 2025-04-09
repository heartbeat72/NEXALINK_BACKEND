from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Student, Faculty, Admin, UserPreference

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Define admin model for custom User model with no username field."""
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'role', 'profile_picture')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'enrollment_number', 'department', 'semester', 'cgpa')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'enrollment_number')
    list_filter = ('department', 'semester', 'batch')

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'designation')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'employee_id')
    list_filter = ('department', 'designation')

@admin.register(Admin)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'employee_id')
    list_filter = ('department',)

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'language', 'notifications_enabled')
    list_filter = ('theme', 'language', 'notifications_enabled')
