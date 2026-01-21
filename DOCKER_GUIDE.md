# 🔧 Docker Troubleshooting Guide

## ✅ Fixed Issues

### Issue 1: `version` attribute is obsolete
**Error**: `the attribute 'version' is obsolete`  
**Fix**: Removed `version: '3.8'` from docker-compose.yml (Docker Compose v2+ doesn't need it)

### Issue 2: Database Connection Error
**Error**: `connection to server at "localhost" failed`  
**Root Cause**: Docker containers were using `.env` file which had `DB_HOST=localhost`. Inside Docker, services communicate using service names, not localhost.  
**Fix**: Added explicit environment variables in docker-compose.yml with `DB_HOST=db` (the database service name)

---

## 🚀 Docker Quick Commands

### Start All Services
```bash
docker-compose up -d
```

### Stop All Services
```bash
docker-compose down
```

### Stop and Remove Volumes (Fresh Start)
```bash
docker-compose down -v
```

### Rebuild and Start
```bash
docker-compose up --build -d
```

### View Running Containers
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs celery

# Follow logs (live)
docker-compose logs -f web
```

### Run Django Commands
```bash
# Migrate database
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Create migrations
docker-compose exec web python manage.py makemigrations

# Django shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web pytest
```

### Access Database
```bash
docker-compose exec db psql -U events_user -d events_db
```

### Access Redis
```bash
docker-compose exec redis redis-cli
```

### Setup Periodic Tasks
```bash
docker-compose exec web python setup_tasks.py
```

---

## 🔍 Common Issues & Solutions

### Issue: Port Already in Use
**Error**: `port is already allocated`

**Solution**:
```bash
# Check what's using the port
netstat -ano | findstr :8000

# Stop the process or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use different host port
```

### Issue: Containers Keep Restarting
**Check logs**:
```bash
docker-compose logs web
```

**Common causes**:
- Database not ready (wait for health check)
- Missing environment variables
- Python errors in code

### Issue: Database Data Lost on Restart
**Cause**: Not using volumes

**Solution**: Already configured in docker-compose.yml:
```yaml
volumes:
  postgres_data:
```

To completely reset:
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### Issue: Code Changes Not Reflected
**For Python code**: Should auto-reload (using `--reload` flag in gunicorn)

**If not working**:
```bash
docker-compose restart web
```

**For dependency changes**:
```bash
docker-compose up --build -d
```

### Issue: Docker Compose Command Not Found
**Windows**: Make sure Docker Desktop is running

**Solution**:
```bash
# Check Docker is running
docker --version
docker-compose --version

# If using Docker Desktop, start it from Start menu
```

---

## 📊 Service URLs (When Running)

- **API**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs/
- **Health Check**: http://localhost:8000/api/health/
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## 🔄 Complete Setup Flow

```bash
# 1. Clean start
docker-compose down -v

# 2. Build and start
docker-compose up --build -d

# 3. Wait for services to be healthy (check logs)
docker-compose logs -f db

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. Create superuser
docker-compose exec web python manage.py createsuperuser

# 6. Setup periodic tasks (for scheduled emails)
docker-compose exec web python setup_tasks.py

# 7. Verify all services running
docker-compose ps

# 8. Test the API
curl http://localhost:8000/api/health/
```

---

## 🧪 Testing in Docker

```bash
# Run all tests
docker-compose exec web pytest

# Run with coverage
docker-compose exec web pytest --cov=accounts --cov=events

# Run specific test file
docker-compose exec web pytest accounts/tests.py
```

---

## 📦 Production Docker Deployment

For production, you'll want to:

1. **Use separate docker-compose.prod.yml**:
```yaml
# docker-compose.prod.yml
services:
  web:
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}  # From .env or secrets
      - DB_HOST=${DB_HOST}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
```

2. **Use managed databases** (not Docker DB):
```yaml
# Remove db service, point to external database
environment:
  - DB_HOST=your-rds-endpoint.amazonaws.com
  - DB_PORT=5432
```

3. **Use environment variables for secrets**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## ⚙️ Environment Variables in Docker

**Development** (current setup):
- Uses environment variables defined directly in `docker-compose.yml`
- Overrides `.env` file settings
- `DB_HOST=db` (Docker service name)
- `CELERY_BROKER_URL=redis://redis:6379/0`

**Local (non-Docker)**:
- Uses `.env` file
- `DB_HOST=localhost`
- `CELERY_BROKER_URL=redis://localhost:6379/0`

---

## 🎯 Quick Verification Checklist

After starting Docker:

- [ ] All containers running: `docker-compose ps`
- [ ] Database healthy: `docker-compose logs db | grep "ready"`
- [ ] Web service responding: `curl http://localhost:8000/api/health/`
- [ ] Migrations applied: `docker-compose exec web python manage.py showmigrations`
- [ ] Celery worker running: `docker-compose logs celery`
- [ ] Redis accessible: `docker-compose exec redis redis-cli ping`

---

## 💡 Tips

1. **Always wait for health checks**: Database and Redis need time to start
2. **Check logs first**: `docker-compose logs <service>`
3. **Restart specific service**: `docker-compose restart web`
4. **Fresh start**: `docker-compose down -v && docker-compose up -d`
5. **Development workflow**: Code changes auto-reload, no rebuild needed

---

## 📞 Still Having Issues?

1. Check `docker-compose logs <service>`
2. Verify all services are "healthy": `docker-compose ps`
3. Ensure Docker Desktop is running (Windows)
4. Check ports aren't in use: `netstat -ano | findstr :8000`
5. Try fresh start: `docker-compose down -v && docker-compose up --build -d`

---

**Docker setup is now working! 🎉**

All services running:
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Django web server (port 8000)
- ✅ Celery worker
- ✅ Celery beat scheduler

Access your API at: http://localhost:8000
