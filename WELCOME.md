# 🎉 Events Platform - Django Backend

## Welcome!

You've got a **production-ready** Events Platform backend with authentication, role-based access control, event management, and automated email notifications!

## 🚀 Quick Start (Choose One)

### Option 1: Automated Setup (Easiest!)
```bash
python init_project.py
```
This interactive script will guide you through the entire setup process.

### Option 2: Docker (Fastest!)
```bash
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```
Then visit: http://localhost:8000

### Option 3: Manual Setup
```bash
# 1. Setup environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configure .env
copy .env.example .env
# Edit .env with your settings

# 3. Setup database
python manage.py migrate
python manage.py createsuperuser

# 4. Run server
python manage.py runserver
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[README.md](README.md)** - Complete documentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy to production
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview
- **[CHECKLIST.md](CHECKLIST.md)** - Requirements verification

## 🔗 Important URLs

- **API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs/
- **Health Check**: http://localhost:8000/api/health/

## 📮 Postman Collection

Import `postman_collection.json` into Postman for instant API testing with:
- Pre-configured requests
- Auto token management
- Full workflow examples

## ✨ Key Features

✅ Email-based authentication with OTP verification  
✅ JWT tokens (access + refresh)  
✅ Role-based permissions (Seeker & Facilitator)  
✅ Event management with search & filters  
✅ Enrollment system with capacity checks  
✅ Automated email notifications (Celery)  
✅ Dockerized for easy deployment  
✅ Production-ready with comprehensive docs  

## 🧪 Run Tests

```bash
pytest
pytest --cov=accounts --cov=events
```

## 📦 Tech Stack

- Django 4.2+
- Django REST Framework
- PostgreSQL
- Redis + Celery
- JWT Authentication
- Docker + Docker Compose

## 🎯 API Endpoints Summary

**Auth**: `/auth/signup`, `/auth/login`, `/auth/verify-email`  
**Events**: `/api/events/`, `/api/events/search/`  
**Seeker**: `/api/seeker/enroll`, `/api/seeker/enrollments`  
**Facilitator**: `/api/facilitator/events`

## 💡 Need Help?

1. Check the logs: `python manage.py runserver`
2. Review documentation in the `/docs` files
3. Test with Postman collection
4. Check OTP in console output (development mode)

## 🔒 Default Settings

- **OTP**: Prints to console (check terminal)
- **Database**: PostgreSQL (configure in .env)
- **Email**: Console backend (for development)
- **JWT**: 60min access, 7day refresh

## 🌟 What's Next?

1. ✅ Import Postman collection
2. ✅ Create test users (Seeker + Facilitator)
3. ✅ Create events (as Facilitator)
4. ✅ Search and enroll (as Seeker)
5. ✅ Test email notifications (setup Celery)
6. ✅ Deploy to production (see DEPLOYMENT.md)

---

**Built with ❤️ using Django REST Framework**

Ready to build amazing event experiences! 🎉
