# 🚀 Quick Start Guide - Events Platform

Get the Events Platform running in under 5 minutes!

## Step 1: Setup Environment

```bash
# Copy environment file
copy .env.example .env
```

Edit `.env` and update these critical settings:
```env
SECRET_KEY=your-randomly-generated-secret-key-change-this
DEBUG=True

# Database (use your PostgreSQL credentials)
DB_NAME=events_db
DB_USER=events_user
DB_PASSWORD=events_password
DB_HOST=localhost
DB_PORT=5432

# Email (use your SMTP provider)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install packages
pip install -r requirements.txt
```

## Step 3: Setup Database

### Option A: PostgreSQL (Recommended)

```sql
-- Run in PostgreSQL
CREATE DATABASE events_db;
CREATE USER events_user WITH PASSWORD 'events_password';
GRANT ALL PRIVILEGES ON DATABASE events_db TO events_user;
ALTER DATABASE events_db OWNER TO events_user;
```

### Option B: Docker Compose (Easiest!)

```bash
docker-compose up -d db redis
```

## Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## Step 5: Run the Server

```bash
python manage.py runserver
```

🎉 **Server running at:** http://localhost:8000

## Step 6: (Optional) Enable Scheduled Emails

Open 3 terminals:

**Terminal 1 - Django Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A events_platform worker -l info
```

**Terminal 3 - Celery Beat:**
```bash
celery -A events_platform beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Setup Periodic Tasks:**
```bash
python setup_tasks.py
```

## 🧪 Quick Test

### 1. Access API Docs
Visit: http://localhost:8000/api/docs/

### 2. Import Postman Collection
Import `postman_collection.json` into Postman

### 3. Test Flow
1. **Signup** as Seeker (check console/email for OTP)
2. **Verify Email** with OTP
3. **Login** to get JWT tokens
4. **Search Events**
5. **Enroll** in an event

---

## 📊 Admin Panel

Access: http://localhost:8000/admin/
Login with superuser credentials

## 🐳 Docker Quick Start

```bash
# Start all services
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Setup tasks
docker-compose exec web python setup_tasks.py
```

## 🔍 Troubleshooting

### Issue: Database connection error
- Ensure PostgreSQL is running
- Check DB credentials in `.env`

### Issue: OTP not received in email
- Check Django console (OTP printed there in dev mode)
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- Try `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` for testing

### Issue: Permission denied errors
- Verify user role (Seeker vs Facilitator)
- Check JWT token is included in Authorization header

## 📚 Next Steps

1. Read full [README.md](README.md)
2. Explore API at `/api/docs/`
3. Import Postman collection for testing
4. Run tests: `pytest`

**Happy Coding! 🎉**
