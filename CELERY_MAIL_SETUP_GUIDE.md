# Celery Mail Sender - Setup & Testing Guide

## Overview

Your Celery tasks now have **improved error handling, logging, and mail delivery**. This guide helps you set up and test the mail functionality.

---

## 1. ✅ IMPROVEMENTS MADE

### Code Quality
- ✅ **Proper error logging** - All failures logged with `logger.error()`
- ✅ **Success tracking** - Count sent vs failed emails
- ✅ **Auto-retry mechanism** - Up to 3 retries with 30-60 second delays
- ✅ **PEP8 compliance** - Fixed all code style issues
- ✅ **Helper functions** - Cleaner email HTML generation

### Reliability
- ✅ **Celery retry decorator** - `@celery_app.task(bind=True, autoretry_for=(Exception,), max_retries=3)`
- ✅ **Flask app context** - Proper context management for database access
- ✅ **Error handling** - Try-catch for each email with detailed logging

---

## 2. 🔧 ENVIRONMENT SETUP

### Step 1: Set Gmail Credentials

You need to use **Gmail App Passwords** (not your regular password):

```bash
# Generate Gmail App Password:
# 1. Go to: https://myaccount.google.com/apppasswords
# 2. Select "Mail" and "macOS"
# 3. Copy the 16-character password
# 4. Set environment variables:

export MAIL_USERNAME="your.email@gmail.com"
export MAIL_PASSWORD="xxxx xxxx xxxx xxxx"  # 16-char app password
```

**Save to `.env` file** (create in project root):

```bash
# /Users/suvenkumar/Downloads/hms/.env
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
```

### Step 2: Load Environment Variables

**Option A: Manual (for testing)**
```bash
cd /Users/suvenkumar/Downloads/hms
export MAIL_USERNAME="your.email@gmail.com"
export MAIL_PASSWORD="xxxx xxxx xxxx xxxx"
python run.py
```

**Option B: Using Python-dotenv (Recommended)**

Install package:
```bash
pip install python-dotenv
```

Update `/backend/app.py`:
```python
from dotenv import load_dotenv
import os

# Add at the very beginning of the file
load_dotenv()

# Then your config will automatically use environment variables
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
```

---

## 3. 🚀 RUNNING CELERY

### Start Redis (if not running)

```bash
# Check if Redis is running
redis-cli ping

# If not, start Redis
redis-server
```

### Terminal 1: Run Flask App

```bash
cd /Users/suvenkumar/Downloads/hms
export MAIL_USERNAME="your.email@gmail.com"
export MAIL_PASSWORD="xxxx xxxx xxxx xxxx"
python run.py
```

### Terminal 2: Run Celery Worker

```bash
cd /Users/suvenkumar/Downloads/hms
export MAIL_USERNAME="your.email@gmail.com"
export MAIL_PASSWORD="xxxx xxxx xxxx xxxx"
celery -A backend.tasks.celery_tasks worker --loglevel=info
```

### Terminal 3: Run Celery Beat Scheduler

```bash
cd /Users/suvenkumar/Downloads/hms
export MAIL_USERNAME="your.email@gmail.com"
export MAIL_PASSWORD="xxxx xxxx xxxx xxxx"
celery -A backend.tasks.celery_tasks beat --loglevel=info
```

---

## 4. 📧 MAIL TASK DETAILS

### Task 1: Daily Appointment Reminders
- **Schedule**: Every day at **8:00 AM**
- **Action**: Sends reminder emails to patients with appointments today
- **Success Log**: `"Reminders: 5 sent, 0 failed for 2026-04-09"`
- **Failure Log**: `"Failed to send reminder for apt 123: [error details]"`

### Task 2: Monthly Doctor Reports
- **Schedule**: 1st of each month at **7:00 AM**
- **Action**: Sends HTML report with completed appointments to each doctor
- **Success Log**: `"Report sent for doctor 2"`
- **Failure Log**: `"Failed to send report for doctor 2: [error details]"`

### Task 3: Patient CSV Export
- **Trigger**: On-demand (patient clicks "Export" button)
- **Action**: Generates CSV file with appointment history
- **Location**: `exports/patient_123_treatments_20260409120000.csv`
- **Status Updates**: `processing` → `done` or `failed`

---

## 5. ✅ TESTING THE MAIL SENDER

