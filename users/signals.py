from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Student, Faculty, Admin, UserPreference

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a profile for a new user based on their role.
    """
    if created:
        # Create user preferences
        UserPreference.objects.get_or_create(user=instance)
        
        # Create role-specific profile
        if instance.role == 'student':
            Student.objects.get_or_create(
                user=instance,
                defaults={
                    'enrollment_number': f"S{User.objects.count():05d}",
                    'batch': "2025",
                    'department': "Computer Science",
                    'semester': 1
                }
            )
        elif instance.role == 'faculty':
            Faculty.objects.get_or_create(
                user=instance,
                defaults={
                    'employee_id': f"F{User.objects.count():05d}",
                    'department': "Computer Science",
                    'designation': "Assistant Professor"
                }
            )
        elif instance.role == 'admin':
            Admin.objects.get_or_create(
                user=instance,
                defaults={
                    'employee_id': f"A{User.objects.count():05d}",
                    'department': "Administration"
                }
            )
