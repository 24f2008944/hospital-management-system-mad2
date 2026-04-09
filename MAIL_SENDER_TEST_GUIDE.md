# ✅ Mail Sender Test - Step by Step Guide

## Status Check: Is Mail Sending Working?

### Quick Answer
Your mail sender **WILL NOT WORK** until you set up Gmail credentials.

---

## 📋 What You Need

### 1. Gmail Account with 2-Factor Authentication
- You must have 2FA enabled on your Gmail account
- Go to: https://myaccount.google.com/security
- Enable "2-Step Verification"

### 2. Gmail App Password
- Go to: https://myaccount.google.com/apppasswords
- Select: Mail and macOS (or your OS)
- Click "Generate"
- Copy the 16-character password (with spaces)
- Example: `abcd efgh ijkl mnop`

### 3. Set Environment Variables
```bash
export MAIL_USERNAME="your.email@gmail.com"
export MAIL_PASSWORD="abcd efgh ijkl mnop"
```

---

## 🚀 Test the Mail Sender

### Step 1: Set Your Credentials
```bash
export MAIL_USERNAME="your.gmail@gmail.com"
export MAIL_PASSWORD="xxxx xxxx xxxx xxxx"
```

### Step 2: Run the Test Script
```bash
cd /Users/suvenkumar/Downloads/hms
python test_mail_sender.py
```

### Step 3: Check Results
The script will show:
- ✅ or ❌ for each component
- Details on what's working/broken
- Instructions to fix any issues

---

## 📊 What the Test Checks

| Component | What It Tests | Expected Result |
|-----------|---------------|-----------------|
| Mail Config | Environment variables set | ✅ Both set |
| Flask-Mail | Package installed | ✅ Installed |
| Flask App | App initializes | ✅ App created |
| Redis | Redis running | ✅ Connected |
| Celery Tasks | Tasks load correctly | ✅ All loaded |
| Email Send | Actually sends test email | ✅ Email sent |

---

## 🔧 If Tests Fail

### ❌ "MAIL_USERNAME is NOT set"
**Fix:**
```bash
export MAIL_USERNAME="your.email@gmail.com"
```

### ❌ "MAIL_PASSWORD is NOT set"
**Fix:**
```bash
export MAIL_PASSWORD="xxxx xxxx xxxx xxxx"
```

### ❌ "Flask-Mail is NOT installed"
**Fix:**
```bash
pip install Flask-Mail
```

### ❌ "Redis connection failed"
**Fix:**
```bash
redis-server
```
(Run in a separate terminal)

### ❌ "Failed to send email"
**Troubleshooting:**
1. Verify App Password is correct (16 chars with spaces)
2. Check Gmail has 2FA enabled
3. Try disabling "Less secure app access" (if using regular password)
4. Check Gmail account isn't locked

---

## 📧 Expected Output - Success

```
============================================================
🔍 TESTING MAIL CONFIGURATION
============================================================

1️⃣ Checking Environment Variables:
----------------------------------------
✅ MAIL_USERNAME is set: your.email@gmail.com
✅ MAIL_PASSWORD is set: ****************

2️⃣ Checking Flask-Mail Installation:
----------------------------------------
✅ Flask-Mail is installed

3️⃣ Testing Flask App Creation:
----------------------------------------
✅ Flask app created successfully

   Mail Configuration:
   - MAIL_SERVER: smtp.gmail.com
   - MAIL_PORT: 587
   - MAIL_USE_TLS: True
   - MAIL_USERNAME: your.email@gmail.com
   - MAIL_DEBUG: True

✅ Mail configuration looks good

4️⃣ Testing Redis Connection:
----------------------------------------
✅ Redis is running and accessible
   Response: True

5️⃣ Testing Celery Tasks:
----------------------------------------
✅ Daily Reminders task loaded
✅ Monthly Reports task loaded
✅ CSV Export task loaded
✅ Celery app configured

   Scheduled Tasks:
   - daily-appointment-reminders
     Schedule: <crontab: 8 0 * * * (m/h/d/m/w)>
     Task: backend.tasks.celery_tasks.send_daily_reminders
   - monthly-doctor-report
     Schedule: <crontab: 7 0 1 * * (m/h/d/m/w)>
     Task: backend.tasks.celery_tasks.send_monthly_reports

6️⃣ Testing Email Send:
----------------------------------------
📧 Sending test email to: your.email@gmail.com
✅ Email sent successfully!
   Check your inbox for the test email

============================================================
📋 TEST SUMMARY
============================================================

✅ Passed: 6/6
  ✅ Config
  ✅ Flask Mail
  ✅ App
  ✅ Redis
  ✅ Tasks
  ✅ Email

🎉 ALL TESTS PASSED! Mail sender is working correctly!
```

---

## 🎯 Next Steps After Success

### 1. Check Your Inbox
- You should receive the test email within 30 seconds
- Check spam folder if not in inbox
- Subject: "Test Email - HMS Celery Mail Sender"

### 2. Start Celery Services
```bash
# Terminal 2: Celery Worker
celery -A backend.tasks.celery_tasks worker --loglevel=info

# Terminal 3: Celery Beat
celery -A backend.tasks.celery_tasks beat --loglevel=info
```

### 3. Monitor Logs
Watch for messages like:
```
[INFO] Reminder sent for appointment 5
[INFO] Reminders: 3 sent, 0 failed for 2026-04-09
```

---

## 💾 Save Credentials (Optional but Recommended)

### Option 1: .env File (Recommended for Development)
Create `.env` file in project root:
```bash
# .env
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
```

Install python-dotenv:
```bash
pip install python-dotenv
```

Update `backend/app.py` (at the beginning):
```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file automatically
```

### Option 2: ~/.bashrc (For Your System)
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export MAIL_USERNAME="your.email@gmail.com"
export MAIL_PASSWORD="xxxx xxxx xxxx xxxx"
```

Then reload:
```bash
source ~/.zshrc  # or ~/.bashrc
```

---

## 🔐 Security Note

⚠️ **NEVER commit credentials to Git!**
- Add `.env` to `.gitignore`
- Use environment variables for production
- Consider using AWS Secrets Manager or similar for production

---

## 📞 Common Questions

### Q: How long does the test email take to arrive?
**A:** Usually 30 seconds to 2 minutes. Check spam folder if delayed.

### Q: Can I use my regular Gmail password?
**A:** No, you must use an App Password (16-character code). Regular passwords won't work.

### Q: What if I don't have 2FA enabled?
**A:** App Passwords require 2FA. Enable it first:
1. Go to https://myaccount.google.com/security
2. Find "2-Step Verification"
3. Click "Enable"

### Q: Will my real email address be exposed?
**A:** Yes, the test email is sent to your own Gmail address as a test.

### Q: Can I use a different email service?
**A:** Yes, modify the mail config in `backend/app.py`:
```python
# For Outlook/Office 365
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587

# For SendGrid
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
```

---

## ✅ Checklist Before Testing

- [ ] Gmail 2FA enabled
- [ ] App Password created (16 chars)
- [ ] Copied the full 16-character password including spaces
- [ ] Environment variables exported
- [ ] Redis running: `redis-cli ping` returns `PONG`
- [ ] Python environment configured
- [ ] test_mail_sender.py script exists
- [ ] Ready to run the test!

---

## 🚀 Ready to Test?

Run this command with your credentials set:
```bash
cd /Users/suvenkumar/Downloads/hms
export MAIL_USERNAME="your.email@gmail.com"
export MAIL_PASSWORD="xxxx xxxx xxxx xxxx"
python test_mail_sender.py
```

**Good luck! 🎉**
