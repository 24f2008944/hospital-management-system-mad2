from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db
from backend.models.user import User, PatientProfile, DoctorProfile, DoctorAvailability, Appointment
from datetime import date, datetime

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/book', methods=['POST'])
@jwt_required()
def book_appointment():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'patient':
        return jsonify({'error': 'Patient access required'}), 403

    data = request.get_json()
    required = ['doctor_id', 'date', 'time']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    patient = PatientProfile.query.filter_by(user_id=user_id).first()
    if not patient:
        return jsonify({'error': 'Patient profile not found'}), 404

    apt_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    if apt_date < date.today():
        return jsonify({'error': 'Cannot book appointment in the past'}), 400

    # Check for conflicts
    existing = Appointment.query.filter_by(
        doctor_id=data['doctor_id'],
        date=apt_date,
        time=data['time'],
        status='Booked'
    ).first()
    if existing:
        return jsonify({'error': 'This time slot is already booked'}), 409

    # Check if patient already has appointment at same time
    patient_conflict = Appointment.query.filter_by(
        patient_id=patient.id,
        date=apt_date,
        time=data['time'],
        status='Booked'
    ).first()
    if patient_conflict:
        return jsonify({'error': 'You already have an appointment at this time'}), 409

    apt = Appointment(
        patient_id=patient.id,
        doctor_id=data['doctor_id'],
        date=apt_date,
        time=data['time'],
        reason=data.get('reason', ''),
        status='Booked'
    )
    db.session.add(apt)
    db.session.commit()
    return jsonify(apt.to_dict()), 201

@appointment_bp.route('/<int:apt_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_appointment(apt_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    patient = PatientProfile.query.filter_by(user_id=user_id).first()

    if user.role == 'patient' and patient:
        apt = Appointment.query.filter_by(id=apt_id, patient_id=patient.id).first_or_404()
    else:
        apt = Appointment.query.get_or_404(apt_id)

    if apt.status == 'Completed':
        return jsonify({'error': 'Cannot cancel a completed appointment'}), 400

    apt.status = 'Cancelled'
    db.session.commit()
    return jsonify(apt.to_dict()), 200

@appointment_bp.route('/<int:apt_id>/reschedule', methods=['PUT'])
@jwt_required()
def reschedule_appointment(apt_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    patient = PatientProfile.query.filter_by(user_id=user_id).first()

    if user.role == 'patient' and patient:
        apt = Appointment.query.filter_by(id=apt_id, patient_id=patient.id).first_or_404()
    else:
        apt = Appointment.query.get_or_404(apt_id)

    if apt.status != 'Booked':
        return jsonify({'error': 'Only booked appointments can be rescheduled'}), 400

    data = request.get_json()
    new_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    new_time = data['time']

    conflict = Appointment.query.filter_by(
        doctor_id=apt.doctor_id,
        date=new_date,
        time=new_time,
        status='Booked'
    ).filter(Appointment.id != apt_id).first()
    if conflict:
        return jsonify({'error': 'This time slot is already taken'}), 409

    apt.date = new_date
    apt.time = new_time
    db.session.commit()
    return jsonify(apt.to_dict()), 200

@appointment_bp.route('/slots', methods=['GET'])
@jwt_required()
def get_slots():
    doctor_id = request.args.get('doctor_id', type=int)
    apt_date = request.args.get('date')
    if not doctor_id or not apt_date:
        return jsonify({'error': 'doctor_id and date required'}), 400

    apt_date_obj = datetime.strptime(apt_date, '%Y-%m-%d').date()
    avail = DoctorAvailability.query.filter_by(
        doctor_id=doctor_id, date=apt_date_obj, is_available=True
    ).first()

    if not avail:
        return jsonify({'slots': [], 'available': False}), 200

    # Generate slots every 30 mins between start and end (supports 24-hour format including night shifts)
    booked_times = [a.time for a in Appointment.query.filter_by(
        doctor_id=doctor_id, date=apt_date_obj, status='Booked'
    ).all()]

    start_h, start_m = map(int, avail.start_time.split(':'))
    end_h, end_m = map(int, avail.end_time.split(':'))
    
    # Convert to minutes for easier calculation
    start_mins = start_h * 60 + start_m
    end_mins = end_h * 60 + end_m
    
    # Handle night shifts where end_time < start_time (e.g., 22:00 to 06:00)
    if end_mins <= start_mins:
        end_mins += 24 * 60  # Add 24 hours to end time
    
    slots = []
    current_mins = start_mins
    
    while current_mins < end_mins:
        # Convert back to hours and minutes
        display_h = (current_mins // 60) % 24
        display_m = current_mins % 60
        slot = f'{display_h:02d}:{display_m:02d}'
        slots.append({'time': slot, 'available': slot not in booked_times})
        current_mins += 30

    return jsonify({'slots': slots, 'available': True}), 200
