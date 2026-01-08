# Events Platform Backend

A Django-based backend for an events management platform with Seeker and Facilitator roles.

## Features

*   **Auth**: JWT Authentication, Email Signup (No username), OTP Verification.
*   **RBAC**: Role-Based Access Control (Seeker vs Facilitator).
*   **Events**: CRUD for Facilitators, Search/Filter for Seekers.
*   **Enrollments**: Seekers can enroll, view past/upcoming enrollments. Capacity checks.
*   **Scheduled Tasks**: Follow-up and Reminder emails via Celery.

## Setup

### Local Development

1.  **Install Dependencies**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    source venv/bin/activate # Linux/Mac
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file (optional, defaults provided in settings.py):
    ```
    DEBUG=True
    SECRET_KEY=your_secret
    DATABASE_URL=postgres://user:pass@localhost:5432/db_name (Optional, defaults to SQLite)
    CELERY_BROKER_URL=redis://localhost:6379/0
    ```

3.  **Migrations**:
    ```bash
    python manage.py migrate
    ```

4.  **Run Server**:
    ```bash
    python manage.py runserver
    ```

5.  **Run Celery Worker** (for emails):
    ```bash
    celery -A events_platform worker -l info
    ```

### Docker

1.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```
    This starts Django (port 8000), Postgres, Redis, and Celery Worker.

## API Documentation

### Auth
*   `POST /auth/signup/`: {email, password, role} (role: SEEKER or FACILITATOR)
*   `POST /auth/verify-email/`: {email, otp}
*   `POST /auth/login/`: {email, password} -> Returns access/refresh tokens.
*   `POST /auth/refresh/`: {refresh}

### Events
*   `GET /api/events/`: List all events (Searchable).
    *   Params: `q` (title/desc), `location`, `language`, `starts_after`, `starts_before`.
*   `POST /api/events/`: Create event (Facilitator only).
*   `GET /api/events/my_events/`: List my created events (Facilitator only).
*   `POST /api/events/{id}/enroll/`: Enroll in event (Seeker only).

### Enrollments
*   `GET /api/enrollments/upcoming/`: List upcoming enrollments (Seeker only).
*   `GET /api/enrollments/past/`: List past enrollments (Seeker only).

## Design Decisions & Tradeoffs

*   **User Model**: Used Django's default `User` model with a OneToOne `Profile` model to store `role` and verification status. This avoids complex custom user model migration issues while satisfying the requirement.
*   **Username**: Since username is not requested, we auto-generate it from the email or just use email as username in the background.
*   **Database**: Configured for PostgreSQL via `DATABASE_URL` but defaults to SQLite for easy local testing without Docker.
*   **Email**: configured to print to console (`EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`) for development.
