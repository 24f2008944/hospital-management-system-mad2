# HealthCare HMS - Hospital Management System

A full-stack Hospital Management System built with **Flask**, **Vue.js**, **SQLite**, **Redis**, and **Celery**.

---

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Flask, Flask-JWT-Extended, SQLAlchemy |
| Frontend  | Vue.js 3 (CDN), Vue Router, Bootstrap 5 |
| Database  | SQLite (auto-created on startup)    |
| Cache     | Redis                               |
| Jobs      | Celery + Redis                      |
| Email     | Flask-Mail (SMTP)                   |

---

## Project Structure

```
hms/
├── backend/
│   ├── app.py              # Flask app factory + seeding
│   ├── models/
│   │   └── user.py         # All SQLAlchemy models
│   ├── routes/
│   │   ├── auth.py         # Login / Register
│   │   ├── admin.py        # Admin APIs
│   │   ├── doctor.py       # Doctor APIs
│   │   ├── patient.py      # Patient APIs
│   │   └── appointment.py  # Booking / Slots APIs
│   └── tasks/
│       └── celery_tasks.py # Celery background jobs
├── frontend/
│   ├── index.html          # Single-page entry point
│   └── static/
│       ├── css/style.css   # Custom styles
│       └── js/
│           ├── auth.js     # Login / Register components
│           ├── admin.js    # Admin dashboard components
│           ├── doctor.js   # Doctor dashboard components
│           ├── patient.js  # Patient dashboard components
│           └── app.js      # Vue Router + Root App
├── instance/               # SQLite DB stored here (auto-created)
├── exports/                # CSV exports stored here
├── run.py                  # Entry point
└── requirements.txt
```

---

## Setup & Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install & start Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis
```

**Windows:** Download from https://redis.io/download or use WSL.

### 3. Run the Flask app

```bash
python run.py
```

The app will be available at: **http://localhost:5000**

---

## Default Login Credentials

| Role   | Username | Password  |
|--------|----------|-----------|
| Admin  | admin    | admin123  |

> Doctors are added by the Admin. Patients register themselves.

---

## Running Background Jobs (Optional)

### Start Celery Worker
```bash
celery -A backend.tasks.celery_tasks.celery_app worker --loglevel=info
```

### Start Celery Beat (scheduled jobs)
```bash
celery -A backend.tasks.celery_tasks.celery_app beat --loglevel=info
```

### Scheduled Jobs
- **Daily reminders** — 8:00 AM every day (sends appointment reminders via email)
- **Monthly reports** — 1st of every month at 7:00 AM (sends doctor activity report)

### Configure Email (for reminders & reports)
Set these environment variables before running:
```bash
export MAIL_USERNAME=your@gmail.com
export MAIL_PASSWORD=your_app_password
```

> Use a Gmail App Password (not your regular password). See: https://support.google.com/accounts/answer/185833

---

## Features

### Admin
- Dashboard with stats (doctors, patients, appointments)
- Add / Edit / Deactivate doctors
- View & manage all patients (blacklist/activate)
- View all appointments
- Search doctors by name/specialization, patients by name/email/phone

### Doctor
- Dashboard with today's patients and upcoming appointments
- Mark appointments as completed with diagnosis + prescription
- Cancel appointments
- Set availability for next 7 days
- View patient history

### Patient
- Register and login
- Browse doctors by department/specialization
- View doctor availability (next 7 days) and book appointments
- Reschedule or cancel booked appointments
- View full treatment history with diagnoses and prescriptions
- Export treatment records as CSV (async job)
- Edit personal profile

### Caching
- Admin dashboard and doctor listing are Redis-cached (5 min TTL)
- Cache invalidated on data writes

---

## API Endpoints Summary

### Auth
| Method | Endpoint           | Description       |
|--------|--------------------|-------------------|
| POST   | /api/auth/register | Patient register  |
| POST   | /api/auth/login    | Login (all roles) |
| GET    | /api/auth/me       | Get current user  |

### Admin
| Method | Endpoint                         | Description          |
|--------|----------------------------------|----------------------|
| GET    | /api/admin/dashboard             | Stats                |
| GET/POST | /api/admin/doctors             | List / Add doctors   |
| PUT    | /api/admin/doctors/<id>          | Update doctor        |
| DELETE | /api/admin/doctors/<id>          | Deactivate doctor    |
| GET    | /api/admin/patients              | List patients        |
| POST   | /api/admin/patients/<id>/toggle  | Toggle active status |
| GET    | /api/admin/appointments          | All appointments     |
| GET    | /api/admin/search                | Search               |

### Doctor
| Method | Endpoint                                  | Description        |
|--------|-------------------------------------------|--------------------|
| GET    | /api/doctor/dashboard                     | Dashboard          |
| GET    | /api/doctor/appointments                  | My appointments    |
| POST   | /api/doctor/appointments/<id>/complete    | Complete + treat   |
| POST   | /api/doctor/appointments/<id>/cancel      | Cancel             |
| GET    | /api/doctor/patients                      | My patients        |
| GET    | /api/doctor/patients/<id>/history         | Patient history    |
| GET/POST | /api/doctor/availability               | Get/Set availability |

### Patient
| Method | Endpoint                          | Description          |
|--------|-----------------------------------|----------------------|
| GET    | /api/patient/dashboard            | Dashboard            |
| PUT    | /api/patient/profile              | Update profile       |
| GET    | /api/patient/doctors              | Browse doctors       |
| GET    | /api/patient/appointments/history | All appointments     |
| POST   | /api/patient/export/trigger       | Trigger CSV export   |
| GET    | /api/patient/export/status/<id>   | Check export status  |
| GET    | /api/patient/export/download/<id> | Download CSV         |

### Appointments
| Method | Endpoint                        | Description       |
|--------|---------------------------------|-------------------|
| POST   | /api/appointment/book           | Book appointment  |
| POST   | /api/appointment/<id>/cancel    | Cancel            |
| PUT    | /api/appointment/<id>/reschedule | Reschedule       |
| GET    | /api/appointment/slots          | Get available slots |
