from flask import request, jsonify, current_app
from flask_restful import Resource
from flask_security import auth_required, current_user, hash_password, login_user, logout_user, roles_required
from datetime import datetime, date, time, timedelta
import json
import pickle
from models import db, User, Role, Department, Doctor, Patient, Appointment, Treatment, DoctorAvailability, MedicalNote
from tasks import export_patient_treatments_csv, send_doctor_monthly_report

class PatientTreatmentHistoryResource(Resource):
    @auth_required()
    def get(self):
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return {'error': 'Patient profile not found'}, 404

        treatments = Treatment.query.join(Appointment).filter(Appointment.patient_id == patient.id).order_by(Treatment.created_at.desc()).all()
        return [treatment.to_dict() for treatment in treatments]

class PatientDashboardDepartmentsResource(Resource):
    def get(self):
        departments = Department.query.all()
        result = []
        for dept in departments:
            doctors = [doctor.to_dict() for doctor in dept.doctors if doctor.is_active]
            dept_data = dept.to_dict()
            dept_data['doctors'] = doctors
            result.append(dept_data)
        return jsonify(result)


class CacheService:
    @staticmethod
    def get(key):
        try:
            from app import cache
            if cache:
                data = cache.get(key)
                return pickle.loads(data) if data else None
        except:
            pass
        return None
    
    @staticmethod
    def set(key, value, timeout=300):
        try:
            from app import cache
            if cache:
                cache.setex(key, timeout, pickle.dumps(value))
        except:
            pass
    
    @staticmethod
    def delete(key):
        try:
            from app import cache
            if cache:
            
                if key.endswith('_'):
                    pattern = f"{key}*"
                    keys_to_delete = cache.keys(pattern)
                    if keys_to_delete:
                        cache.delete(*keys_to_delete)
                else:
                    cache.delete(key)
        except:
            pass

class AuthResource(Resource):
    def post(self):
        from app import user_datastore
        data = request.get_json()
        action = data.get('action')
        

        if action == 'login':
            email = data.get('email')
            password = data.get('password')

            user = user_datastore.find_user(email=email)
            if user and user.verify_and_update_password(password):
                # Check if user is a blocked doctor or patient
                blocked = False
                doctor = getattr(user, 'doctor_profile', None)
                patient = getattr(user, 'patient_profile', None)
                if doctor and doctor.blacklist_date:
                    blocked = True
                if patient and patient.blacklist_date:
                    blocked = True
                if blocked:
                    return {'success': False, 'message': 'Your account is blocked. Please contact the hospital.'}, 403
                login_user(user)
                return {
                    'success': True,
                    'user': user.to_dict()
                }
            return {'success': False, 'message': 'Invalid credentials'}, 401
        
        elif action == 'register':
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            role_name = data.get('role', 'patient')
            
            # Check if user exists
            existing_user = user_datastore.find_user(email=email)
            if existing_user:
                if not existing_user.active:
                    reason = ''
                    if role_name == 'doctor':
                        doctor = Doctor.query.filter_by(user_id=existing_user.id).first()
                        if doctor and doctor.blacklist_reason:
                            reason = f": {doctor.blacklist_reason}"
                    elif role_name == 'patient':
                        patient = Patient.query.filter_by(user_id=existing_user.id).first()
                        if patient and patient.blacklist_reason:
                            reason = f": {patient.blacklist_reason}"
                    return {'success': False, 'message': f'This account has been blacklisted{reason}'}, 403
                return {'success': False, 'message': 'User already exists'}, 400
            
            
            role = user_datastore.find_role(role_name)
            if not role:
                return {'success': False, 'message': 'Invalid role'}, 400
            
            user = user_datastore.create_user(
                email=email,
                username=username,
                password=hash_password(password),
                active=True,
                roles=[role]
            )
            
            
            db.session.commit()
            
        
            if role_name == 'patient':
                patient = Patient(user_id=user.id)
                db.session.add(patient)
                db.session.commit()
            
            return {
                'success': True,
                'user': user.to_dict(),
                'message': 'Registration successful'
            }
        
        elif action == 'logout':
            logout_user()
            return {'success': True, 'message': 'Logged out successfully'}
        
        return {'success': False, 'message': 'Invalid action'}, 400

class DashboardResource(Resource):
    @auth_required()
    def get(self):
        cache_key = f"dashboard_{current_user.id}"
        cached_data = CacheService.get(cache_key)
        if cached_data:
            return cached_data
        
        user_roles = [role.name for role in current_user.roles]
        
        if 'admin' in user_roles:
            data = {
                'role': 'admin',
                'stats': {
                    'total_doctors': Doctor.query.filter_by(is_active=True).count(),
                    'total_patients': Patient.query.filter_by(is_active=True).count(),
                    'total_appointments': Appointment.query.count(),
                    'pending_appointments': Appointment.query.filter_by(status='Booked').count(),
                    'completed_appointments': Appointment.query.filter_by(status='Completed').count(),
                    'departments': Department.query.count()
                },
                'recent_appointments': [apt.to_dict() for apt in 
                    Appointment.query.order_by(Appointment.created_at.desc()).limit(5)]
            }
        
        elif 'doctor' in user_roles:
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if doctor:
                today = date.today()
                data = {
                    'role': 'doctor',
                    'doctor': doctor.to_dict(),
                    'stats': {
                        'today_appointments': Appointment.query.filter_by(
                            doctor_id=doctor.id, 
                            appointment_date=today,
                            status='Booked'
                        ).count(),
                        'total_patients': Appointment.query.filter_by(
                            doctor_id=doctor.id
                        ).distinct(Appointment.patient_id).count(),
                        'completed_treatments': Appointment.query.filter_by(
                            doctor_id=doctor.id,
                            status='Completed'
                        ).count()
                    },
                    'upcoming_appointments': [apt.to_dict() for apt in 
                        Appointment.query.filter_by(doctor_id=doctor.id, status='Booked')
                        .filter(Appointment.appointment_date >= today)
                        .order_by(Appointment.appointment_date, Appointment.appointment_time).limit(10)]
                }
            else:
                data = {'role': 'doctor', 'error': 'Doctor profile not found'}
        
        elif 'patient' in user_roles:
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if patient:
                today = date.today()
                data = {
                    'role': 'patient',
                    'patient': patient.to_dict(),
                    'stats': {
                        'total_appointments': Appointment.query.filter(
                            Appointment.patient_id == patient.id,
                            Appointment.status != 'Cancelled'
                        ).count(),
                        'upcoming_appointments': Appointment.query.filter_by(
                            patient_id=patient.id, status='Booked'
                        ).filter(Appointment.appointment_date >= today).count(),
                        'completed_treatments': Appointment.query.filter_by(
                            patient_id=patient.id,
                            status='Completed'
                        ).count()
                    },
                    'upcoming_appointments': [apt.to_dict() for apt in 
                            Appointment.query.filter_by(patient_id=patient.id, status='Booked')
                            .filter(Appointment.appointment_date >= today)
                            .order_by(Appointment.appointment_date, Appointment.appointment_time).all()],
                    'appointments': [apt.to_dict() for apt in Appointment.query.filter_by(patient_id=patient.id)
                        .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()],
                    'departments': [dept.to_dict() for dept in Department.query.all()]
                }
            else:
                data = {'role': 'patient', 'error': 'Patient profile not found'}
        
        else:
            data = {'error': 'Unknown role'}
        
        CacheService.set(cache_key, data, 300)  
        return data

