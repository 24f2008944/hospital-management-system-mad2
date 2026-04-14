# backend/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
from flask_security import UserMixin, RoleMixin
import uuid
import secrets

# This will be initialized in app.py
db = SQLAlchemy()

# Association table for the many-to-many relationship between Users and Roles
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    confirmed_at = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer, default=0)
    
    # Many-to-Many relationship with Role
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def get_auth_token(self):
        # Generate a simple token using user id and secrets
        return secrets.token_urlsafe(32)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'active': self.active,
            'roles': [role.name for role in self.roles],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }

    def __repr__(self):
        return f'<User {self.email}>'

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'doctors_count': len(self.doctors),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Department {self.name}>'

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    user = db.relationship('User', backref=db.backref('doctor_profile', uselist=False))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    department = db.relationship('Department', backref='doctors')
    license_number = db.Column(db.String(50), unique=True, nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    experience_years = db.Column(db.Integer, default=0)
    qualification = db.Column(db.String(200), nullable=True)
    consultation_fee = db.Column(db.Float, default=0.0)
    available_days = db.Column(db.String(100), nullable=True)  # JSON string of available days
    available_time_start = db.Column(db.Time, nullable=True)
    available_time_end = db.Column(db.Time, nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    blacklist_reason = db.Column(db.Text, nullable=True)
    blacklist_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user else None,
            'department': self.department.to_dict() if self.department else None,
            'license_number': self.license_number,
            'specialization': self.specialization,
            'experience_years': self.experience_years,
            'qualification': self.qualification,
            'consultation_fee': self.consultation_fee,
            'available_days': self.available_days,
            'available_time_start': self.available_time_start.strftime('%H:%M') if self.available_time_start else None,
            'available_time_end': self.available_time_end.strftime('%H:%M') if self.available_time_end else None,
            'contact_number': self.contact_number,
            'is_active': self.is_active,
            'blacklist_reason': self.blacklist_reason,
            'blacklist_date': self.blacklist_date.isoformat() if self.blacklist_date else None,
            'appointments_count': len(self.appointments),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Doctor {self.user.username if self.user else "Unknown"}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    user = db.relationship('User', backref=db.backref('patient_profile', uselist=False))
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    emergency_contact = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    blood_group = db.Column(db.String(5), nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    medical_history = db.Column(db.Text, nullable=True)
    insurance_details = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    blacklist_reason = db.Column(db.Text, nullable=True)
    blacklist_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name or ''} {self.last_name or ''}".strip(),
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'contact_number': self.contact_number,
            'emergency_contact': self.emergency_contact,
            'address': self.address,
            'blood_group': self.blood_group,
            'allergies': self.allergies,
            'medical_history': self.medical_history,
            'insurance_details': self.insurance_details,
            'is_active': self.is_active,
            'blacklist_reason': self.blacklist_reason,
            'blacklist_date': self.blacklist_date.isoformat() if self.blacklist_date else None,
            'appointments_count': len(self.appointments),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Patient {self.user.username if self.user else "Unknown"}>'

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Booked')  # Booked, Completed, Cancelled, Rescheduled
    reason = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'appointment_date', 'appointment_time', 
                          name='unique_doctor_appointment'),
    )

    def to_dict(self):
        data = {
            'id': self.id,
            'patient': self.patient.to_dict() if self.patient else None,
            'doctor': self.doctor.to_dict() if self.doctor else None,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.strftime('%H:%M') if self.appointment_time else None,
            'status': self.status,
            'reason': self.reason,
            'notes': self.notes,
            'has_treatment': bool(self.treatment),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        # Add doctor details for frontend compatibility
        if self.doctor:
            data['doctor_name'] = self.doctor.user.username if self.doctor.user else 'Unknown'
            data['doctor_specialization'] = self.doctor.specialization or ''
            data['department_name'] = self.doctor.department.name if self.doctor.department else ''
            data['doctor_experience'] = self.doctor.experience_years or 0
        else:
            data['doctor_name'] = 'Unknown'
            data['doctor_specialization'] = ''
            data['department_name'] = ''
            data['doctor_experience'] = 0
        # Add patient details for frontend compatibility
        if self.patient:
            data['patient_name'] = self.patient.full_name if hasattr(self.patient, 'full_name') and self.patient.full_name else (self.patient.user.username if self.patient.user else 'Unknown')
            data['patient_email'] = self.patient.user.email if self.patient.user else ''
            data['patient_phone'] = self.patient.contact_number or ''
            data['patient_dob'] = self.patient.date_of_birth.isoformat() if self.patient.date_of_birth else ''
        else:
            data['patient_name'] = 'Unknown'
            data['patient_email'] = ''
            data['patient_phone'] = ''
            data['patient_dob'] = ''
        return data

    def __repr__(self):
        return f'<Appointment {self.id}: {self.patient} -> {self.doctor}>'

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False, unique=True)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=True)
    treatment_notes = db.Column(db.Text, nullable=True)
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date, nullable=True)
    cost = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    appointment = db.relationship('Appointment', backref=db.backref('treatment', uselist=False))

    def to_dict(self):
        data = {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'treatment_notes': self.treatment_notes,
            'notes': self.treatment_notes,  # Alias for frontend compatibility
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'cost': self.cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        # Add doctor and department info from appointment
        if self.appointment:
            # Doctor info
            if self.appointment.doctor and self.appointment.doctor.user:
                data['doctor_name'] = self.appointment.doctor.user.username
                data['doctor_email'] = self.appointment.doctor.user.email
            if self.appointment.doctor and self.appointment.doctor.department:
                data['department_name'] = self.appointment.doctor.department.name
                data['doctor_specialization'] = self.appointment.doctor.specialization
            # Appointment info
            data['appointment_date'] = self.appointment.appointment_date.isoformat() if self.appointment.appointment_date else None
            data['appointment_time'] = self.appointment.appointment_time.strftime('%H:%M') if self.appointment.appointment_time else None
            # Patient info
            if self.appointment.patient:
                patient = self.appointment.patient
                data['patient_id'] = patient.id
                data['patient_name'] = patient.full_name if hasattr(patient, 'full_name') else None
                data['patient_email'] = patient.user.email if patient.user else None
        return data

    def __repr__(self):
        return f'<Treatment for Appointment {self.appointment_id}>'

class DoctorAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    doctor = db.relationship('Doctor', backref='availability_slots')
    available_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    max_appointments = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.user.username if self.doctor and self.doctor.user else None,
            'available_date': self.available_date.isoformat() if self.available_date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'is_available': self.is_available,
            'max_appointments': self.max_appointments,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<DoctorAvailability {self.doctor_id} on {self.available_date}>'

class MedicalNote(db.Model):
    """Clinical notes added by doctors for patients"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    note_type = db.Column(db.String(50), nullable=False)  # Consultation, Follow-up, Observation, etc.
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_private = db.Column(db.Boolean, default=False)  # Private notes only visible to doctors
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='medical_notes')
    doctor = db.relationship('Doctor', backref='medical_notes')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.user.username if self.patient and self.patient.user else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.user.username if self.doctor and self.doctor.user else None,
            'note_type': self.note_type,
            'title': self.title,
            'content': self.content,
            'is_private': self.is_private,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<MedicalNote {self.id}: {self.title}>'