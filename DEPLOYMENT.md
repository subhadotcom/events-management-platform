# 🚀 Deployment Guide - Events Platform

This guide covers deploying the Events Platform to production environments.

## 📋 Pre-Deployment Checklist

- [ ] All tests passing (`pytest`)
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Static files collected
- [ ] Secret key generated
- [ ] Email service configured
- [ ] Redis instance available (for Celery)
- [ ] SSL certificate ready

## 🔐 Security Checklist

### 1. Update Django Settings

```python
# In .env for production
DEBUG=False
SECRET_KEY=<use-a-strong-random-key-min-50-characters>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
```

### 2. Generate Secret Key

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 3. Database Security

- Use strong passwords
- Enable SSL connections
- Regular backups
- Restrict network access

### 4. Enable Security Headers

Already configured in `settings.py` when `DEBUG=False`:
- HTTPS redirect
- Secure cookies
- XSS protection
- Content type sniffing protection

## 🌐 Deployment Options

### Option 1: Render.com (Recommended for Quick Deploy)

**Why Render?**
- Free tier available
- Built-in PostgreSQL
- Auto SSL certificates
- Easy Redis add-on
- Git-based deployment

**Steps:**

1. **Create `render.yaml`** (already configured in project)

2. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/events-platform.git
git push -u origin main
```

3. **Deploy on Render**
   - Go to https://render.com
   - New → Blueprint
   - Connect GitHub repo
   - Render will auto-detect `render.yaml`
   - Add environment variables
   - Deploy!

4. **Run migrations**
```bash
# In Render shell
python manage.py migrate
python manage.py createsuperuser
python setup_tasks.py
```

### Option 2: Railway.app

**Steps:**

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login and Deploy**
```bash
railway login
railway init
railway add  # Add PostgreSQL and Redis
railway up
```

3. **Set Environment Variables**
- Go to Railway dashboard
- Add all variables from `.env.example`

4. **Run Migrations**
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python setup_tasks.py
```

### Option 3: Docker + DigitalOcean/AWS

**Steps:**

1. **Build Production Image**
```bash
docker build -t events-platform:latest .
```

2. **Push to Registry**
```bash
docker tag events-platform:latest your-registry/events-platform:latest
docker push your-registry/events-platform:latest
```

3. **Deploy to Server**
```bash
# On your server
docker-compose -f docker-compose.prod.yml up -d
```

4. **Setup Database**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python setup_tasks.py
```

### Option 4: Heroku

**Steps:**

1. **Create Heroku App**
```bash
heroku create events-platform-api
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
```

2. **Set Environment Variables**
```bash
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=events-platform-api.herokuapp.com
# ... other variables
```

3. **Create `Procfile`** (already in project):
```
web: gunicorn events_platform.wsgi:application
worker: celery -A events_platform worker -l info
beat: celery -A events_platform beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

4. **Deploy**
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku run python setup_tasks.py
```

5. **Scale Workers**
```bash
heroku ps:scale web=1 worker=1 beat=1
```

## 📧 Email Service Configuration

### Option 1: Gmail (Development/Small Scale)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
```

**Get App Password:**
1. Enable 2FA on Gmail
2. Go to Google Account → Security → App Passwords
3. Generate password for "Mail"

### Option 2: SendGrid (Production)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

### Option 3: AWS SES (Scalable)

```bash
pip install django-ses
```

```python
# In settings.py
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
```

## 🔄 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: pytest
        
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

## 📊 Monitoring & Logging

### 1. Error Tracking - Sentry

```bash
pip install sentry-sdk
```

```python
# In settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    environment="production",
)
```

### 2. Application Monitoring - New Relic

```bash
pip install newrelic
```

### 3. Logging

Already configured in Django settings. For production, use:
- **Papertrail** - Log aggregation
- **CloudWatch** - AWS logging
- **Datadog** - Full monitoring

## 🔍 Health Checks

API includes health check endpoint:
```
GET /api/health/
```

Returns:
```json
{
  "status": "healthy",
  "service": "events-platform"
}
```

## 🚀 Performance Optimization

### 1. Database Indexes
Already configured in models. Review with:
```bash
python manage.py sqlmigrate events 0001
python manage.py sqlmigrate accounts 0001
```

### 2. Redis Caching

```python
# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}
```

### 3. Database Connection Pooling

```bash
pip install psycopg2-pool
```

### 4. Static Files CDN

Use **CloudFlare** or **AWS CloudFront** for static files.

## 📈 Scaling Strategy

### Horizontal Scaling
- Load balancer (Nginx/AWS ALB)
- Multiple web instances
- Multiple Celery workers

### Vertical Scaling
- Increase server resources
- Database read replicas

### Database Optimization
- Connection pooling
- Query optimization
- Indexes on frequently queried fields (already added)

## 🔒 Backup Strategy

### Database Backups
```bash
# PostgreSQL backup
pg_dump -h localhost -U events_user events_db > backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U events_user events_db < backup_20260120.sql
```

### Automated Backups
- **Render**: Automatic PostgreSQL backups
- **AWS RDS**: Automated snapshots
- **Heroku**: Use PG Backups add-on

## 🌐 Domain & SSL

### 1. Purchase Domain
- Namecheap
- Google Domains
- GoDaddy

### 2. Configure DNS
```
A     @       your-server-ip
A     www     your-server-ip
A     api     your-server-ip
```

### 3. SSL Certificate

**Option A: Let's Encrypt (Free)**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Option B: CloudFlare (Free + CDN)**
- Add domain to CloudFlare
- Enable Flexible SSL
- Auto HTTPS rewrites

## 📞 Support & Maintenance

### Regular Tasks
- [ ] Monitor error rates (Sentry)
- [ ] Check Celery queue length
- [ ] Database performance
- [ ] Security updates
- [ ] Backup verification

### Updating Dependencies
```bash
pip list --outdated
pip install -U package-name
python manage.py test  # Verify nothing broke
```

## 🎯 Post-Deployment

1. **Test all endpoints** with Postman collection
2. **Verify email delivery**
3. **Check Celery tasks** are running
4. **Monitor logs** for errors
5. **Load testing** with tools like Locust or Apache Bench
6. **Setup monitoring** dashboards

---

## 📝 Environment Variables Reference

```env
# Django Core
DEBUG=False
SECRET_KEY=<50+ character random string>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=events_db
DB_USER=events_user
DB_PASSWORD=<strong-password>
DB_HOST=<database-host>
DB_PORT=5432

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=<smtp-host>
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<password>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Celery
CELERY_BROKER_URL=redis://<redis-host>:6379/0
CELERY_RESULT_BACKEND=redis://<redis-host>:6379/0

# CORS (if using frontend)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

**Ready to deploy! 🚀**

Need help? Check:
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Local development
- Django Deployment Checklist: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
