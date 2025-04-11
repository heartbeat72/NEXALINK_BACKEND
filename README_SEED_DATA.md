# Seed Data for Academic Management System

This document provides instructions on how to populate the database with test data for the Academic Management System.

## Prerequisites

1. Make sure you have all the required dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure your Django project is properly configured and the database is set up.

## Available Test Accounts

After running the seed script, you can use the following test accounts:

### Admin
- Email: `admin@example.com`
- Password: `adminpass`

### Faculty
- Email: `[first_name].[last_name]@university.edu` (e.g., `john.doe@university.edu`)
- Password: `facultypass`

### Students
- Email: `[first_name].[last_name]@student.university.edu` (e.g., `jane.smith@student.university.edu`)
- Password: `studentpass`

## Running the Seed Script

1. Navigate to the backend directory:
   ```bash
   cd back_end
   ```

2. Run the seed script:
   ```bash
   python seed_data.py
   ```

The script will:
- Create 5 departments (CS, EE, ME, CE, IT)
- Create 1 admin user
- Create 5 faculty members
- Create 50 students
- Create courses for each department
- Create modules and topics for each course
- Enroll students in random courses

## Data Structure

### Departments
- Computer Science (CS)
- Electrical Engineering (EE)
- Mechanical Engineering (ME)
- Civil Engineering (CE)
- Information Technology (IT)

### Courses
Each department has 8 courses (101-402) with:
- 5 modules per course
- 3 topics per module

### Student Data
- Randomly assigned to departments
- Random CGPA between 6.0 and 9.5
- Random semester (1-8)
- Random batch (2020-2023)
- Enrolled in 5 random courses

### Faculty Data
- Randomly assigned to departments
- Random designation (Professor, Associate Professor, etc.)
- Random specialization
- Assigned to teach multiple courses

## Notes

- The seed script uses the Faker library to generate realistic data.
- All passwords are hashed using Django's built-in password hashing.
- The script is idempotent - running it multiple times will not create duplicate data.
- This is strictly for development and testing purposes.

## Troubleshooting

If you encounter any issues:

1. Make sure all migrations are applied:
   ```bash
   python manage.py migrate
   ```

2. Check if the database is properly configured in your settings.

3. Ensure you have the required permissions to create database records.

4. If you need to start fresh, you can:
   - Delete the database and recreate it
   - Run migrations again
   - Run the seed script 