class DepartmentListResource(Resource):
    @auth_required()
    def get(self):
        cache_key = "departments_list"
        cached_data = CacheService.get(cache_key)
        if cached_data:
            return cached_data
        
        departments = Department.query.all()
        data = [dept.to_dict() for dept in departments]
        
        CacheService.set(cache_key, data, 600)  
        return data
    
    @auth_required()
    def post(self):
        if not current_user.has_role('admin'):
            return {'error': 'Unauthorized'}, 403
        
        data = request.get_json()
        department = Department(
            name=data.get('name'),
            description=data.get('description')
        )
        
        try:
            db.session.add(department)
            db.session.commit()
            CacheService.delete("departments_list")
            return department.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

class DepartmentResource(Resource):
    @auth_required()
    def get(self, dept_id):
        department = Department.query.get_or_404(dept_id)
        return department.to_dict()
    
    @auth_required()
    def put(self, dept_id):
        if not current_user.has_role('admin'):
            return {'error': 'Unauthorized'}, 403
        
        department = Department.query.get_or_404(dept_id)
        data = request.get_json()
        
        department.name = data.get('name', department.name)
        department.description = data.get('description', department.description)
        
        try:
            db.session.commit()
            CacheService.delete("departments_list")
            return department.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400
    
    @auth_required()
    def delete(self, dept_id):
        if not current_user.has_role('admin'):
            return {'error': 'Unauthorized'}, 403
        
        department = Department.query.get_or_404(dept_id)
        
        try:
            db.session.delete(department)
            db.session.commit()
            CacheService.delete("departments_list")
            return {'message': 'Department deleted successfully'}
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

