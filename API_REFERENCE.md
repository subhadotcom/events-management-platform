# 📡 API Reference - Events Platform

Complete API documentation with request/response examples.

**Base URL**: `http://localhost:8000`  
**Production**: `https://your-domain.com`

---

## 🔐 Authentication Endpoints

Authentication is required for all endpoints except signup, verify-email, login, and health check.

### 1. User Signup

Create a new user account. OTP will be sent to email.

**Endpoint**: `POST /auth/signup`  
**Auth Required**: No  
**Permissions**: None

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "role": "Seeker"
}
```

**Field Descriptions**:
- `email` (string, required): Valid email address
- `password` (string, required): Min 8 characters, mix of letters/numbers
- `role` (string, required): Either "Seeker" or "Facilitator"

**Success Response** (201 Created):
```json
{
  "detail": "User created successfully. OTP sent to user@example.com",
  "email": "user@example.com"
}
```

**Error Responses**:

400 Bad Request - Email already exists:
```json
{
  "detail": "A user with this email already exists.",
  "code": "email_exists"
}
```

400 Bad Request - Weak password:
```json
{
  "detail": "password: This password is too common.",
  "code": "validation_error"
}
```

---

### 2. Verify Email (OTP)

Verify email address with 6-digit OTP.

**Endpoint**: `POST /auth/verify-email`  
**Auth Required**: No  
**Permissions**: None

**Request Body**:
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Field Descriptions**:
- `email` (string, required): Email address
- `otp` (string, required): 6-digit code from email

**Success Response** (200 OK):
```json
{
  "detail": "Email verified successfully. You can now login.",
  "email": "user@example.com"
}
```

**Error Responses**:

400 Bad Request - Invalid OTP:
```json
{
  "detail": "Invalid OTP",
  "code": "otp_verification_failed"
}
```

400 Bad Request - Expired OTP:
```json
{
  "detail": "OTP has expired",
  "code": "otp_verification_failed"
}
```

400 Bad Request - Max attempts:
```json
{
  "detail": "Maximum verification attempts exceeded",
  "code": "otp_verification_failed"
}
```

---

### 3. Login

Authenticate and receive JWT tokens.

**Endpoint**: `POST /auth/login`  
**Auth Required**: No  
**Permissions**: None

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "Seeker",
    "email_verified": true,
    "date_joined": "2026-01-20T14:00:00Z"
  }
}
```

**Error Responses**:

401 Unauthorized - Invalid credentials:
```json
{
  "detail": "Invalid credentials",
  "code": "invalid_credentials"
}
```

403 Forbidden - Email not verified:
```json
{
  "detail": "Email not verified. Please verify your email first.",
  "code": "email_not_verified"
}
```

---

### 4. Refresh Token

Get a new access token using refresh token.

**Endpoint**: `POST /auth/refresh`  
**Auth Required**: No  
**Permissions**: None

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 5. Resend OTP

Request a new OTP if previous one expired.

**Endpoint**: `POST /auth/resend-otp`  
**Auth Required**: No  
**Permissions**: None

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Success Response** (200 OK):
```json
{
  "detail": "OTP sent to user@example.com",
  "email": "user@example.com"
}
```

---

### 6. Get Current User

Get authenticated user details.

**Endpoint**: `GET /auth/me`  
**Auth Required**: Yes  
**Permissions**: Authenticated

**Headers**:
```
Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "Seeker",
  "email_verified": true,
  "date_joined": "2026-01-20T14:00:00Z"
}
```

---

## 🎫 Event Endpoints

### 7. Search Events

Search and filter events with pagination.

**Endpoint**: `GET /api/events/search/`  
**Auth Required**: Yes  
**Permissions**: Authenticated

**Query Parameters**:
- `location` (string, optional): Filter by location (case-insensitive)
- `language` (string, optional): Filter by language (case-insensitive)
- `starts_after` (datetime, optional): Events starting after this time (ISO 8601)
- `starts_before` (datetime, optional): Events starting before this time (ISO 8601)
- `q` (string, optional): Search in title and description
- `page` (integer, optional): Page number (default: 1)

**Example Request**:
```
GET /api/events/search/?location=Mumbai&language=English&starts_after=2026-01-21T00:00:00Z&page=1
```

**Success Response** (200 OK):
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/events/search/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Django Workshop",
      "language": "English",
      "location": "Mumbai, India",
      "starts_at": "2026-02-15T10:00:00Z",
      "ends_at": "2026-02-15T18:00:00Z",
      "capacity": 30,
      "created_by_email": "facilitator@example.com",
      "total_enrollments": 15,
      "available_seats": 15
    }
  ]
}
```

---

### 8. List All Events

Get all events with pagination.

**Endpoint**: `GET /api/events/`  
**Auth Required**: Yes  
**Permissions**: Authenticated

**Query Parameters**:
- `page` (integer, optional): Page number

**Success Response** (200 OK):
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/events/?page=2",
  "previous": null,
  "results": [...]
}
```