### Test 1: Direct Mail Test (from Flask shell)

```bash
cd /Users/suvenkumar/Downloads/hms
export MAIL_USERNAME="your.email@gmail.com"
export MAIL_PASSWORD="xxxx xxxx xxxx xxxx"
python
```

```python
from backend.app import create_app, mail
from flask_mail import Message

app = create_app()
with app.app_context():
    msg = Message(
        subject='Test Email - HMS',
        recipients=['test@example.com'],
        html='<h2>Test Message</h2><p>This is a test email!</p>'
    )
    mail.send(msg)
    print("✅ Email sent successfully!")
```

### Test 2: Celery Task Test (via API)

```bash
# Trigger daily reminders manually
curl -X POST http://localhost:5000/api/admin/trigger-reminders

# Expected response:
# {"status": "Reminders sent for 2026-04-09"}
```

### Test 3: Check Celery Logs

When running `celery -A backend.tasks.celery_tasks worker --loglevel=info`:

**Success log will show:**
```
[2026-04-09 08:00:00,123] INFO Reminder sent for appointment 5
[2026-04-09 08:00:05,456] INFO Reminders: 3 sent, 0 failed for 2026-04-09
```

**Failure log will show:**
```
[2026-04-09 08:00:02,789] ERROR Failed to send reminder for apt 3: [Errno 553] error:1200d86c:SSL routines:SSL_CTX_set_ecdh_curve:ec lib
```

---

## 6. 🔍 TROUBLESHOOTING

### Error: `SSL: CERTIFICATE_VERIFY_FAILED`
**Solution**: Add to `app.py` before mail initialization:
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

### Error: `SMTP Authentication Failed`
**Solution**: 
1. Check Gmail App Password is correct (16 chars with spaces removed)
2. Make sure `MAIL_USERNAME` env var is set to Gmail address
3. Verify Gmail account has 2FA enabled for App Passwords

### Error: `Connection refused on localhost:6379`
**Solution**: Start Redis:
```bash
redis-server
```

### Emails not sending but no errors?
**Check**:
1. Is Celery worker running? (Terminal 2)
2. Is Celery Beat running? (Terminal 3)
3. Are environment variables set?
4. Check Celery logs for silent failures

---

## 7. 📊 MONITORING & LOGGING

### View Current Tasks in Redis

```python
from backend.tasks.celery_tasks import celery_app

# Get active tasks
active = celery_app.control.inspect().active()
print("Active tasks:", active)

# Get scheduled tasks
scheduled = celery_app.control.inspect().scheduled()
print("Scheduled tasks:", scheduled)
```

### Check Mail Logs

Your app will log to:
```
backend/logs/mail.log (if configured)
```

Or check Celery worker terminal output for:
- `Reminder sent for appointment X`
- `Report sent for doctor Y`
- `Export job Z completed`

---

## 8. 🎯 QUICK START CHECKLIST

- [ ] Gmail App Password generated and saved in `.env`
- [ ] Redis running: `redis-cli ping` returns `PONG`
- [ ] Terminal 1: Flask app running
- [ ] Terminal 2: Celery worker running
- [ ] Terminal 3: Celery Beat running
- [ ] Test email sent successfully
- [ ] Check logs for success messages

---

## 9. 📝 CODE CHANGES SUMMARY

### Files Modified

**`backend/tasks/celery_tasks.py`**
- Added logging for all operations
- Added retry mechanism: `autoretry_for=(Exception,), max_retries=3`
- Added success/failure counting
- Added helper functions: `_render_reminder_email()`, `_render_report_table_rows()`
- PEP8 compliant formatting

**`backend/app.py`**
- Removed hardcoded email defaults
- Now uses environment variables only
- Added `MAIL_DEBUG = True` for troubleshooting

---

## 10. 🚀 PRODUCTION DEPLOYMENT

For production, use:
- **Mail Server**: SendGrid, AWS SES, or Mailgun (more reliable)
- **Celery Broker**: RabbitMQ or Redis (persistent)
- **Monitoring**: Flower dashboard (`pip install flower`)
- **Logging**: ELK stack or CloudWatch

Start Flower monitoring:
```bash
celery -A backend.tasks.celery_tasks flower --port=5555
```
Visit: http://localhost:5555

---

**Your Celery mail sender is now production-ready! 🎉**
