# Events Platform - Django Backend

A production-ready Django REST API for managing events with authentication, role-based access control, search, and enrollments.

## 🚀 Features

### ✅ Core Features
- **Authentication System**
  - Email-based signup (no username required)
  - Email OTP verification (6-digit code, 5-min expiry, 3 attempts max)
  - JWT authentication (access & refresh tokens)
  - Login restricted to verified users only

- **Role-Based Access Control (RBAC)**
  - Two roles: **Seeker** and **Facilitator**
  - Role-based permissions on all endpoints
  - Ownership validation for event CRUD operations

- **Event Management**
  - Full CRUD operations for Facilitators
  - Event fields: title, description, language, location, start/end times, capacity
  - Automatic validation (dates, capacity, etc.)
  - Database indexes for optimal search performance

- **Seeker Features**
  - Search events with filters (location, language, date range, text search)
  - Enroll in events (with capacity checks)
  - View past and upcoming enrollments
  - Cancel enrollments

- **Facilitator Features**
  - Create, update, delete own events
  - View all events with enrollment counts and available seats
  - Only event creator can modify/delete their events

### 🎁 Bonus Features
- **Dockerized Setup** - Complete Docker Compose configuration
- **Scheduled Emails** - Celery tasks for automated notifications:
  - Follow-up email 1 hour after enrollment
  - Reminder email 1 hour before event starts
- **API Documentation** - Swagger/OpenAPI docs at `/api/docs/`
- **Production Ready** - Gunicorn, PostgreSQL, Redis, security settings

## 📋 Tech Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Authentication**: djangorestframework-simplejwt
- **Database**: PostgreSQL
- **Task Queue**: Celery + Redis
- **Email**: SMTP (configurable)
- **Documentation**: drf-spectacular (Swagger)
- **Containerization**: Docker + Docker Compose

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (for Celery tasks)
- Docker & Docker Compose (optional)

### Option 1: Local Setup

1. **Clone and navigate to the project**
```bash
cd Events
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
# Copy example env file
copy .env.example .env

# Edit .env with your configuration:
# - Database credentials
# - Email settings (SMTP)
# - JWT token lifetimes
# - OTP settings
```

5. **Setup PostgreSQL database**
```sql
CREATE DATABASE events_db;
CREATE USER events_user WITH PASSWORD 'events_password';
GRANT ALL PRIVILEGES ON DATABASE events_db TO events_user;
```

6. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser** (for Django admin)
```bash
python manage.py createsuperuser
```

8. **Run development server**
```bash
python manage.py runserver
```

Server will be available at: `http://localhost:8000`

9. **Run Celery (for scheduled emails)** - In separate terminals:
```bash
# Terminal 1 - Celery Worker
celery -A events_platform worker -l info

# Terminal 2 - Celery Beat (scheduler)
celery -A events_platform beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Option 2: Docker Setup

1. **Copy environment file**
```bash
copy .env.example .env
```

2. **Build and run containers**
```bash
docker-compose up --build
```

3. **Run migrations** (in a new terminal)
```bash
docker-compose exec web python manage.py migrate
```

4. **Create superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

5. **Setup periodic tasks**
```bash
docker-compose exec web python manage.py shell
```
```python
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

# Create interval - every 5 minutes
schedule, _ = IntervalSchedule.objects.get_or_create(
    every=5,
    period=IntervalSchedule.MINUTES,
)

# Follow-up email task
PeriodicTask.objects.get_or_create(
    interval=schedule,
    name='Send enrollment follow-up emails',
    task='events.tasks.send_enrollment_followup_email',
)