---

### 9. Get Event Details

Get detailed information about a specific event.

**Endpoint**: `GET /api/events/{id}/`  
**Auth Required**: Yes  
**Permissions**: Authenticated

**Success Response** (200 OK):
```json
{
  "id": 1,
  "title": "Django Workshop",
  "description": "Learn Django REST Framework from scratch",
  "language": "English",
  "location": "Mumbai, India",
  "starts_at": "2026-02-15T10:00:00Z",
  "ends_at": "2026-02-15T18:00:00Z",
  "capacity": 30,
  "created_by": 2,
  "created_by_email": "facilitator@example.com",
  "total_enrollments": 15,
  "available_seats": 15,
  "is_past": false,
  "is_upcoming": true,
  "created_at": "2026-01-20T14:00:00Z",
  "updated_at": "2026-01-20T14:00:00Z"
}
```

---

### 10. Create Event (Facilitator Only)

Create a new event.

**Endpoint**: `POST /api/events/`  
**Auth Required**: Yes  
**Permissions**: Facilitator

**Request Body**:
```json
{
  "title": "Django REST Framework Masterclass",
  "description": "Deep dive into DRF with hands-on projects",
  "language": "English",
  "location": "Bangalore, India",
  "starts_at": "2026-03-01T09:00:00Z",
  "ends_at": "2026-03-01T17:00:00Z",
  "capacity": 25
}
```

**Field Descriptions**:
- `title` (string, required): Event title
- `description` (string, required): Detailed description
- `language` (string, required): Event language
- `location` (string, required): Event location
- `starts_at` (datetime, required): Start time in ISO 8601 format (UTC)
- `ends_at` (datetime, required): End time in ISO 8601 format (UTC)
- `capacity` (integer, optional): Maximum enrollments

**Success Response** (201 Created):
```json
{
  "id": 5,
  "title": "Django REST Framework Masterclass",
  "description": "Deep dive into DRF with hands-on projects",
  "language": "English",
  "location": "Bangalore, India",
  "starts_at": "2026-03-01T09:00:00Z",
  "ends_at": "2026-03-01T17:00:00Z",
  "capacity": 25,
  "created_by": 2,
  "created_by_email": "facilitator@example.com",
  "total_enrollments": 0,
  "available_seats": 25,
  "is_past": false,
  "is_upcoming": true,
  "created_at": "2026-01-20T15:00:00Z",
  "updated_at": "2026-01-20T15:00:00Z"
}
```

**Error Responses**:

403 Forbidden - Not a facilitator:
```json
{
  "detail": "You do not have permission to perform this action.",
  "code": "permission_denied"
}
```

400 Bad Request - Invalid dates:
```json
{
  "detail": "End time must be after start time",
  "code": "invalid_dates"
}
```

---

### 11. Update Event (Owner Only)

Update an existing event.

**Endpoint**: `PUT /api/events/{id}/`  
**Auth Required**: Yes  
**Permissions**: Facilitator (owner only)

**Request Body**: Same as Create Event

**Success Response** (200 OK): Same structure as Create Event

**Error Responses**:

403 Forbidden - Not the owner:
```json
{
  "detail": "You do not have permission to edit this event",
  "code": "permission_denied"
}
```

---

### 12. Delete Event (Owner Only)

Delete an event.

**Endpoint**: `DELETE /api/events/{id}/`  
**Auth Required**: Yes  
**Permissions**: Facilitator (owner only)

**Success Response** (204 No Content): Empty body

---

## 👤 Seeker Endpoints

### 13. Enroll in Event

Enroll in an event.

**Endpoint**: `POST /api/seeker/enroll`  
**Auth Required**: Yes  
**Permissions**: Seeker

**Request Body**:
```json
{
  "event_id": 1
}
```

**Success Response** (201 Created):
```json
{
  "id": 10,
  "event": 1,
  "event_title": "Django Workshop",
  "event_details": {
    "id": 1,
    "title": "Django Workshop",
    "language": "English",
    "location": "Mumbai, India",
    "starts_at": "2026-02-15T10:00:00Z",
    "ends_at": "2026-02-15T18:00:00Z",
    "capacity": 30,
    "created_by_email": "facilitator@example.com",
    "total_enrollments": 16,
    "available_seats": 14
  },
  "seeker": 1,
  "seeker_email": "seeker@example.com",
  "status": "enrolled",
  "created_at": "2026-01-20T15:30:00Z",
  "updated_at": "2026-01-20T15:30:00Z"
}
```

