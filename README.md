# NexaLink Academic System - Backend

This is the Django REST Framework backend for the NexaLink Academic System, a comprehensive academic management solution.

## Features

- JWT Authentication and Role-Based Access Control
- Student, Faculty, and Admin user roles
- Academic management (departments, courses, modules, topics)
- Attendance tracking and analytics
- Study materials management
- Feedback system
- Performance analytics
- Internal Assessment (IA) marks management

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL or MongoDB
- Redis (for Celery)

### Installation

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/yourusername/nexalink-backend.git
   cd nexalink-backend
   \`\`\`

2. Create a virtual environment:
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

3. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. Create a `.env` file based on `.env.example`:
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your configuration
   \`\`\`

5. Run migrations:
   \`\`\`bash
   python manage.py migrate
   \`\`\`

6. Create a superuser:
   \`\`\`bash
   python manage.py createsuperuser
   \`\`\`

7. Run the development server:
   \`\`\`bash
   python manage.py runserver
   \`\`\`

### Docker Deployment

1. Build and run with Docker Compose:
   \`\`\`bash
   docker-compose up -d
   \`\`\`

2. Create a superuser:
   \`\`\`bash
   docker-compose exec web python manage.py createsuperuser
   \`\`\`

## API Documentation

API documentation is available at:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## Project Structure

The backend is organized into the following Django apps:

- `users`: User management and authentication
- `academics`: Academic structure management
- `attendance`: Attendance tracking
- `materials`: Study materials management
- `feedback`: Feedback system
- `analytics`: Data analytics
- `ia_marks`: Internal Assessment marks management

## Environment Variables

See `.env.example` for all required environment variables.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