# Reminder email task
PeriodicTask.objects.get_or_create(
    interval=schedule,
    name='Send event reminder emails',
    task='events.tasks.send_event_reminder_email',
)
```

Access the application:
- API: `http://localhost:8000`
- Admin: `http://localhost:8000/admin`
- API Docs: `http://localhost:8000/api/docs/`

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | User signup (email, password, role) | No |
| POST | `/auth/verify-email` | Verify email with OTP | No |
| POST | `/auth/login` | Login (returns JWT tokens) | No |
| POST | `/auth/refresh` | Refresh access token | No |
| POST | `/auth/resend-otp` | Resend OTP | No |
| GET | `/auth/me` | Get current user info | Yes |

### Event Endpoints

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/api/events/` | List all events | Yes | Any |
| POST | `/api/events/` | Create event | Yes | Facilitator |
| GET | `/api/events/{id}/` | Get event details | Yes | Any |
| PUT | `/api/events/{id}/` | Update event | Yes | Facilitator (owner) |
| DELETE | `/api/events/{id}/` | Delete event | Yes | Facilitator (owner) |
| GET | `/api/events/search/` | Search events with filters | Yes | Any |

### Seeker Endpoints

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/api/seeker/enroll` | Enroll in event | Yes | Seeker |
| GET | `/api/seeker/enrollments` | List enrollments | Yes | Seeker |
| POST | `/api/seeker/enrollments/{id}/cancel` | Cancel enrollment | Yes | Seeker |

**Query params for enrollments:**
- `type=upcoming` - Get upcoming enrollments
- `type=past` - Get past enrollments

### Facilitator Endpoints

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/api/facilitator/events` | List own events with stats | Yes | Facilitator |

### Search Filters (GET `/api/events/search/`)

- `location` - Filter by location (case-insensitive)
- `language` - Filter by language (case-insensitive)
- `starts_after` - Events starting after this datetime (ISO format)
- `starts_before` - Events starting before this datetime (ISO format)
- `q` - Search in title and description
- `page` - Page number for pagination
- `page_size` - Results per page

**Example:**
```
GET /api/events/search/?location=Mumbai&language=English&starts_after=2026-01-21T00:00:00Z&page=1
```

## 📝 Request/Response Examples

### 1. Signup
```bash
POST /auth/signup
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role": "Seeker"
}

Response (201):
{
  "detail": "User created successfully. OTP sent to john@example.com",
  "email": "john@example.com"
}
```

### 2. Verify Email
```bash
POST /auth/verify-email
Content-Type: application/json

{
  "email": "john@example.com",
  "otp": "123456"
}

Response (200):
{
  "detail": "Email verified successfully. You can now login.",
  "email": "john@example.com"
}
```

### 3. Login
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "role": "Seeker",
    "email_verified": true,
    "date_joined": "2026-01-20T14:00:00Z"
  }
}
```

### 4. Create Event (Facilitator)
```bash
POST /api/events/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Django Workshop",
  "description": "Learn Django REST Framework",
  "language": "English",
  "location": "Mumbai, India",
  "starts_at": "2026-02-01T10:00:00Z",
  "ends_at": "2026-02-01T18:00:00Z",
  "capacity": 50
}

Response (201):
{
  "id": 1,
  "title": "Django Workshop",
  "description": "Learn Django REST Framework",
  "language": "English",
  "location": "Mumbai, India",
  "starts_at": "2026-02-01T10:00:00Z",
  "ends_at": "2026-02-01T18:00:00Z",
  "capacity": 50,
  "created_by": 2,
  "created_by_email": "facilitator@example.com",
  "total_enrollments": 0,
  "available_seats": 50,
  "is_past": false,
  "is_upcoming": true,
  "created_at": "2026-01-20T14:05:00Z",
  "updated_at": "2026-01-20T14:05:00Z"
}
```

### 5. Enroll in Event (Seeker)
```bash
POST /api/seeker/enroll
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "event_id": 1
}

Response (201):
{
  "id": 1,
  "event": 1,
  "event_title": "Django Workshop",
  "seeker": 1,
  "seeker_email": "john@example.com",
  "status": "enrolled",
  "created_at": "2026-01-20T14:10:00Z",
  "updated_at": "2026-01-20T14:10:00Z"
}
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=accounts --cov=events

# Run specific test file
pytest accounts/tests.py
```

