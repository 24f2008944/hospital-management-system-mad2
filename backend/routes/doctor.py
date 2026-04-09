from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db
from backend.models.user import User, DoctorProfile, DoctorAvailability, Appointment, Treatment, PatientProfile
from datetime import date, timedelta
from functools import wraps
import redis, json

doctor_bp = Blueprint('doctor', __name__)
cache = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

def doctor_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'doctor':
            return jsonify({'error': 'Doctor access required'}), 403
        return f(*args, **kwargs)
    return decorated

@doctor_bp.route('/dashboard', methods=['GET'])
@doctor_required
def dashboard():
    user_id = int(get_jwt_identity())
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    today = date.today()
    week_end = today + timedelta(days=7)

    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date >= today,
        Appointment.status == 'Booked'
    ).order_by(Appointment.date, Appointment.time).all()

    patients_today = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date == today,
        Appointment.status == 'Booked'
    ).count()

    return jsonify({
        'doctor': doctor.to_dict(),
        'upcoming_appointments': [a.to_dict() for a in upcoming],
        'patients_today': patients_today
    }), 200

@doctor_bp.route('/appointments', methods=['GET'])
@doctor_required
def get_appointments():
    user_id = int(get_jwt_identity())
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    status = request.args.get('status')
    query = Appointment.query.filter_by(doctor_id=doctor.id)
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in appointments]), 200

@doctor_bp.route('/appointments/<int:apt_id>/complete', methods=['POST'])
@doctor_required
def complete_appointment(apt_id):
    user_id = int(get_jwt_identity())
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    apt = Appointment.query.filter_by(id=apt_id, doctor_id=doctor.id).first_or_404()
    data = request.get_json()

    apt.status = 'Completed'
    if apt.treatment:
        apt.treatment.diagnosis = data.get('diagnosis', '')
        apt.treatment.prescription = data.get('prescription', '')
        apt.treatment.notes = data.get('notes', '')
        if data.get('next_visit'):
            from datetime import datetime
            apt.treatment.next_visit = datetime.strptime(data['next_visit'], '%Y-%m-%d').date()
    else:
        treatment = Treatment(
            appointment_id=apt_id,
            diagnosis=data.get('diagnosis', ''),
            prescription=data.get('prescription', ''),
            notes=data.get('notes', ''),
        )
        if data.get('next_visit'):
            from datetime import datetime
            treatment.next_visit = datetime.strptime(data['next_visit'], '%Y-%m-%d').date()
        db.session.add(treatment)

    db.session.commit()
    return jsonify(apt.to_dict()), 200

@doctor_bp.route('/appointments/<int:apt_id>/cancel', methods=['POST'])
@doctor_required
def cancel_appointment(apt_id):
    user_id = int(get_jwt_identity())
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    apt = Appointment.query.filter_by(id=apt_id, doctor_id=doctor.id).first_or_404()
    apt.status = 'Cancelled'
    db.session.commit()
    return jsonify(apt.to_dict()), 200

@doctor_bp.route('/patients', methods=['GET'])
@doctor_required
def get_patients():
    user_id = int(get_jwt_identity())
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    patient_ids = db.session.query(Appointment.patient_id).filter_by(doctor_id=doctor.id).distinct()
    patients = PatientProfile.query.filter(PatientProfile.id.in_(patient_ids)).all()
    return jsonify([p.to_dict() for p in patients]), 200

@doctor_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@doctor_required
def patient_history(patient_id):
    user_id = int(get_jwt_identity())
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    appointments = Appointment.query.filter_by(
        doctor_id=doctor.id, patient_id=patient_id
    ).order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in appointments]), 200

@doctor_bp.route('/availability', methods=['GET'])
@doctor_required
def get_availability():
    user_id = int(get_jwt_identity())
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    today = date.today()
    avails = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today
    ).order_by(DoctorAvailability.date).all()
    return jsonify([a.to_dict() for a in avails]), 200

@doctor_bp.route('/availability', methods=['POST'])
@doctor_required
def set_availability():
    user_id = int(get_jwt_identity())
    doctor = DoctorProfile.query.filter_by(user_id=user_id).first()
    data = request.get_json()

    from datetime import datetime
    avail_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

    existing = DoctorAvailability.query.filter_by(doctor_id=doctor.id, date=avail_date).first()
    if existing:
        existing.start_time = data.get('start_time', existing.start_time)
        existing.end_time = data.get('end_time', existing.end_time)
        existing.max_appointments = data.get('max_appointments', existing.max_appointments)
        existing.is_available = data.get('is_available', existing.is_available)
    else:
        avail = DoctorAvailability(
            doctor_id=doctor.id,
            date=avail_date,
            start_time=data.get('start_time', '09:00'),
            end_time=data.get('end_time', '17:00'),
            max_appointments=data.get('max_appointments', 10),
            is_available=data.get('is_available', True)
        )
        db.session.add(avail)

    db.session.commit()
    return jsonify({'message': 'Availability updated'}), 200
