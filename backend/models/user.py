from backend.app import db
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    doctors = db.relationship('DoctorProfile', back_populates='department', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'doctor_count': len(self.doctors)
        }

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, doctor, patient
    full_name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor_profile = db.relationship('DoctorProfile', back_populates='user', uselist=False)
    patient_profile = db.relationship('PatientProfile', back_populates='user', uselist=False)

    def to_dict(self):
        d = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if self.doctor_profile:
            d['doctor_profile'] = self.doctor_profile.to_dict()
        if self.patient_profile:
            d['patient_profile'] = self.patient_profile.to_dict()
        return d

class DoctorProfile(db.Model):
    __tablename__ = 'doctor_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    specialization = db.Column(db.String(150))
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer, default=0)
    consultation_fee = db.Column(db.Float, default=500.0)
    bio = db.Column(db.Text)

    user = db.relationship('User', back_populates='doctor_profile')
    department = db.relationship('Department', back_populates='doctors')
    availabilities = db.relationship('DoctorAvailability', back_populates='doctor', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', back_populates='doctor', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.user.full_name if self.user else '',
            'email': self.user.email if self.user else '',
            'phone': self.user.phone if self.user else '',
            'department_id': self.department_id,
            'department': self.department.name if self.department else '',
            'specialization': self.specialization,
            'qualification': self.qualification,
            'experience_years': self.experience_years,
            'consultation_fee': self.consultation_fee,
            'bio': self.bio,
            'is_active': self.user.is_active if self.user else False,
        }

class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availabilities'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    max_appointments = db.Column(db.Integer, default=10)
    is_available = db.Column(db.Boolean, default=True)

    doctor = db.relationship('DoctorProfile', back_populates='availabilities')

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'date': self.date.isoformat(),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'max_appointments': self.max_appointments,
            'is_available': self.is_available
        }

class PatientProfile(db.Model):
    __tablename__ = 'patient_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    blood_group = db.Column(db.String(5))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(20))
    medical_history = db.Column(db.Text)

    user = db.relationship('User', back_populates='patient_profile')
    appointments = db.relationship('Appointment', back_populates='patient', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.user.full_name if self.user else '',
            'email': self.user.email if self.user else '',
            'phone': self.user.phone if self.user else '',
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'blood_group': self.blood_group,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'medical_history': self.medical_history,
            'is_active': self.user.is_active if self.user else False,
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_profiles.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='Booked')  # Booked, Completed, Cancelled
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = db.relationship('PatientProfile', back_populates='appointments')
    doctor = db.relationship('DoctorProfile', back_populates='appointments')
    treatment = db.relationship('Treatment', back_populates='appointment', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'patient_name': self.patient.user.full_name if self.patient and self.patient.user else '',
            'doctor_name': self.doctor.user.full_name if self.doctor and self.doctor.user else '',
            'department': self.doctor.department.name if self.doctor and self.doctor.department else '',
            'date': self.date.isoformat(),
            'time': self.time,
            'status': self.status,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'treatment': self.treatment.to_dict() if self.treatment else None
        }

class Treatment(db.Model):
    __tablename__ = 'treatments'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), unique=True, nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    next_visit = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship('Appointment', back_populates='treatment')

    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'notes': self.notes,
            'next_visit': self.next_visit.isoformat() if self.next_visit else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ExportJob(db.Model):
    __tablename__ = 'export_jobs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, done, failed
    file_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
