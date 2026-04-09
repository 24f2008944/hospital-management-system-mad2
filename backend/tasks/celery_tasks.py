from celery import Celery
from celery.schedules import crontab
import csv
import os
from datetime import date, datetime, timedelta

celery_app = Celery('hms_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

celery_app.conf.beat_schedule = {
    'daily-appointment-reminders': {
        'task': 'backend.tasks.celery_tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    'monthly-doctor-report': {
        'task': 'backend.tasks.celery_tasks.send_monthly_reports',
        'schedule': crontab(day_of_month=1, hour=7, minute=0),
    },
}

def get_app():
    from backend.app import create_app
    return create_app()

@celery_app.task(bind=True)
def send_daily_reminders(self):
    app = get_app()
    with app.app_context():
        from backend.models.user import Appointment
        from flask_mail import Message
        from backend.app import mail

        today = date.today()
        appointments = Appointment.query.filter_by(date=today, status='Booked').all()

        for apt in appointments:
            try:
                patient_email = apt.patient.user.email if apt.patient and apt.patient.user else None
                if not patient_email:
                    continue
                msg = Message(
                    subject='Appointment Reminder - HealthCare HMS',
                    recipients=[patient_email],
                    html=f"""
                    <h2>Appointment Reminder</h2>
                    <p>Dear {apt.patient.user.full_name},</p>
                    <p>You have an appointment scheduled for today at <strong>{apt.time}</strong> 
                    with <strong>Dr. {apt.doctor.user.full_name}</strong> 
                    ({apt.doctor.specialization}).</p>
                    <p>Please arrive 10 minutes early.</p>
                    <br><p>HealthCare HMS</p>
                    """
                )
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send reminder for apt {apt.id}: {e}")

    return f"Reminders sent for {date.today()}"

@celery_app.task(bind=True)
def send_monthly_reports(self):
    app = get_app()
    with app.app_context():
        from backend.models.user import DoctorProfile, Appointment
        from flask_mail import Message
        from backend.app import mail

        last_month = date.today().replace(day=1) - timedelta(days=1)
        month_start = last_month.replace(day=1)
        month_end = last_month

        doctors = DoctorProfile.query.all()
        for doctor in doctors:
            try:
                appointments = Appointment.query.filter(
                    Appointment.doctor_id == doctor.id,
                    Appointment.date >= month_start,
                    Appointment.date <= month_end,
                    Appointment.status == 'Completed'
                ).all()

                if not appointments:
                    continue

                rows = ""
                for apt in appointments:
                    t = apt.treatment
                    rows += f"""
                    <tr>
                        <td>{apt.patient.user.full_name if apt.patient and apt.patient.user else 'N/A'}</td>
                        <td>{apt.date}</td>
                        <td>{t.diagnosis if t else 'N/A'}</td>
                        <td>{t.prescription if t else 'N/A'}</td>
                    </tr>"""

                html_report = f"""
                <html><body>
                <h2>Monthly Activity Report - {last_month.strftime('%B %Y')}</h2>
                <p>Doctor: <strong>Dr. {doctor.user.full_name}</strong></p>
                <p>Department: {doctor.department.name if doctor.department else 'N/A'}</p>
                <p>Total Appointments: <strong>{len(appointments)}</strong></p>
                <table border="1" cellpadding="8" cellspacing="0">
                    <thead><tr><th>Patient</th><th>Date</th><th>Diagnosis</th><th>Prescription</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
                </body></html>
                """

                msg = Message(
                    subject=f'Monthly Report - {last_month.strftime("%B %Y")}',
                    recipients=[doctor.user.email],
                    html=html_report
                )
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send report for doctor {doctor.id}: {e}")

    return "Monthly reports sent"

@celery_app.task(bind=True)
def export_patient_csv(self, job_id, user_id):
    app = get_app()
    with app.app_context():
        from backend.models.user import ExportJob, PatientProfile, Appointment
        from backend.app import db

        job = ExportJob.query.get(job_id)
        if not job:
            return

        try:
            job.status = 'processing'
            db.session.commit()

            patient = PatientProfile.query.filter_by(user_id=user_id).first()
            if not patient:
                job.status = 'failed'
                db.session.commit()
                return

            appointments = Appointment.query.filter(
                Appointment.patient_id == patient.id,
                Appointment.status == 'Completed'
            ).order_by(Appointment.date.desc()).all()

            os.makedirs('exports', exist_ok=True)
            filepath = f'exports/patient_{user_id}_treatments_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'

            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Patient ID', 'Patient Name', 'Consulting Doctor', 'Department',
                                 'Appointment Date', 'Appointment Time', 'Diagnosis',
                                 'Treatment/Prescription', 'Notes', 'Next Visit'])
                for apt in appointments:
                    t = apt.treatment
                    writer.writerow([
                        patient.id,
                        patient.user.full_name if patient.user else '',
                        apt.doctor.user.full_name if apt.doctor and apt.doctor.user else '',
                        apt.doctor.department.name if apt.doctor and apt.doctor.department else '',
                        apt.date.isoformat(),
                        apt.time,
                        t.diagnosis if t else '',
                        t.prescription if t else '',
                        t.notes if t else '',
                        t.next_visit.isoformat() if t and t.next_visit else ''
                    ])

            job.status = 'done'
            job.file_path = filepath
            db.session.commit()

        except Exception as e:
            job.status = 'failed'
            db.session.commit()
            raise self.retry(exc=e, countdown=30, max_retries=3)
