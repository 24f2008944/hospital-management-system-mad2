# Hospital Management System

This project is a full-stack hospital management system with a Flask backend and Vue.js frontend.

## Features
- Patient, doctor, and admin dashboards
- Appointment booking and management
- Email notifications (MailHog)
- Scheduled tasks (Celery worker & beat)

## How to Run
1. **Backend**: `python backend/app.py`
2. **Celery Worker**: `celery -A tasks.celery worker --loglevel=info` (from backend folder)
3. **Celery Beat**: `celery -A tasks.celery beat --loglevel=info` (from backend folder)
4. **MailHog**: `./mailhog.exe` (from backend folder)
5. **Frontend**: `npm install && npm run serve` (from frontend folder)

## Folder Structure
- `backend/` - Flask API, Celery tasks, database
- `frontend/` - Vue.js SPA

## Requirements
- Python 3.12+
- Node.js & npm
- Redis (for Celery)

---
For more details, see the code and comments in each folder.


celery -A celery_app call tasks.send_all_doctors_monthly_reports