from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from backend.app import db
from backend.models.user import User, DoctorProfile, PatientProfile, Appointment, Department
from functools import wraps
import redis
import json

admin_bp = Blueprint('admin', __name__)
cache = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
CACHE_TTL = 300

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
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

def invalidate_cache(pattern):
    try:
        keys = cache.keys(pattern)
        if keys:
            cache.delete(*keys)
    except:
        pass

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    cached = try_cache_get('admin:dashboard')
    if cached:
        return jsonify(cached), 200

    total_doctors = DoctorProfile.query.join(User).filter(User.is_active == True).count()
    total_patients = PatientProfile.query.join(User).filter(User.is_active == True).count()
    total_appointments = Appointment.query.count()
    booked = Appointment.query.filter_by(status='Booked').count()
    completed = Appointment.query.filter_by(status='Completed').count()
    cancelled = Appointment.query.filter_by(status='Cancelled').count()

    data = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'booked_appointments': booked,
        'completed_appointments': completed,
        'cancelled_appointments': cancelled
    }
    try_cache_set('admin:dashboard', data)
    return jsonify(data), 200

@admin_bp.route('/doctors', methods=['GET'])
@admin_required
def get_doctors():
    cached = try_cache_get('admin:doctors')
    if cached:
        return jsonify(cached), 200
    doctors = DoctorProfile.query.join(User).all()
    data = [d.to_dict() for d in doctors]
    try_cache_set('admin:doctors', data)
    return jsonify(data), 200

@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def create_doctor():
    data = request.get_json()
    required = ['username', 'email', 'password', 'full_name', 'specialization', 'department_id']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 409
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role='doctor',
        full_name=data['full_name'],
        phone=data.get('phone', ''),
        is_active=True
    )
    db.session.add(user)
    db.session.flush()

    profile = DoctorProfile(
        user_id=user.id,
        department_id=data['department_id'],
        specialization=data['specialization'],
        qualification=data.get('qualification', ''),
        experience_years=data.get('experience_years', 0),
        consultation_fee=data.get('consultation_fee', 500.0),
        bio=data.get('bio', '')
    )
    db.session.add(profile)
    db.session.commit()
    invalidate_cache('admin:*')
    return jsonify(profile.to_dict()), 201

@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@admin_required
def update_doctor(doctor_id):
    doctor = DoctorProfile.query.get_or_404(doctor_id)
    data = request.get_json()

    if 'full_name' in data: doctor.user.full_name = data['full_name']
    if 'email' in data: doctor.user.email = data['email']
    if 'phone' in data: doctor.user.phone = data['phone']
    if 'specialization' in data: doctor.specialization = data['specialization']
    if 'department_id' in data: doctor.department_id = data['department_id']
    if 'qualification' in data: doctor.qualification = data['qualification']
    if 'experience_years' in data: doctor.experience_years = data['experience_years']
    if 'consultation_fee' in data: doctor.consultation_fee = data['consultation_fee']
    if 'bio' in data: doctor.bio = data['bio']

    db.session.commit()
    invalidate_cache('admin:*')
    return jsonify(doctor.to_dict()), 200

@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@admin_required
def delete_doctor(doctor_id):
    doctor = DoctorProfile.query.get_or_404(doctor_id)
    doctor.user.is_active = False
    db.session.commit()
    invalidate_cache('admin:*')
    return jsonify({'message': 'Doctor deactivated'}), 200

@admin_bp.route('/doctors/<int:doctor_id>/toggle', methods=['POST'])
@admin_required
def toggle_doctor(doctor_id):
    doctor = DoctorProfile.query.get_or_404(doctor_id)
    doctor.user.is_active = not doctor.user.is_active
    db.session.commit()
    invalidate_cache('admin:*')
    return jsonify({'is_active': doctor.user.is_active}), 200

@admin_bp.route('/patients', methods=['GET'])
@admin_required
def get_patients():
    cached = try_cache_get('admin:patients')
    if cached:
        return jsonify(cached), 200
    patients = PatientProfile.query.join(User).all()
    data = [p.to_dict() for p in patients]
    try_cache_set('admin:patients', data)
    return jsonify(data), 200

@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@admin_required
def update_patient(patient_id):
    patient = PatientProfile.query.get_or_404(patient_id)
    data = request.get_json()
    
    # Update User fields
    if 'full_name' in data: 
        patient.user.full_name = data['full_name']
    if 'email' in data: 
        patient.user.email = data['email']
    if 'phone' in data: 
        patient.user.phone = data['phone']
    if 'is_active' in data: 
        patient.user.is_active = data['is_active']
    
    # Update Patient Profile fields
    if 'gender' in data: 
        patient.gender = data['gender']
    if 'blood_group' in data: 
        patient.blood_group = data['blood_group']
    if 'address' in data: 
        patient.address = data['address']
    
    db.session.commit()
    invalidate_cache('admin:*')
    return jsonify(patient.to_dict()), 200

@admin_bp.route('/patients/<int:patient_id>/toggle', methods=['POST'])
@admin_required
def toggle_patient(patient_id):
    patient = PatientProfile.query.get_or_404(patient_id)
    patient.user.is_active = not patient.user.is_active
    db.session.commit()
    invalidate_cache('admin:*')
    return jsonify({'is_active': patient.user.is_active}), 200

@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def get_all_appointments():
    appointments = Appointment.query.order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in appointments]), 200

@admin_bp.route('/search', methods=['GET'])
@admin_required
def search():
    q = request.args.get('q', '').strip()
    stype = request.args.get('type', 'all')
    results = {}

    if stype in ('all', 'doctor'):
        doctors = DoctorProfile.query.join(User).filter(
            (User.full_name.ilike(f'%{q}%')) |
            (DoctorProfile.specialization.ilike(f'%{q}%'))
        ).all()
        results['doctors'] = [d.to_dict() for d in doctors]

    if stype in ('all', 'patient'):
        patients = PatientProfile.query.join(User).filter(
            (User.full_name.ilike(f'%{q}%')) |
            (User.email.ilike(f'%{q}%')) |
            (User.phone.ilike(f'%{q}%'))
        ).all()
        results['patients'] = [p.to_dict() for p in patients]

    return jsonify(results), 200

@admin_bp.route('/departments', methods=['GET'])
@admin_required
def get_departments():
    depts = Department.query.all()
    return jsonify([d.to_dict() for d in depts]), 200
