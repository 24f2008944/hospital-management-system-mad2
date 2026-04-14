from mail import send_email
import os
from dotenv import load_dotenv
import csv
import io
import sys
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from celery_app import celery

load_dotenv()

def get_app_context():
    try:
        from app import app
        return app
    except ImportError:
        sys.path.insert(0, os.path.dirname(__file__))
        from app import app
        return app

@celery.task(bind=True)
def send_daily_reminders(self):
    app = get_app_context()
    with app.app_context():
        from app import db
        from models import Appointment, Doctor, Patient
        today = date.today()
        appointments = db.session.query(Appointment).filter_by(
            status='Booked',
            appointment_date=today
        ).all()
        reminder_count = 0
        for appointment in appointments:
            patient = appointment.patient
            doctor = appointment.doctor
            try:
                html_body = f"""
                <div>
                    <p>Dear {patient.first_name or patient.user.username},</p>
                    <p>This is a friendly reminder for your appointment today at our hospital.</p>
                    <div>
                        <ul>
                            <li>Please arrive <strong>15 minutes early</strong></li>
                            <li>Bring your medical records and ID</li>
                            <li>If you cannot attend, please contact us immediately</li>
                        </ul>
                    </div>
                    <p>Best regards,<br>Hospital Management Team</p>
                </div>
                """
                send_email(
                    to=patient.user.email,
                    subject="Today's Appointment Reminder - Hospital Visit",
                    message=html_body,
                    content="html"
                )
                reminder_count += 1
                print(f"[OK] Email sent to {patient.user.email}")
            except Exception as e:
                print(f"[ERROR] Failed to send email to {patient.user.email}: {str(e)}")

        return f"Daily reminders sent: {reminder_count} emails for {len(appointments)} appointments scheduled TODAY"

@celery.task(bind=True)
def export_patient_treatments_csv(self, patient_id):
    app = get_app_context()
    with app.app_context():
        from app import db
        from models import Appointment, Doctor, Patient, Treatment
        patient = db.session.query(Patient).get(patient_id)
        if not patient:
            return "Patient not found"
        treatments = db.session.query(Treatment).join(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.status == 'Completed'
        ).order_by(Appointment.appointment_date.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Date', 'Doctor', 'Department', 'Diagnosis', 'Prescription',
            'Treatment Notes', 'Cost', 'Follow-up Required', 'Follow-up Date'
        ])
        for treatment in treatments:
            appointment = treatment.appointment
            doctor = appointment.doctor
            writer.writerow([
                appointment.appointment_date.strftime('%Y-%m-%d'),
                f"Dr. {doctor.user.username}",
                doctor.department.name,
                treatment.diagnosis,
                treatment.prescription or '',
                treatment.treatment_notes or '',
                f"${treatment.cost:.2f}",
                'Yes' if treatment.follow_up_required else 'No',
                treatment.follow_up_date.strftime('%Y-%m-%d') if treatment.follow_up_date else ''
            ])
        csv_content = output.getvalue()
        output.close()
        filename = f"patient_{patient_id}_treatments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join('exports', filename)
        os.makedirs('exports', exist_ok=True)
        with open(filepath, 'w', newline='') as f:
            f.write(csv_content)
        try:
            body = f"""
Dear {patient.first_name or patient.user.username},

Your treatment history export is ready. Please find the attached CSV file with all your treatment records.

The export includes:
- Appointment dates
- Consulting doctors
- Diagnoses
- Prescriptions
- Treatment notes
- Costs
- Follow-up information

Best regards,
Hospital Management Team
"""
            send_email(
                to=patient.user.email,
                subject='Treatment History Export',
                message=body,
                content="plain",
                attachment_file=filepath
            )
            os.remove(filepath)
            return f"Treatment history exported and sent to {patient.user.email}"
        except Exception as e:
            return f"Failed to send export: {str(e)}"



@celery.task(bind=True)
def send_doctor_monthly_report(self, doctor_id, year, month):
    app = get_app_context()
    with app.app_context():
        from models import Doctor, Appointment, Treatment
        from app import db
        print(f"[DEBUG] send_doctor_monthly_report called with doctor_id={doctor_id}, year={year}, month={month}")
        doctor = db.session.query(Doctor).get(doctor_id)
        if not doctor:
            print(f"[ERROR] Doctor {doctor_id} not found")
            return f"Doctor {doctor_id} not found"
        print(f"[DEBUG] Found doctor: {doctor.user.username}, email: {doctor.user.email}")
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        appointments = db.session.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date < end_date
        ).all()
        print(f"[DEBUG] Appointments found for doctor in month: {len(appointments)}")
        html = f"""
        <div style='font-family: Arial; max-width: 700px;'>
            <h2>Monthly Activity Report for Dr. {doctor.user.username}</h2>
            <p>Month: {start_date.strftime('%B %Y')}</p>
            <h3>Appointments ({len(appointments)})</h3>
            <table border='1' cellpadding='6' cellspacing='0' style='border-collapse: collapse;'>
                <tr>
                    <th>Date</th>
                    <th>Patient</th>
                    <th>Diagnosis</th>
                    <th>Treatment</th>
                </tr>
        """
        for apt in appointments:
            treatment = db.session.query(Treatment).filter_by(appointment_id=apt.id).first()
            html += f"""
                <tr>
                    <td>{apt.appointment_date.strftime('%Y-%m-%d')}</td>
                    <td>{apt.patient.user.username}</td>
                    <td>{treatment.diagnosis if treatment else '-'} </td>
                    <td>{treatment.treatment_notes if treatment else '-'} </td>
                </tr>
            """
        html += "</table>"
        html += "<p>End of report.</p></div>"
        print(f"[INFO] Sending monthly report to {doctor.user.email} via Mailhog...")
        print(f"[DEBUG] SMTP settings: server={os.getenv('MAIL_SERVER')}, port={os.getenv('MAIL_PORT')}")
        send_email(
            to=doctor.user.email,
            subject=f"Monthly Activity Report - {start_date.strftime('%B %Y')}",
            message=html,
            content="html"
        )
        print(f"[OK] Report sent to {doctor.user.email}")
        return f"Report sent to {doctor.user.email}"


mail_api = Blueprint('mail_api', __name__)
report_api = Blueprint('report_api', __name__)

@mail_api.route('/api/send-patient-mail', methods=['POST'])
def send_patient_mail_api():
    from models import Appointment
    data = request.get_json()
    appointment_id = data.get('appointment_id')
    if not appointment_id:
        return jsonify({'error': 'Missing appointment_id'}), 400
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    send_daily_reminders.apply_async(args=[])
    return jsonify({'message': 'Patient mail triggered successfully'})

@report_api.route('/api/send-monthly-report', methods=['POST'])
def trigger_monthly_report():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    year = data.get('year')
    month = data.get('month')
    if not all([doctor_id, year, month]):
        return jsonify({'error': 'Missing parameters'}), 400
    send_doctor_monthly_report.apply_async(args=[doctor_id, year, month])
    return jsonify({'message': 'Monthly report triggered'})

@celery.task(bind=True)
def send_all_doctors_monthly_reports(self):
    app = get_app_context()
    with app.app_context():
        from models import Doctor
        today = date.today()
        year = today.year
        month = today.month
        doctors = Doctor.query.all()
        for doctor in doctors:
            send_doctor_monthly_report.apply_async(args=[doctor.id, year, month])
        return f"Triggered monthly reports for {len(doctors)} doctors"
