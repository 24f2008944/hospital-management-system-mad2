from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db
from backend.models.user import User, PatientProfile, DoctorProfile, DoctorAvailability, Department, Appointment, ExportJob
from datetime import date, timedelta
from functools import wraps
import redis, json

patient_bp = Blueprint('patient', __name__)
cache = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
CACHE_TTL = 300

def patient_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'patient':
            return jsonify({'error': 'Patient access required'}), 403
        return f(*args, **kwargs)
    return decorated

def try_cache_get(key):
    try:
        val = cache.get(key)
        return json.loads(val) if val else None
    except:
        return None

def try_cache_set(key, val, ttl=CACHE_TTL):
    try:
        cache.setex(key, ttl, json.dumps(val))
    except:
        pass

@patient_bp.route('/dashboard', methods=['GET'])
@patient_required
def dashboard():
    user_id = int(get_jwt_identity())
    patient = PatientProfile.query.filter_by(user_id=user_id).first()
    if not patient:
        return jsonify({'error': 'Patient profile not found'}), 404

    today = date.today()
    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.date >= today,
        Appointment.status == 'Booked'
    ).order_by(Appointment.date).all()

    past = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status.in_(['Completed', 'Cancelled'])
    ).order_by(Appointment.date.desc()).limit(10).all()

    depts_cached = try_cache_get('departments:all')
    if depts_cached:
        departments = depts_cached
    else:
        departments = [d.to_dict() for d in Department.query.all()]
        try_cache_set('departments:all', departments)

    return jsonify({
        'patient': patient.to_dict(),
        'upcoming_appointments': [a.to_dict() for a in upcoming],
        'past_appointments': [a.to_dict() for a in past],
        'departments': departments
    }), 200

@patient_bp.route('/profile', methods=['PUT'])
@patient_required
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    patient = PatientProfile.query.filter_by(user_id=user_id).first()
    data = request.get_json()

    if 'full_name' in data: user.full_name = data['full_name']
    if 'phone' in data: user.phone = data['phone']
    if 'gender' in data: patient.gender = data['gender']
    if 'blood_group' in data: patient.blood_group = data['blood_group']
    if 'address' in data: patient.address = data['address']
    if 'emergency_contact' in data: patient.emergency_contact = data['emergency_contact']
    if 'medical_history' in data: patient.medical_history = data['medical_history']
    if 'date_of_birth' in data and data['date_of_birth']:
        from datetime import datetime
        patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()

    db.session.commit()
    return jsonify(patient.to_dict()), 200

@patient_bp.route('/doctors', methods=['GET'])
@patient_required
def get_doctors():
    specialization = request.args.get('specialization', '')
    dept_id = request.args.get('department_id')

    cache_key = f'doctors:spec:{specialization}:dept:{dept_id}'
    cached = try_cache_get(cache_key)
    if cached:
        return jsonify(cached), 200

    query = DoctorProfile.query.join(User).filter(User.is_active == True)
    if specialization:
        query = query.filter(DoctorProfile.specialization.ilike(f'%{specialization}%'))
    if dept_id:
        query = query.filter(DoctorProfile.department_id == int(dept_id))

    doctors = query.all()
    today = date.today()
    week_end = today + timedelta(days=7)

    result = []
    for d in doctors:
        doc_data = d.to_dict()
        avails = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == d.id,
            DoctorAvailability.date >= today,
            DoctorAvailability.date <= week_end,
            DoctorAvailability.is_available == True
        ).order_by(DoctorAvailability.date).all()
        doc_data['availabilities'] = [a.to_dict() for a in avails]
        result.append(doc_data)

    try_cache_set(cache_key, result, ttl=120)
    return jsonify(result), 200

@patient_bp.route('/appointments/history', methods=['GET'])
@patient_required
def appointment_history():
    user_id = int(get_jwt_identity())
    patient = PatientProfile.query.filter_by(user_id=user_id).first()
    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in appointments]), 200

@patient_bp.route('/export/trigger', methods=['POST'])
@patient_required
def trigger_export():
    user_id = int(get_jwt_identity())
    job = ExportJob(user_id=user_id, status='pending')
    db.session.add(job)
    db.session.commit()

    try:
        from backend.tasks.celery_tasks import export_patient_csv
        export_patient_csv.delay(job.id, user_id)
    except Exception:
        # Fallback: run synchronously if Celery not running
        _run_export_sync(job.id, user_id)

    return jsonify({'job_id': job.id, 'status': 'pending', 'message': 'Export triggered'}), 202

def _run_export_sync(job_id, user_id):
    import csv, os
    from io import StringIO
    job = ExportJob.query.get(job_id)
    if not job:
        return
    try:
        job.status = 'processing'
        db.session.commit()
        patient = PatientProfile.query.filter_by(user_id=user_id).first()
        appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.status == 'Completed'
        ).all()

        os.makedirs('exports', exist_ok=True)
        filepath = f'exports/patient_{user_id}_treatments.csv'
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Patient ID', 'Patient Name', 'Doctor', 'Date', 'Diagnosis', 'Prescription', 'Notes', 'Next Visit'])
            for apt in appointments:
                t = apt.treatment
                writer.writerow([
                    patient.id, patient.user.full_name if patient.user else '',
                    apt.doctor.user.full_name if apt.doctor and apt.doctor.user else '',
                    apt.date.isoformat(), t.diagnosis if t else '', t.prescription if t else '',
                    t.notes if t else '', t.next_visit.isoformat() if t and t.next_visit else ''
                ])
        job.status = 'done'
        job.file_path = filepath
        db.session.commit()
    except Exception as e:
        job.status = 'failed'
        db.session.commit()

@patient_bp.route('/export/status/<int:job_id>', methods=['GET'])
@patient_required
def export_status(job_id):
    user_id = int(get_jwt_identity())
    job = ExportJob.query.filter_by(id=job_id, user_id=user_id).first_or_404()
    return jsonify(job.to_dict()), 200

@patient_bp.route('/export/download/<int:job_id>', methods=['GET'])
@patient_required
def download_export(job_id):
    user_id = int(get_jwt_identity())
    job = ExportJob.query.filter_by(id=job_id, user_id=user_id, status='done').first_or_404()
    return send_file(job.file_path, as_attachment=True, download_name='treatment_history.csv')