**Error Responses**:

400 Bad Request - Event full:
```json
{
  "detail": "Event is at full capacity",
  "code": "event_full"
}
```

400 Bad Request - Already enrolled:
```json
{
  "detail": "Already enrolled in this event",
  "code": "already_enrolled"
}
```

400 Bad Request - Past event:
```json
{
  "detail": "Cannot enroll in past events",
  "code": "past_event"
}
```

403 Forbidden - Not a seeker:
```json
{
  "detail": "You do not have permission to perform this action.",
  "code": "permission_denied"
}
```

---

### 14. List My Enrollments

Get all enrollments for the authenticated seeker.

**Endpoint**: `GET /api/seeker/enrollments`  
**Auth Required**: Yes  
**Permissions**: Seeker

**Query Parameters**:
- `type` (string, optional): Filter by type
  - `upcoming`: Only future events
  - `past`: Only past events
  - Omit for all enrollments

**Examples**:
```
GET /api/seeker/enrollments
GET /api/seeker/enrollments?type=upcoming
GET /api/seeker/enrollments?type=past
```

**Success Response** (200 OK):
```json
{
  "count": 5,
  "results": [
    {
      "id": 10,
      "event": 1,
      "event_title": "Django Workshop",
      "event_details": {
        "id": 1,
        "title": "Django Workshop",
        "language": "English",
        "location": "Mumbai, India",
        "starts_at": "2026-02-15T10:00:00Z",
        "ends_at": "2026-02-15T18:00:00Z",
        "capacity": 30,
        "created_by_email": "facilitator@example.com",
        "total_enrollments": 16,
        "available_seats": 14
      },
      "seeker": 1,
      "seeker_email": "seeker@example.com",
      "status": "enrolled",
      "created_at": "2026-01-20T15:30:00Z",
      "updated_at": "2026-01-20T15:30:00Z"
    }
  ]
}
```

---

### 15. Cancel Enrollment

Cancel an enrollment.

**Endpoint**: `POST /api/seeker/enrollments/{enrollment_id}/cancel`  
**Auth Required**: Yes  
**Permissions**: Seeker (owner of enrollment)

**Success Response** (200 OK):
```json
{
  "id": 10,
  "event": 1,
  "event_title": "Django Workshop",
  "event_details": {...},
  "seeker": 1,
  "seeker_email": "seeker@example.com",
  "status": "canceled",
  "created_at": "2026-01-20T15:30:00Z",
  "updated_at": "2026-01-20T16:00:00Z"
}
```

**Error Responses**:

400 Bad Request - Already canceled:
```json
{
  "detail": "Enrollment already canceled",
  "code": "already_canceled"
}
```

404 Not Found:
```json
{
  "detail": "Enrollment not found",
  "code": "enrollment_not_found"
}
```

---

## 🎓 Facilitator Endpoints

### 16. List My Events

Get all events created by the authenticated facilitator with statistics.

**Endpoint**: `GET /api/facilitator/events`  
**Auth Required**: Yes  
**Permissions**: Facilitator

**Success Response** (200 OK):
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "title": "Django Workshop",
      "description": "Learn Django REST Framework",
      "language": "English",
      "location": "Mumbai, India",
      "starts_at": "2026-02-15T10:00:00Z",
      "ends_at": "2026-02-15T18:00:00Z",
      "capacity": 30,
      "total_enrollments": 16,
      "available_seats": 14,
      "created_at": "2026-01-20T14:00:00Z",
      "updated_at": "2026-01-20T14:00:00Z"
    }
  ]
}
```

---

## 🔧 Utility Endpoints

### 17. Health Check

Check if the API is running.

**Endpoint**: `GET /api/health/`  
**Auth Required**: No  
**Permissions**: None

**Success Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "events-platform"
}
```

---

### 18. API Documentation

Interactive Swagger/OpenAPI documentation.

**Endpoint**: `GET /api/docs/`  
**Auth Required**: No  
**Permissions**: None

Opens in browser with interactive API explorer.

---

## 📝 Common Response Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content to return
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## 🔑 Authentication

All protected endpoints require a JWT access token in the Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

Token expires after 60 minutes (configurable). Use refresh token to get a new access token.

---

## 📊 Pagination

All list endpoints support pagination:

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 20, max: 100)

**Response Format**:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/events/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## ⚠️ Error Format

All errors follow this consistent format:

```json
{
  "detail": "Human-readable error message",
  "code": "machine_readable_error_code"
}
```

---

**For complete examples, import the Postman collection: `postman_collection.json`**