class DoctorListResource(Resource):
    def get(self):
        # anauthorized user
        search = request.args.get('search', '')
        department_id = request.args.get('department_id')
        
        cache_key = f"doctors_list_{search}_{department_id}"
        cached_data = CacheService.get(cache_key)
        if cached_data:
            return cached_data
        
        query = Doctor.query.filter_by(is_active=True)
        
        if search:
            query = query.join(User).filter(
                db.or_(
                    User.username.contains(search),
                    User.email.contains(search),
                    Doctor.specialization.contains(search)
                )
            )
        
        if department_id:
            query = query.filter_by(department_id=department_id)
        
        doctors = query.all()
        data = [doctor.to_dict() for doctor in doctors]
        
        CacheService.set(cache_key, data, 300)  
        return data
    
    @auth_required()
    def post(self):
        from app import user_datastore
        if not current_user.has_role('admin'):
            return {'error': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        
        required_fields = ['email', 'username', 'department_id']
        for field in required_fields:
            if not data.get(field):
                return {'error': f'Missing required field: {field}'}, 400
        
        try:
            
            role = user_datastore.find_role('doctor')
            user = user_datastore.create_user(
                email=data.get('email'),
                username=data.get('username'),
                password=hash_password(data.get('password', 'doctor123')),
                active=True,
                roles=[role]
            )
            
            
            db.session.commit()
            
           
            doctor = Doctor(
                user_id=user.id,
                department_id=data.get('department_id'),
                license_number=data.get('license_number'),
                specialization=data.get('specialization'),
                experience_years=data.get('experience_years', 0),
                qualification=data.get('qualification'),
                consultation_fee=data.get('consultation_fee', 0.0),
                available_days=data.get('available_days'),
                available_time_start=datetime.strptime(data.get('available_time_start'), '%H:%M').time() if data.get('available_time_start') else None,
                available_time_end=datetime.strptime(data.get('available_time_end'), '%H:%M').time() if data.get('available_time_end') else None,
                contact_number=data.get('contact_number')
            )
            
            db.session.add(doctor)
            db.session.commit()
            CacheService.delete("doctors_list__")
            
            CacheService.delete("dashboard_")
            return doctor.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            import traceback
            current_app.logger.error(f"Error creating doctor: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return {'error': str(e)}, 400

class DoctorResource(Resource):
    @auth_required()
    def get(self, doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        return doctor.to_dict()
    
    @auth_required()
    def put(self, doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        
        if not (current_user.has_role('admin') or 
                (current_user.has_role('doctor') and doctor.user_id == current_user.id)):
            return {'error': 'Unauthorized'}, 403

        data = request.get_json()

    
        for field in ['license_number', 'specialization', 'experience_years', 
                      'qualification', 'consultation_fee', 'available_days', 'contact_number']:
            if field in data:
                setattr(doctor, field, data[field])

        # Update time fields
        if 'available_time_start' in data and data['available_time_start']:
            doctor.available_time_start = datetime.strptime(data['available_time_start'], '%H:%M').time()
        if 'available_time_end' in data and data['available_time_end']:
            doctor.available_time_end = datetime.strptime(data['available_time_end'], '%H:%M').time()

        if 'department_id' in data:
            doctor.department_id = data['department_id']

        
        if doctor.user:
            if 'username' in data:
                doctor.user.username = data['username']
            if 'email' in data:
                doctor.user.email = data['email']

        try:
            db.session.commit()
            CacheService.delete("doctors_list__")
            CacheService.delete("dashboard_")
            return doctor.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400
    
    @auth_required()
    def delete(self, doctor_id):
        if not current_user.has_role('admin'):
            return {'error': 'Unauthorized'}, 403
        
        action = request.args.get('action', 'block')
        doctor = Doctor.query.get_or_404(doctor_id)
        data = request.get_json(silent=True) or {}
        
        if action == 'delete':
            user = doctor.user
            try:
                appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
                for appt in appointments:
                    if appt.treatment:
                        db.session.delete(appt.treatment)
                    db.session.delete(appt)
                
                DoctorAvailability.query.filter_by(doctor_id=doctor_id).delete(synchronize_session=False)
                MedicalNote.query.filter_by(doctor_id=doctor_id).delete(synchronize_session=False)
                
                db.session.delete(doctor)
                if user:
                    db.session.delete(user)
                db.session.commit()
                CacheService.delete("doctors_list__")
                CacheService.delete("dashboard_")
                return {'message': 'Doctor permanently deleted'}
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 400
        else:
            reason = data.get('reason', 'No reason provided')
            doctor.is_active = False
            doctor.blacklist_reason = reason
            doctor.blacklist_date = datetime.utcnow()
            
            try:
                db.session.commit()
                CacheService.delete("doctors_list__")
                CacheService.delete("dashboard_")
                return {'message': 'Doctor blocked successfully', 'reason': reason}
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 400

class PatientListResource(Resource):
    @auth_required()
    def get(self):
        if not (current_user.has_role('admin') or current_user.has_role('doctor')):
            return {'error': 'Unauthorized'}, 403
        
        search = request.args.get('search', '')
        cache_key = f"patients_list_{search}"
        cached_data = CacheService.get(cache_key)
        if cached_data:
            return cached_data
        
        query = Patient.query.filter_by(is_active=True)
        
        if search:
            query = query.join(User).filter(
                db.or_(
                    User.username.contains(search),
                    User.email.contains(search),
                    Patient.first_name.contains(search),
                    Patient.last_name.contains(search),
                    Patient.contact_number.contains(search)
                )
            )
        
        patients = query.all()
        data = [patient.to_dict() for patient in patients]
        
        CacheService.set(cache_key, data, 300)  
        return data
    
    @auth_required()
    def post(self):
        from app import user_datastore
        if not current_user.has_role('admin'):
            return {'error': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        
        role = user_datastore.find_role('patient')
        user = user_datastore.create_user(
            email=data.get('email'),
            username=data.get('username'),
            password=hash_password(data.get('password', 'patient123')),
            active=True,
            roles=[role]
        )
        
        
        patient = Patient(
            user_id=user.id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            gender=data.get('gender'),
            contact_number=data.get('contact_number'),
            emergency_contact=data.get('emergency_contact'),
            address=data.get('address'),
            blood_group=data.get('blood_group'),
            allergies=data.get('allergies'),
            medical_history=data.get('medical_history'),
            insurance_details=data.get('insurance_details')
        )
        
        try:
            db.session.add(patient)
            db.session.commit()
            CacheService.delete("patients_list_")
            CacheService.delete("dashboard_")
            return patient.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

class PatientResource(Resource):
    @auth_required()
    def get(self, patient_id):
        patient = Patient.query.get_or_404(patient_id)
        
        
        if not (current_user.has_role('admin') or 
                current_user.has_role('doctor') or
                (current_user.has_role('patient') and patient.user_id == current_user.id)):
            return {'error': 'Unauthorized'}, 403
        
        return patient.to_dict()
    
    @auth_required()
    def put(self, patient_id):
        patient = Patient.query.get_or_404(patient_id)

        if not (current_user.has_role('admin') or 
                (current_user.has_role('patient') and patient.user_id == current_user.id)):
            return {'error': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        
        for field in ['first_name', 'last_name', 'gender', 'contact_number', 
                      'emergency_contact', 'address', 'blood_group', 'allergies', 
                      'medical_history', 'insurance_details']:
            if field in data:
                setattr(patient, field, data[field])

        if 'date_of_birth' in data and data['date_of_birth']:
            patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()

        # Update related User email
        if patient.user and 'email' in data:
            patient.user.email = data['email']

        try:
            db.session.commit()
            CacheService.delete("patients_list_")
            CacheService.delete("dashboard_")
            return patient.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400
    
    @auth_required()
    def delete(self, patient_id):
        if not current_user.has_role('admin'):
            return {'error': 'Unauthorized'}, 403
        
        action = request.args.get('action', 'block')
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json(silent=True) or {}
        
        if action == 'delete':
            user = patient.user
            try:
                appointments = Appointment.query.filter_by(patient_id=patient_id).all()
                for appt in appointments:
                    if appt.treatment:
                        db.session.delete(appt.treatment)
                    db.session.delete(appt)
                
                MedicalNote.query.filter_by(patient_id=patient_id).delete(synchronize_session=False)
                
                db.session.delete(patient)
                if user:
                    db.session.delete(user)
                db.session.commit()
                CacheService.delete("patients_list_")
                CacheService.delete("dashboard_")
                return {'message': 'Patient permanently deleted'}
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 400
        else:
            reason = data.get('reason', 'No reason provided')
            patient.is_active = False
            patient.blacklist_reason = reason
            patient.blacklist_date = datetime.utcnow()
            
            try:
                db.session.commit()
                CacheService.delete("patients_list_")
                CacheService.delete("dashboard_")
                return {'message': 'Patient blocked successfully', 'reason': reason}
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 400

class BlacklistedDoctorsResource(Resource):
    @auth_required()
    def get(self):
        if not current_user.has_role('admin'):
            return {'error': 'Unauthorized'}, 403
        
        blacklisted_doctors = Doctor.query.filter_by(is_active=False).all()
        return [doctor.to_dict() for doctor in blacklisted_doctors]

class UnblockDoctorResource(Resource):
    @auth_required()
    def put(self, doctor_id):
        if not current_user.has_role('admin'):
            return {'error': 'Unauthorized'}, 403
        
        doctor = Doctor.query.get_or_404(doctor_id)
        doctor.is_active = True
        doctor.blacklist_reason = None
        doctor.blacklist_date = None
        
        try:
            db.session.commit()
            CacheService.delete("doctors_list__")
            CacheService.delete("dashboard_")
            return {'message': 'Doctor unblocked successfully'}
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

class BlacklistedPatientsResource(Resource):
    @auth_required()
    def get(self):
        if not current_user.has_role('admin'):
            return {'error': 'Unauthorized'}, 403
        
        blacklisted_patients = Patient.query.filter_by(is_active=False).all()
        return [patient.to_dict() for patient in blacklisted_patients]

class UnblockPatientResource(Resource):
    @auth_required()
    def put(self, patient_id):
        if not current_user.has_role('admin'):
            return {'error': 'Unauthorized'}, 403
        
        patient = Patient.query.get_or_404(patient_id)
        patient.is_active = True
        patient.blacklist_reason = None
        patient.blacklist_date = None
        
        try:
            db.session.commit()
            CacheService.delete("patients_list_")
            CacheService.delete("dashboard_")
            return {'message': 'Patient unblocked successfully'}
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

class DoctorPatientsResource(Resource):
    """Get all patients for a specific doctor"""
    
    @auth_required()
    @roles_required('doctor')
    def get(self):
        try:
            
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if not doctor:
                return {'error': 'Doctor profile not found'}, 404
            
           
            patient_ids = db.session.query(Appointment.patient_id).filter(
                Appointment.doctor_id == doctor.id
            ).distinct().all()
            
            patient_ids = [pid[0] for pid in patient_ids]
            
            if not patient_ids:
                return []
            
            # Get patient details
            patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
            
            result = []
            for patient in patients:
                patient_data = patient.to_dict()
                
                
                appointments_count = Appointment.query.filter_by(
                    doctor_id=doctor.id,
                    patient_id=patient.id
                ).count()
                
                
                treatments_count = Treatment.query.join(Appointment).filter(
                    Appointment.doctor_id == doctor.id,
                    Appointment.patient_id == patient.id
                ).count()
                
                patient_data['appointments_count'] = appointments_count
                patient_data['treatments_count'] = treatments_count
                patient_data['name'] = patient_data['full_name']
                patient_data['email'] = patient.user.email if patient.user else 'N/A'
                patient_data['phone'] = patient.contact_number
                
                result.append(patient_data)
            
            return result
            
        except Exception as e:
            print(f"Error in DoctorPatientsResource: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': 'Failed to load patients'}, 500

class PatientAppointmentsResource(Resource):
    """Get appointments for a specific patient"""
    
    @auth_required()
    def get(self, patient_id):
        try:
            # Check if user is doctor or admin or the patient themselves
            if current_user.has_role('doctor'):
                doctor = Doctor.query.filter_by(user_id=current_user.id).first()
                if not doctor:
                    return {'error': 'Doctor profile not found'}, 404
                
                appointments = Appointment.query.filter_by(
                    patient_id=patient_id,
                    doctor_id=doctor.id
                ).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
                
            elif current_user.has_role('admin'):
                
                appointments = Appointment.query.filter_by(
                    patient_id=patient_id
                ).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
                
            elif current_user.has_role('patient'):
                patient = Patient.query.get(patient_id)
                if not patient or patient.user_id != current_user.id:
                    return {'error': 'Unauthorized'}, 403
                
                appointments = Appointment.query.filter_by(
                    patient_id=patient_id
                ).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
            else:
                return {'error': 'Unauthorized'}, 403
            
            return [apt.to_dict() for apt in appointments]
            
        except Exception as e:
            print(f"Error in PatientAppointmentsResource: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': 'Failed to load appointments'}, 500

class PatientTreatmentsResource(Resource):
    """Get treatments for a specific patient"""
    
    @auth_required()
    def get(self, patient_id):
        try:
            # Check if user is doctor or admin or the patient themselves
            if current_user.has_role('doctor'):
                doctor = Doctor.query.filter_by(user_id=current_user.id).first()
                if not doctor:
                    return {'error': 'Doctor profile not found'}, 404
                
                treatments = Treatment.query.join(Appointment).filter(
                    Appointment.patient_id == patient_id,
                    Appointment.doctor_id == doctor.id
                ).order_by(Treatment.created_at.desc()).all()
                
            elif current_user.has_role('admin'):
                treatments = Treatment.query.join(Appointment).filter(
                    Appointment.patient_id == patient_id
                ).order_by(Treatment.created_at.desc()).all()
                
            elif current_user.has_role('patient'):
                patient = Patient.query.get(patient_id)
                if not patient or patient.user_id != current_user.id:
                    return {'error': 'Unauthorized'}, 403
                
                treatments = Treatment.query.join(Appointment).filter(
                    Appointment.patient_id == patient_id
                ).order_by(Treatment.created_at.desc()).all()
            else:
                return {'error': 'Unauthorized'}, 403
            
            return [treatment.to_dict() for treatment in treatments]
            
        except Exception as e:
            print(f"Error in PatientTreatmentsResource: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': 'Failed to load treatments'}, 500

class PatientOwnAppointmentsResource(Resource):
    """Patient's own appointments"""
    
    @auth_required()
    @roles_required('patient')
    def get(self):
        """Get all appointments for the logged-in patient"""
        try:
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if not patient:
                return {'message': 'Patient profile not found'}, 404
            
            appointments = Appointment.query.filter_by(
                patient_id=patient.id
            ).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
            
            return [apt.to_dict() for apt in appointments]
            
        except Exception as e:
            print(f"Error in PatientOwnAppointmentsResource: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'message': 'Failed to load appointments'}, 500

class PatientOwnTreatmentsResource(Resource):
    """Patient's own treatment history"""
    
    @auth_required()
    @roles_required('patient')
    def get(self):
        """Get all treatments for the logged-in patient"""
        try:
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if not patient:
                return {'error': 'Patient profile not found'}, 404
            
            treatments = Treatment.query.join(Appointment).filter(
                Appointment.patient_id == patient.id
            ).order_by(Treatment.created_at.desc()).all()
            
            return [treatment.to_dict() for treatment in treatments]
            
        except Exception as e:
            print(f"Error in PatientOwnTreatmentsResource: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': 'Failed to load treatments'}, 500

class MedicalNotesListResource(Resource):
    """Get and create medical notes for patients"""
    
    @auth_required()
    def get(self):
        """Get medical notes - filtered by role"""
        try:
            patient_id = request.args.get('patient_id')
            
            if current_user.has_role('doctor'):
                doctor = Doctor.query.filter_by(user_id=current_user.id).first()
                if not doctor:
                    return {'error': 'Doctor profile not found'}, 404
                
                query = MedicalNote.query
                
                if patient_id:
                    # Check if doctor has treated this patient
                    has_appointment = Appointment.query.filter_by(
                        doctor_id=doctor.id,
                        patient_id=patient_id
                    ).first()
                    
                    if not has_appointment:
                        return {'error': 'Unauthorized - no relationship with this patient'}, 403
                    
                    query = query.filter_by(patient_id=patient_id)
                else:
                    # Get all notes for doctor's patients
                    patient_ids = db.session.query(Appointment.patient_id).filter(
                        Appointment.doctor_id == doctor.id
                    ).distinct().all()
                    patient_ids = [pid[0] for pid in patient_ids]
                    query = query.filter(MedicalNote.patient_id.in_(patient_ids))
                
                notes = query.order_by(MedicalNote.created_at.desc()).all()
                
            elif current_user.has_role('patient'):
                patient = Patient.query.filter_by(user_id=current_user.id).first()
                if not patient:
                    return {'error': 'Patient profile not found'}, 404
                
                # Patient can only see their own non-private notes
                notes = MedicalNote.query.filter_by(
                    patient_id=patient.id,
                    is_private=False
                ).order_by(MedicalNote.created_at.desc()).all()
                
            elif current_user.has_role('admin'):
                # Admin can see all notes
                query = MedicalNote.query
                if patient_id:
                    query = query.filter_by(patient_id=patient_id)
                notes = query.order_by(MedicalNote.created_at.desc()).all()
            else:
                return {'error': 'Unauthorized'}, 403
            
            return [note.to_dict() for note in notes]
            
        except Exception as e:
            print(f"Error in MedicalNotesListResource GET: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': 'Failed to load medical notes'}, 500
    
    @auth_required()
    @roles_required('doctor')
    def post(self):
        """Create a new medical note - doctors only"""
        try:
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if not doctor:
                return {'error': 'Doctor profile not found'}, 404
            
            data = request.get_json()
            patient_id = data.get('patient_id')
            
            has_appointment = Appointment.query.filter_by(
                doctor_id=doctor.id,
                patient_id=patient_id
            ).first()
            
            if not has_appointment:
                return {'error': 'Can only add notes for your patients'}, 403
            
            note = MedicalNote(
                patient_id=patient_id,
                doctor_id=doctor.id,
                note_type=data.get('note_type', 'General'),
                title=data.get('title'),
                content=data.get('content'),
                is_private=data.get('is_private', False)
            )
            
            db.session.add(note)
            db.session.commit()
            
            return note.to_dict(), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in MedicalNotesListResource POST: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': 'Failed to create medical note'}, 500

class MedicalNoteResource(Resource):
    """Individual medical note operations"""
    
    @auth_required()
    def get(self, note_id):
        """Get a specific medical note"""
        try:
            note = MedicalNote.query.get_or_404(note_id)
            
            # Check authorization
            if current_user.has_role('doctor'):
                doctor = Doctor.query.filter_by(user_id=current_user.id).first()
                if note.doctor_id != doctor.id:
                    return {'error': 'Unauthorized'}, 403
                    
            elif current_user.has_role('patient'):
                patient = Patient.query.filter_by(user_id=current_user.id).first()
                if note.patient_id != patient.id or note.is_private:
                    return {'error': 'Unauthorized'}, 403
                    
            elif not current_user.has_role('admin'):
                return {'error': 'Unauthorized'}, 403
            
            return note.to_dict()
            
        except Exception as e:
            print(f"Error in MedicalNoteResource GET: {str(e)}")
            return {'error': 'Failed to load medical note'}, 500
    
    @auth_required()
    @roles_required('doctor')
    def put(self, note_id):
        """Update a medical note - only by the doctor who created it"""
        try:
            note = MedicalNote.query.get_or_404(note_id)
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            
            if note.doctor_id != doctor.id:
                return {'error': 'Can only edit your own notes'}, 403
            
            data = request.get_json()
            
            if 'note_type' in data:
                note.note_type = data['note_type']
            if 'title' in data:
                note.title = data['title']
            if 'content' in data:
                note.content = data['content']
            if 'is_private' in data:
                note.is_private = data['is_private']
            
            note.updated_at = datetime.utcnow()
            
            db.session.commit()
            return note.to_dict()
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in MedicalNoteResource PUT: {str(e)}")
            return {'error': 'Failed to update medical note'}, 500
    
    @auth_required()
    @roles_required('doctor')
    def delete(self, note_id):
        """Delete a medical note - only by the doctor who created it"""
        try:
            note = MedicalNote.query.get_or_404(note_id)
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            
            if note.doctor_id != doctor.id:
                return {'error': 'Can only delete your own notes'}, 403
            
            db.session.delete(note)
            db.session.commit()
            
            return {'message': 'Medical note deleted successfully'}
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in MedicalNoteResource DELETE: {str(e)}")
            return {'error': 'Failed to delete medical note'}, 500

class AppointmentListResource(Resource):
    @auth_required()
    def get(self):
        status = request.args.get('status')
        doctor_id = request.args.get('doctor_id')
        patient_id = request.args.get('patient_id')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Appointment.query
        
        # Apply filters based on user role
        if current_user.has_role('doctor'):
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if doctor:
                query = query.filter_by(doctor_id=doctor.id)
        elif current_user.has_role('patient'):
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if patient:
                query = query.filter_by(patient_id=patient.id)
        
        
        if status:
            query = query.filter_by(status=status)
        if doctor_id and current_user.has_role('admin'):
            query = query.filter_by(doctor_id=doctor_id)
        if patient_id and (current_user.has_role('admin') or current_user.has_role('doctor')):
            query = query.filter_by(patient_id=patient_id)
        if date_from:
            query = query.filter(Appointment.appointment_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(Appointment.appointment_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        
        appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
        return [appointment.to_dict() for appointment in appointments]
    
    @auth_required()
    def post(self):
        data = request.get_json()
        
        if current_user.has_role('patient'):
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if not patient:
                return {'error': 'Patient profile not found'}, 404
            data['patient_id'] = patient.id
        
        # Validate doctor availability
        doctor = Doctor.query.get(data.get('doctor_id'))
        if not doctor or not doctor.is_active:
            return {'error': 'Doctor not available'}, 400
        
        appointment_date = datetime.strptime(data.get('appointment_date'), '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data.get('appointment_time'), '%H:%M').time()
        
        if doctor.available_time_start and doctor.available_time_end:
            if not (doctor.available_time_start <= appointment_time <= doctor.available_time_end):
                return {'message': f'Appointment time must be between {doctor.available_time_start.strftime("%H:%M")} and {doctor.available_time_end.strftime("%H:%M")}'}, 400
        
        # Check for conflicting appointments
        existing = Appointment.query.filter_by(
            doctor_id=data.get('doctor_id'),
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='Booked'
        ).first()
        
        if existing:
            return {'error': 'This time slot is already booked'}, 400
        
        appointment = Appointment(
            patient_id=data.get('patient_id'),
            doctor_id=data.get('doctor_id'),
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=data.get('reason'),
            notes=data.get('notes'),
            status='Booked'
        )
        
        try:
            db.session.add(appointment)
            db.session.commit()
            # Clear dashboard cache for both doctor and patient
            CacheService.delete("dashboard_")
            return appointment.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

class AppointmentResource(Resource):
    @auth_required()
    def get(self, appointment_id):
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Check authorization
        if not (current_user.has_role('admin') or 
                (current_user.has_role('doctor') and appointment.doctor.user_id == current_user.id) or
                (current_user.has_role('patient') and appointment.patient.user_id == current_user.id)):
            return {'error': 'Unauthorized'}, 403
        
        return appointment.to_dict()
    
    @auth_required()
    def put(self, appointment_id):
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Check authorization
        if not (current_user.has_role('admin') or 
                (current_user.has_role('doctor') and appointment.doctor.user_id == current_user.id) or
                (current_user.has_role('patient') and appointment.patient.user_id == current_user.id)):
            return {'error': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        # If updating appointment time, validate it's within doctor's available time range
        if 'appointment_time' in data:
            appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
            doctor = appointment.doctor
            if doctor.available_time_start and doctor.available_time_end:
                if not (doctor.available_time_start <= appointment_time <= doctor.available_time_end):
                    return {'message': f'Appointment time must be between {doctor.available_time_start.strftime("%H:%M")} and {doctor.available_time_end.strftime("%H:%M")}'}, 400
            appointment.appointment_time = appointment_time
        
        # Update appointment fields
        if 'status' in data:
            appointment.status = data['status']
        if 'reason' in data:
            appointment.reason = data['reason']
        if 'notes' in data:
            appointment.notes = data['notes']
        if 'appointment_date' in data:
            appointment.appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        
        appointment.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            # Clear dashboard cache for both doctor and patient
            CacheService.delete("dashboard_")
            return appointment.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

    @auth_required()
    def delete(self, appointment_id):
        appointment = Appointment.query.get_or_404(appointment_id)

        # Check authorization
        if not (current_user.has_role('admin') or
                (current_user.has_role('doctor') and appointment.doctor.user_id == current_user.id) or
                (current_user.has_role('patient') and appointment.patient.user_id == current_user.id)):
            return {'error': 'Unauthorized'}, 403

        try:
            # If appointment has a treatment, delete it first
            if appointment.treatment:
                db.session.delete(appointment.treatment)

            db.session.delete(appointment)
            db.session.commit()
            CacheService.delete("dashboard_")
            return {'message': 'Appointment deleted successfully'}
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

class TreatmentResource(Resource):
    @auth_required()
    def get(self, appointment_id):
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Check authorization
        if not (current_user.has_role('admin') or 
                (current_user.has_role('doctor') and appointment.doctor.user_id == current_user.id) or
                (current_user.has_role('patient') and appointment.patient.user_id == current_user.id)):
            return {'error': 'Unauthorized'}, 403
        
        if appointment.treatment:
            return appointment.treatment.to_dict()
        else:
            return {'error': 'No treatment record found'}, 404
    
    @auth_required()
    def post(self, appointment_id):
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Only doctors can create treatment records
        if not (current_user.has_role('doctor') and appointment.doctor.user_id == current_user.id):
            return {'error': 'Unauthorized'}, 403
        
        # Check if treatment already exists
        if appointment.treatment:
            return {'error': 'Treatment record already exists'}, 400
        
        data = request.get_json()
        
        treatment = Treatment(
            appointment_id=appointment_id,
            diagnosis=data.get('diagnosis'),
            prescription=data.get('prescription'),
            treatment_notes=data.get('treatment_notes'),
            follow_up_required=data.get('follow_up_required', False),
            follow_up_date=datetime.strptime(data.get('follow_up_date'), '%Y-%m-%d').date() if data.get('follow_up_date') else None,
            cost=data.get('cost', 0.0)
        )
        
        # Mark appointment as completed
        appointment.status = 'Completed'
        appointment.updated_at = datetime.utcnow()
        
        try:
            db.session.add(treatment)
            db.session.commit()
            return treatment.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400
    
    def put(self, appointment_id):
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Only doctors can update treatment records
        if not (current_user.has_role('doctor') and appointment.doctor.user_id == current_user.id):
            return {'error': 'Unauthorized'}, 403
        
        if not appointment.treatment:
            return {'error': 'Treatment record not found'}, 404
        
        data = request.get_json()
        treatment = appointment.treatment
        
        # Update treatment fields
        for field in ['diagnosis', 'prescription', 'treatment_notes', 'follow_up_required', 'cost']:
            if field in data:
                setattr(treatment, field, data[field])
        
        if 'follow_up_date' in data and data['follow_up_date']:
            treatment.follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()
        
        treatment.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return treatment.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

class ExportResource(Resource):
    @auth_required()
    def post(self):
        data = request.get_json()
        export_type = data.get('type')
        
        if export_type == 'patient_treatments':
            # Only patients can export their own data or admin can export for any patient
            if current_user.has_role('patient'):
                patient = Patient.query.filter_by(user_id=current_user.id).first()
                if not patient:
                    return {'error': 'Patient profile not found'}, 404
                patient_id = patient.id
            elif current_user.has_role('admin'):
                patient_id = data.get('patient_id')
                if not patient_id:
                    return {'error': 'Patient ID required'}, 400
            else:
                return {'error': 'Unauthorized'}, 403
            
            task = export_patient_treatments_csv.delay(patient_id)
            return {
                'success': True,
                'message': 'Export started. You will receive an email when it\'s ready.',
                'task_id': task.id
            }
        
        elif export_type == 'doctor_report':
            if not (current_user.has_role('doctor') or current_user.has_role('admin')):
                return {'error': 'Unauthorized'}, 403
            
            if current_user.has_role('doctor'):
                doctor = Doctor.query.filter_by(user_id=current_user.id).first()
                if not doctor:
                    return {'error': 'Doctor profile not found'}, 404
                doctor_id = doctor.id
            else:
                doctor_id = data.get('doctor_id')
                if not doctor_id:
                    return {'error': 'Doctor ID required'}, 400
            
            month = data.get('month', datetime.now().month)
            year = data.get('year', datetime.now().year)
            
            # Start the background task
            task = send_doctor_monthly_report.apply_async(args=[doctor_id, year, month])
            return {
                'success': True,
                'message': 'Report generation started. You will receive an email when it\'s ready.',
                'task_id': task.id
            }
        
        else:
            return {'error': 'Invalid export type'}, 400

class SearchResource(Resource):
    @auth_required()
    def get(self):
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')  
        
        if not query:
            return {'error': 'Search query required'}, 400
        
        results = {}
        
        if search_type in ['all', 'doctors']:
            doctors = Doctor.query.join(User).filter(
                db.and_(
                    Doctor.is_active == True,
                    db.or_(
                        User.username.contains(query),
                        User.email.contains(query),
                        Doctor.specialization.contains(query)
                    )
                )
            ).limit(10).all()
            results['doctors'] = [doctor.to_dict() for doctor in doctors]
        
        if search_type in ['all', 'patients'] and (current_user.has_role('admin') or current_user.has_role('doctor')):
            patients = Patient.query.join(User).filter(
                db.and_(
                    Patient.is_active == True,
                    db.or_(
                        User.username.contains(query),
                        User.email.contains(query),
                        Patient.first_name.contains(query),
                        Patient.last_name.contains(query),
                        Patient.contact_number.contains(query)
                    )
                )
            ).limit(10).all()
            results['patients'] = [patient.to_dict() for patient in patients]
        
        if search_type in ['all', 'departments']:
            departments = Department.query.filter(
                db.or_(
                    Department.name.contains(query),
                    Department.description.contains(query)
                )
            ).limit(10).all()
            results['departments'] = [dept.to_dict() for dept in departments]
        
        return results


class DoctorAvailabilityListResource(Resource):
    """Doctor availability management - SIMPLIFIED"""
    
    @auth_required()
    def get(self):
        """Get doctor's availability slots"""
        try:
            if not current_user.has_role('doctor'):
                return {'error': 'Only doctors can access this'}, 403
            
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if not doctor:
                return {'error': 'Doctor profile not found'}, 404
            
            slots = DoctorAvailability.query.filter_by(doctor_id=doctor.id).order_by(
                DoctorAvailability.available_date, 
                DoctorAvailability.start_time
            ).all()
            
            return [slot.to_dict() for slot in slots]
            
        except Exception as e:
            print(f"Error in get availability: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': 'Server error'}, 500
    
    @auth_required()
    def post(self):
        """Create new availability slot - SIMPLIFIED"""
        try:
            if not current_user.has_role('doctor'):
                return {'error': 'Only doctors can add availability'}, 403
            
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if not doctor:
                return {'error': 'Doctor profile not found'}, 404
            
            data = request.get_json()
            
            if not data.get('date') or not data.get('start_time') or not data.get('end_time'):
                return {'error': 'Date, start time and end time are required'}, 400
            
        
            from datetime import datetime as dt
            
            availability = DoctorAvailability(
                doctor_id=doctor.id,
                available_date=dt.strptime(data['date'], '%Y-%m-%d').date(),
                start_time=dt.strptime(data['start_time'], '%H:%M').time(),
                end_time=dt.strptime(data['end_time'], '%H:%M').time(),
                max_appointments=int(data.get('max_appointments', 1)),
                is_available=bool(data.get('is_available', True))
            )
            
            db.session.add(availability)
            db.session.commit()
            
            return availability.to_dict(), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating availability: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': 'Failed to create slot'}, 500


class DoctorAvailabilityResource(Resource):
    """Individual doctor availability slot management"""
    
    @auth_required()
    def get(self, availability_id):
        """Get specific availability slot"""
        if not current_user.has_role('doctor'):
            return {'error': 'Unauthorized. Doctor access required.'}, 403
        
        try:
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if not doctor:
                return {'error': 'Doctor not found'}, 404
            
            availability = DoctorAvailability.query.filter_by(
                id=availability_id,
                doctor_id=doctor.id
            ).first()
            
            if not availability:
                return {'error': 'Availability slot not found'}, 404
            
            return availability.to_dict()
            
        except Exception as e:
            return {'error': f'Failed to get availability: {str(e)}'}, 500
    
    @auth_required()
    def put(self, availability_id):
        """Update availability slot - SIMPLIFIED"""
        try:
            if not current_user.has_role('doctor'):
                return {'error': 'Only doctors can update availability'}, 403
            
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if not doctor:
                return {'error': 'Doctor profile not found'}, 404
            
            availability = DoctorAvailability.query.filter_by(
                id=availability_id,
                doctor_id=doctor.id
            ).first()
            
            if not availability:
                return {'error': 'Slot not found'}, 404
            
            data = request.get_json()
            if not data:
                return {'error': 'No data provided'}, 400
            
            from datetime import datetime as dt
            
            if 'date' in data:
                availability.available_date = dt.strptime(data['date'], '%Y-%m-%d').date()
            
            if 'start_time' in data:
                availability.start_time = dt.strptime(data['start_time'], '%H:%M').time()
            
            if 'end_time' in data:
                availability.end_time = dt.strptime(data['end_time'], '%H:%M').time()
            
            if 'max_appointments' in data:
                availability.max_appointments = int(data['max_appointments'])
            
            if 'is_available' in data:
                availability.is_available = bool(data['is_available'])
            
            db.session.commit()
            
            return availability.to_dict()
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating availability: {str(e)}")
            return {'error': 'Failed to update slot'}, 500
    
    @auth_required()
    def delete(self, availability_id):
        """Delete availability slot - SIMPLIFIED"""
        try:
            if not current_user.has_role('doctor'):
                return {'error': 'Only doctors can delete availability'}, 403
            
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if not doctor:
                return {'error': 'Doctor profile not found'}, 404
            
            availability = DoctorAvailability.query.filter_by(
                id=availability_id,
                doctor_id=doctor.id
            ).first()
            
            if not availability:
                return {'error': 'Slot not found'}, 404
            
            db.session.delete(availability)
            db.session.commit()
            
            return {'message': 'Slot deleted successfully'}
            
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting availability: {str(e)}")
            return {'error': 'Failed to delete slot'}, 500


class PatientAvailabilityResource(Resource):
    """Patient view of doctor availability - SIMPLIFIED"""

    @auth_required()
    def get(self, doctor_id):
        """Get available slots for a specific doctor"""
        try:
            if not current_user.has_role('patient'):
                return {'error': 'Only patients can view availability'}, 403

            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                return {'error': 'Doctor not found'}, 404

            from datetime import datetime as dt
            today = dt.now().date()
            end_date = today + timedelta(days=30)

            availability_slots = DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doctor_id,
                DoctorAvailability.available_date >= today,
                DoctorAvailability.available_date <= end_date,
                DoctorAvailability.is_available == True
            ).order_by(DoctorAvailability.available_date, DoctorAvailability.start_time).all()

            # For each slot, check how many appointments are already booked
            available_slots = []
            for slot in availability_slots:
                booked_appointments = Appointment.query.filter(
                    Appointment.doctor_id == doctor_id,
                    Appointment.appointment_date == slot.available_date,
                    Appointment.appointment_time >= slot.start_time,
                    Appointment.appointment_time < slot.end_time,
                    Appointment.status != 'Cancelled'
                ).count()

                available_appointments = slot.max_appointments - booked_appointments

                if available_appointments > 0:
                    slot_data = slot.to_dict()
                    slot_data['available_appointments'] = available_appointments
                    slot_data['booked_appointments'] = booked_appointments
                    available_slots.append(slot_data)

            return {
                'doctor': doctor.to_dict(),
                'available_slots': available_slots
            }

        except Exception as e:
            print(f"Error getting patient availability: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': 'Failed to get availability'}, 500

class TriggerRemindersResource(Resource):
    """Manually trigger daily appointment reminders - Admin only"""

    @auth_required()
    @roles_required('admin')
    def post(self):
        """Manually trigger the daily reminders task"""
        try:
            from tasks import send_daily_reminders

            
            result = send_daily_reminders()

            return {
                'success': True,
                'message': 'Daily reminders triggered successfully',
                'result': result
            }

        except Exception as e:
            print(f"Error triggering reminders: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': f'Failed to trigger reminders: {str(e)}'}, 500







