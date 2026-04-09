from celery import Celery
from celery.schedules import crontab
import csv
import os
import logging
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

celery_app = Celery(
    'hms_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

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


@celery_app.task(bind=True, autoretry_for=(Exception,), max_retries=3)
def send_daily_reminders(self):
    app = get_app()
    with app.app_context():
        from backend.models.user import Appointment
        from backend.app import mail
        from flask_mail import Message

        today = date.today()
        appointments = Appointment.query.filter_by(
            date=today, status='Booked'
        ).all()

        success_count = 0
        fail_count = 0

        for apt in appointments:
            try:
                patient_email = (
                    apt.patient.user.email
                    if apt.patient and apt.patient.user
                    else None
                )
                if not patient_email:
                    logger.warning(
                        f"No email for appointment {apt.id}"
                    )
                    continue

                msg = Message(
                    subject='Appointment Reminder - HealthCare HMS',
                    recipients=[patient_email],
                    html=_render_reminder_email(apt),
                )
                mail.send(msg)
                success_count += 1
                logger.info(
                    f"Reminder sent for appointment {apt.id}"
                )

            except Exception as e:
                fail_count += 1
                logger.error(
                    f"Failed to send reminder for apt {apt.id}: {e}"
                )
                if self.request.retries < self.max_retries:
                    raise self.retry(countdown=60)

        result = (
            f"Reminders: {success_count} sent, "
            f"{fail_count} failed for {today}"
        )
        logger.info(result)
        return result


def _render_reminder_email(apt):
    """Generate reminder email HTML."""
    doctor_name = (
        apt.doctor.user.full_name
        if apt.doctor else 'Doctor'
    )
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
    <h2>Appointment Reminder</h2>
    <p>Dear {apt.patient.user.full_name if apt.patient else 'Patient'},
    </p>
    <p>You have an appointment scheduled for today at
    <strong>{apt.time}</strong> with
    <strong>Dr. {doctor_name}</strong>
    ({apt.doctor.specialization if apt.doctor else 'N/A'}).</p>
    <p>Please arrive 10 minutes early.</p>
    <br>
    <p>HealthCare HMS</p>
    </body>
    </html>
    """


@celery_app.task(bind=True, autoretry_for=(Exception,), max_retries=3)
def send_monthly_reports(self):
    app = get_app()
    with app.app_context():
        from backend.models.user import DoctorProfile, Appointment
        from backend.app import mail
        from flask_mail import Message

        last_month = (
            date.today().replace(day=1) - timedelta(days=1)
        )
        month_start = last_month.replace(day=1)
        month_end = last_month

        doctors = DoctorProfile.query.all()
        success_count = 0
        fail_count = 0

        for doctor in doctors:
            try:
                appointments = Appointment.query.filter(
                    Appointment.doctor_id == doctor.id,
                    Appointment.date >= month_start,
                    Appointment.date <= month_end,
                    Appointment.status == 'Completed'
                ).all()

                if not appointments:
                    logger.info(
                        f"No appointments for "
                        f"doctor {doctor.id} in {month_start}"
                    )
                    continue

                rows = _render_report_table_rows(appointments)

                html_report = (
                    f"<html><body style="
                    f"'font-family: Arial, sans-serif;'>"
                    f"<h2>Monthly Activity Report - {
                        last_month.strftime('%B %Y')
                    }</h2>"
                    f"<p>Doctor: <strong>Dr. {
                        doctor.user.full_name
                    }</strong></p>"
                    f"<p>Department: {
                        doctor.department.name
                        if doctor.department else 'N/A'
                    }</p>"
                    f"<p>Total Appointments: <strong>{
                        len(appointments)
                    }</strong></p>"
                    f"<table border='1' cellpadding='8' "
                    f"cellspacing='0'>"
                    f"<thead><tr><th>Patient</th><th>Date</th>"
                    f"<th>Diagnosis</th><th>Prescription</th>"
                    f"</tr></thead>"
                    f"<tbody>{rows}</tbody></table>"
                    f"</body></html>"
                )

                msg = Message(
                    subject=(
                        f'Monthly Report - '
                        f'{last_month.strftime("%B %Y")}'
                    ),
                    recipients=[doctor.user.email],
                    html=html_report
                )
                mail.send(msg)
                success_count += 1
                logger.info(f"Report sent for doctor {doctor.id}")

            except Exception as e:
                fail_count += 1
                logger.error(
                    f"Failed to send report for doctor "
                    f"{doctor.id}: {e}"
                )
                if self.request.retries < self.max_retries:
                    raise self.retry(countdown=60)

        result = (
            f"Reports: {success_count} sent, "
            f"{fail_count} failed"
        )
        logger.info(result)
        return result


def _render_report_table_rows(appointments):
    """Generate report table rows HTML."""
    rows = ""
    for apt in appointments:
        t = apt.treatment
        patient_name = (
            apt.patient.user.full_name
            if apt.patient and apt.patient.user
            else 'N/A'
        )
        diagnosis = t.diagnosis if t else 'N/A'
        prescription = t.prescription if t else 'N/A'

        rows += f"""
        <tr>
            <td>{patient_name}</td>
            <td>{apt.date}</td>
            <td>{diagnosis}</td>
            <td>{prescription}</td>
        </tr>"""

    return rows


@celery_app.task(bind=True, autoretry_for=(Exception,), max_retries=3)
def export_patient_csv(self, job_id, user_id):
    app = get_app()
    with app.app_context():
        from backend.models.user import (
            ExportJob, PatientProfile, Appointment
        )
        from backend.app import db

        job = ExportJob.query.get(job_id)
        if not job:
            logger.error(f"Export job {job_id} not found")
            return

        try:
            job.status = 'processing'
            db.session.commit()
            logger.info(f"Processing export job {job_id}")

            patient = PatientProfile.query.filter_by(
                user_id=user_id
            ).first()
            if not patient:
                job.status = 'failed'
                db.session.commit()
                logger.error(f"Patient {user_id} not found")
                return

            appointments = Appointment.query.filter(
                Appointment.patient_id == patient.id,
                Appointment.status == 'Completed'
            ).order_by(Appointment.date.desc()).all()

            os.makedirs('exports', exist_ok=True)
            filepath = (
                f'exports/patient_{user_id}_treatments_'
                f'{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
            )

            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Patient ID', 'Patient Name',
                    'Consulting Doctor', 'Department',
                    'Appointment Date', 'Appointment Time',
                    'Diagnosis', 'Treatment/Prescription',
                    'Notes', 'Next Visit'
                ])
                for apt in appointments:
                    t = apt.treatment
                    writer.writerow([
                        patient.id,
                        (
                            patient.user.full_name
                            if patient.user else ''
                        ),
                        (
                            apt.doctor.user.full_name
                            if apt.doctor and apt.doctor.user
                            else ''
                        ),
                        (
                            apt.doctor.department.name
                            if apt.doctor and apt.doctor.department
                            else ''
                        ),
                        apt.date.isoformat(),
                        apt.time,
                        t.diagnosis if t else '',
                        t.prescription if t else '',
                        t.notes if t else '',
                        (
                            t.next_visit.isoformat()
                            if t and t.next_visit else ''
                        )
                    ])

            job.status = 'done'
            job.file_path = filepath
            db.session.commit()
            logger.info(
                f"Export job {job_id} completed: {filepath}"
            )

        except Exception as e:
            job.status = 'failed'
            db.session.commit()
            logger.error(f"Export job {job_id} failed: {e}")
            if self.request.retries < self.max_retries:
                raise self.retry(exc=e, countdown=30)
