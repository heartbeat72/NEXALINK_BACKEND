from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Student, Faculty, Admin, UserPreference

User = get_user_model()

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['theme', 'language', 'notifications_enabled']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['enrollment_number', 'batch', 'department', 'semester', 'cgpa']

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['employee_id', 'department', 'designation', 'specialization']

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['employee_id', 'department']

class UserSerializer(serializers.ModelSerializer):
    student_profile = StudentSerializer(read_only=True)
    faculty_profile = FacultySerializer(read_only=True)
    admin_profile = AdminSerializer(read_only=True)
    preferences = UserPreferenceSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'profile_picture', 
                  'student_profile', 'faculty_profile', 'admin_profile', 'preferences',
                  'is_active', 'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 'role']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # Create user preferences
        UserPreference.objects.create(user=user)
        
        # Create role-specific profile
        if user.role == 'student':
            Student.objects.create(
                user=user,
                enrollment_number=f"S{User.objects.count():05d}",
                batch="2025",
                department="Computer Science",
                semester=1
            )
        elif user.role == 'faculty':
            Faculty.objects.create(
                user=user,
                employee_id=f"F{User.objects.count():05d}",
                department="Computer Science",
                designation="Assistant Professor"
            )
        elif user.role == 'admin':
            Admin.objects.create(
                user=user,
                employee_id=f"A{User.objects.count():05d}",
                department="Administration"
            )
            
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['role'] = user.role
        token['name'] = f"{user.first_name} {user.last_name}"
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra response data
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['role'] = self.user.role
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_picture']
