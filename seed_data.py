import os
import django
import random
from faker import Faker
from datetime import datetime, timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexalink.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import User, Student, Faculty, Admin, UserPreference
from academics.models import Department, Course, Enrollment, Module, Topic, AcademicYear, Semester

fake = Faker()

def create_departments():
    departments = [
        ('Computer Science', 'CS'),
        ('Electrical Engineering', 'EE'),
        ('Mechanical Engineering', 'ME'),
        ('Civil Engineering', 'CE'),
        ('Information Technology', 'IT'),
    ]
    
    for name, code in departments:
        Department.objects.get_or_create(
            name=name,
            code=code,
            description=fake.text(max_nb_chars=200)
        )
    
    return Department.objects.all()

def create_academic_year():
    current_year = datetime.now().year
    academic_year, _ = AcademicYear.objects.get_or_create(
        name=f"{current_year}-{current_year+1}",
        start_date=datetime(current_year, 8, 1),
        end_date=datetime(current_year+1, 7, 31),
        is_current=True
    )
    return academic_year

def create_semesters(academic_year):
    semesters = [
        ('Fall', datetime(academic_year.start_date.year, 8, 1), datetime(academic_year.start_date.year, 12, 31)),
        ('Spring', datetime(academic_year.start_date.year+1, 1, 1), datetime(academic_year.start_date.year+1, 5, 31)),
        ('Summer', datetime(academic_year.start_date.year+1, 6, 1), datetime(academic_year.start_date.year+1, 7, 31)),
    ]
    
    for name, start_date, end_date in semesters:
        Semester.objects.get_or_create(
            academic_year=academic_year,
            name=name,
            start_date=start_date,
            end_date=end_date,
            is_current=(name == 'Spring')  # Set Spring as current semester
        )
    
    return Semester.objects.all()

def create_admin():
    # Create admin user
    admin_user = User.objects.create_user(
        email='admin@example.com',
        password='adminpass',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    
    # Create admin profile
    Admin.objects.create(
        user=admin_user,
        employee_id='ADM001',
        department='Administration'
    )
    
    # Create admin preferences
    UserPreference.objects.create(
        user=admin_user,
        theme='light',
        language='en',
        notifications_enabled=True
    )
    
    return admin_user

def create_faculty(departments):
    faculty_list = []
    designations = ['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer']
    specializations = [
        'Artificial Intelligence', 'Machine Learning', 'Data Science',
        'Computer Networks', 'Database Systems', 'Software Engineering',
        'Embedded Systems', 'Power Systems', 'Control Systems',
        'Thermodynamics', 'Fluid Mechanics', 'Structural Engineering'
    ]
    
    for i in range(5):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@university.edu"
        
        # Create faculty user
        faculty_user = User.objects.create_user(
            email=email,
            password='facultypass',
            first_name=first_name,
            last_name=last_name,
            role='faculty'
        )
        
        # Create faculty profile
        faculty = Faculty.objects.create(
            user=faculty_user,
            employee_id=f'FAC{str(i+1).zfill(3)}',
            department=random.choice(departments),
            designation=random.choice(designations),
            specialization=random.choice(specializations)
        )
        
        # Create faculty preferences
        UserPreference.objects.create(
            user=faculty_user,
            theme=random.choice(['light', 'dark']),
            language='en',
            notifications_enabled=True
        )
        
        faculty_list.append(faculty)
    
    return faculty_list

def create_students(departments, semesters):
    students = []
    batches = ['2020', '2021', '2022', '2023']
    
    for i in range(50):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@student.university.edu"
        
        # Create student user
        student_user = User.objects.create_user(
            email=email,
            password='studentpass',
            first_name=first_name,
            last_name=last_name,
            role='student'
        )
        
        # Create student profile
        student = Student.objects.create(
            user=student_user,
            enrollment_number=f'EN{str(i+1).zfill(3)}',
            batch=random.choice(batches),
            department=random.choice(departments),
            semester=random.randint(1, 8),
            cgpa=round(random.uniform(6.0, 9.5), 2)
        )
        
        # Create student preferences
        UserPreference.objects.create(
            user=student_user,
            theme=random.choice(['light', 'dark']),
            language='en',
            notifications_enabled=True
        )
        
        students.append(student)
    
    return students

def create_courses(departments, faculty):
    courses = []
    course_codes = {
        'CS': ['CS101', 'CS102', 'CS201', 'CS202', 'CS301', 'CS302', 'CS401', 'CS402'],
        'EE': ['EE101', 'EE102', 'EE201', 'EE202', 'EE301', 'EE302', 'EE401', 'EE402'],
        'ME': ['ME101', 'ME102', 'ME201', 'ME202', 'ME301', 'ME302', 'ME401', 'ME402'],
        'CE': ['CE101', 'CE102', 'CE201', 'CE202', 'CE301', 'CE302', 'CE401', 'CE402'],
        'IT': ['IT101', 'IT102', 'IT201', 'IT202', 'IT301', 'IT302', 'IT401', 'IT402']
    }
    
    for dept in departments:
        for code in course_codes[dept.code]:
            course = Course.objects.create(
                code=code,
                name=f"{dept.name} {code}",
                description=fake.text(max_nb_chars=200),
                department=dept,
                credits=random.randint(3, 4),
                faculty=random.choice(faculty),
                semester=int(code[2]),
                is_active=True
            )
            
            # Create modules for each course
            for i in range(1, 6):
                module = Module.objects.create(
                    course=course,
                    title=f"Module {i}",
                    description=fake.text(max_nb_chars=100),
                    order=i
                )
                
                # Create topics for each module
                for j in range(1, 4):
                    Topic.objects.create(
                        module=module,
                        title=f"Topic {j}",
                        description=fake.text(max_nb_chars=100),
                        content=fake.text(max_nb_chars=500),
                        order=j
                    )
            
            courses.append(course)
    
    return courses

def create_enrollments(students, courses):
    for student in students:
        # Enroll student in 5 random courses
        student_courses = random.sample(courses, 5)
        for course in student_courses:
            Enrollment.objects.create(
                student=student,
                course=course,
                is_active=True
            )

def seed_database():
    print("Starting database seeding...")
    
    # Create departments
    print("Creating departments...")
    departments = create_departments()
    
    # Create academic year and semesters
    print("Creating academic year and semesters...")
    academic_year = create_academic_year()
    semesters = create_semesters(academic_year)
    
    # Create admin
    print("Creating admin...")
    admin = create_admin()
    
    # Create faculty
    print("Creating faculty...")
    faculty = create_faculty(departments)
    
    # Create students
    print("Creating students...")
    students = create_students(departments, semesters)
    
    # Create courses
    print("Creating courses...")
    courses = create_courses(departments, faculty)
    
    # Create enrollments
    print("Creating enrollments...")
    create_enrollments(students, courses)
    
    print("Database seeding completed successfully!")

if _name_ == '_main_':
    seed_database()