## 🔒 Security Features

- [x] Password validation (Django's built-in validators)
- [x] JWT token authentication
- [x] CSRF protection
- [x] SQL injection prevention (Django ORM)
- [x] XSS protection headers
- [x] HTTPS enforcement in production
- [x] Secure cookie settings
- [x] Rate limiting on OTP verification attempts
- [x] Role-based access control
- [x] Ownership validation

## 📊 Database Schema

### User Profile
- Extends Django's default User model
- Fields: role, email_verified, timestamps

### OTP
- Fields: email, otp_code, attempts, is_used, expires_at
- Indexes: email+created_at, email+otp_code

### Event
- Fields: title, description, language, location, starts_at, ends_at, capacity, created_by
- Indexes: starts_at, language, location, created_by

### Enrollment
- Fields: event, seeker, status, timestamps
- Unique constraint: (event, seeker)
- Indexes: seeker+status, event+status

## 🎯 Design Decisions & Tradeoffs

### 1. **Using Django's Default User Model**
✅ **Decision**: Extended User model with OneToOne UserProfile
- **Pros**: No migration headaches, compatible with all Django/DRF packages
- **Cons**: Username field exists but unused
- **Tradeoff**: Set username=email during signup to satisfy uniqueness

### 2. **OTP Storage**
✅ **Decision**: Database table with expiry and attempt tracking
- **Pros**: Persistent, queryable, audit trail
- **Cons**: More DB writes than Redis cache
- **Trade off**: Acceptable for this use case; could move to Redis for scale

### 3. **Capacity Enforcement**
✅ **Decision**: Database-level unique constraint + application-level checks
- **Pros**: Prevents race conditions
- **Cons**: Requires transaction handling
- **Tradeoff**: Choose data consistency over slight performance cost

### 4. **JWT Tokens**
✅ **Decision**: Short-lived access (60min), long-lived refresh (7 days)
- **Pros**: Stateless auth, scalable
- **Cons**: Cannot revoke tokens easily
- **Tradeoff**: Acceptable for this use case; blacklist available if needed

### 5. **Search Implementation**
✅ **Decision**: Database queries with indexes
- **Pros**: Simple, works well for moderate data
- **Cons**: May slow down with millions of records
- **Tradeoff**: Could add Elasticsearch later if needed

### 6. **Email Scheduling**
✅ **Decision**: Celery Beat with 5-minute intervals
- **Pros**: Reliable, flexible
- **Cons**: Requires Redis infrastructure
- **Tradeoff**: Essential for production-quality notifications

## 🌐 Deployment Guide

### Environment Variables (Production)
```bash
DEBUG=False
SECRET_KEY=<generate-strong-secret-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-provider.com
# ... other settings
```

### Deployment Steps
1. Set all environment variables
2. Run migrations: `python manage.py migrate`
3. Collect static files: `python manage.py collectstatic`
4. Start Gunicorn: `gunicorn events_platform.wsgi:application`
5. Setup Nginx reverse proxy
6. Configure SSL certificate (Let's Encrypt)
7. Start Celery worker and beat

### Recommended Platforms
- **Render** - Easy deployment with PostgreSQL + Redis
- **Railway** - Simple Docker deployment
- **DigitalOcean App Platform** - Managed deployment
- **AWS ECS/EC2** - Full control
- **Heroku** - Quick deployment (add PostgreSQL + Redis add-ons)

## 📦 Postman Collection

Import the Postman collection from `postman_collection.json` for ready-to-use API testing.

## 🤝 Support

For issues or questions:
1. Check API documentation at `/api/docs/`
2. Review error messages (consistent format)
3. Check logs in development
4. Verify environment variables

## 📄 License

MIT License - Feel free to use this project for learning and commercial purposes.

---

**Built with ❤️ using Django REST Framework**
