#!/usr/bin/env python3
"""
Mail Sender Testing Script for HMS Celery Tasks
Tests if emails are being sent correctly
"""

import os
import sys
from datetime import date

# Add project to path
sys.path.insert(0, '/Users/suvenkumar/Downloads/hms')

def test_mail_configuration():
    """Test if mail configuration is set up correctly"""
    print("\n" + "="*60)
    print("🔍 TESTING MAIL CONFIGURATION")
    print("="*60)
    
    # Check environment variables
    print("\n1️⃣ Checking Environment Variables:")
    print("-" * 40)
    
    mail_username = os.environ.get('MAIL_USERNAME')
    mail_password = os.environ.get('MAIL_PASSWORD')
    
    if mail_username:
        print(f"✅ MAIL_USERNAME is set: {mail_username}")
    else:
        print("❌ MAIL_USERNAME is NOT set")
        print("   Set it with: export MAIL_USERNAME='your@gmail.com'")
    
    if mail_password:
        print(f"✅ MAIL_PASSWORD is set: {'*' * 16}")
    else:
        print("❌ MAIL_PASSWORD is NOT set")
        print("   Set it with: export MAIL_PASSWORD='xxxx xxxx xxxx xxxx'")
    
    if not (mail_username and mail_password):
        print("\n⚠️  ENVIRONMENT VARIABLES NOT SET - Mail won't work!")
        return False
    
    return True


def test_flask_mail_import():
    """Test if Flask-Mail is installed"""
    print("\n2️⃣ Checking Flask-Mail Installation:")
    print("-" * 40)
    
    try:
        from flask_mail import Mail, Message
        print("✅ Flask-Mail is installed")
        return True
    except ImportError as e:
        print(f"❌ Flask-Mail is NOT installed: {e}")
        print("   Install with: pip install Flask-Mail")
        return False


def test_app_creation():
    """Test if Flask app can be created"""
    print("\n3️⃣ Testing Flask App Creation:")
    print("-" * 40)
    
    try:
        from backend.app import create_app, mail
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Check mail config
        print("\n   Mail Configuration:")
        print(f"   - MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"   - MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"   - MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"   - MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"   - MAIL_DEBUG: {app.config.get('MAIL_DEBUG')}")
        
        if not app.config.get('MAIL_USERNAME'):
            print("\n   ❌ MAIL_USERNAME not configured!")
            return False
        
        print("\n✅ Mail configuration looks good")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create Flask app: {e}")
        return False


def test_send_email():
    """Test sending an actual email"""
    print("\n4️⃣ Testing Email Send:")
    print("-" * 40)
    
    try:
        from backend.app import create_app, mail
        from flask_mail import Message
        
        app = create_app()
        
        with app.app_context():
            # Create test email
            test_email = os.environ.get('MAIL_USERNAME')
            
            msg = Message(
                subject='Test Email - HMS Celery Mail Sender',
                recipients=[test_email],
                html="""
                <html>
                <body style="font-family: Arial, sans-serif;">
                <h2>🎉 Test Email Successful!</h2>
                <p>This email was sent by the HMS Celery mail sender.</p>
                <p><strong>Timestamp:</strong> """ + str(date.today()) + """</p>
                <p>If you received this email, the mail sender is working correctly! ✅</p>
                </body>
                </html>
                """
            )
            
            print(f"📧 Sending test email to: {test_email}")
            mail.send(msg)
            print("✅ Email sent successfully!")
            print("   Check your inbox for the test email")
            return True
            
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print(f"   Error details: {type(e).__name__}")
        return False


def test_celery_tasks():
    """Test if Celery tasks can be loaded"""
    print("\n5️⃣ Testing Celery Tasks:")
    print("-" * 40)
    
    try:
        from backend.tasks.celery_tasks import (
            send_daily_reminders,
            send_monthly_reports,
            export_patient_csv,
            celery_app
        )
        
        print("✅ Daily Reminders task loaded")
        print("✅ Monthly Reports task loaded")
        print("✅ CSV Export task loaded")
        print("✅ Celery app configured")
        
        # Check beat schedule
        print("\n   Scheduled Tasks:")
        for task_name, task_config in celery_app.conf.beat_schedule.items():
            print(f"   - {task_name}")
            print(f"     Schedule: {task_config['schedule']}")
            print(f"     Task: {task_config['task']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load Celery tasks: {e}")
        return False


def test_redis_connection():
    """Test if Redis is available"""
    print("\n6️⃣ Testing Redis Connection:")
    print("-" * 40)
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        response = r.ping()
        if response:
            print("✅ Redis is running and accessible")
            print(f"   Response: {response}")
            return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("   Make sure Redis is running: redis-server")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("📊 HMS CELERY MAIL SENDER - DIAGNOSTIC TEST")
    print("="*60)
    
    results = {}
    
    # Run all tests
    results['config'] = test_mail_configuration()
    results['flask_mail'] = test_flask_mail_import()
    results['app'] = test_app_creation()
    results['redis'] = test_redis_connection()
    results['tasks'] = test_celery_tasks()
    results['email'] = test_send_email() if results['config'] and results['app'] else False
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Mail sender is working correctly!")
        return 0
    else:
        print("\n⚠️  Some tests failed. See details above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
