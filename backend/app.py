# backend/app.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password
from flask_mail import Mail
from celery import Celery
import redis
import os
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__)
    
    
    app.config['SECRET_KEY'] = 'a-very-secret-and-secure-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'hospital.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Flask-Security-Too Configurations
    app.config['SECURITY_PASSWORD_SALT'] = 'another-very-secret-salt'
    app.config['SECURITY_REGISTERABLE'] = True 
    app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
    app.config['SECURITY_UNAUTHORIZED_VIEW'] = None 
    app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = [{'email': {'mapper': 'email', 'case_insensitive': True}}]
    app.config['SECURITY_TRACKABLE'] = True
    app.config['SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Redis Configuration
    app.config['REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/1'
    
    # Celery Configuration
    app.config['broker_url'] = 'redis://localhost:6379/0'
    app.config['result_backend'] = 'redis://localhost:6379/0'
    
    # Mail Configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    
    return app

app = create_app()


from models import db  
db.init_app(app)
migrate = Migrate(app, db)
cors = CORS(app, supports_credentials=True)
api = Api(app, prefix="/api")
mail = Mail(app)

# Redis Cache
try:
    cache = redis.Redis.from_url(app.config['CACHE_REDIS_URL'])
except:
    cache = None

from models import User, Role, Department, Doctor, Patient, Appointment, Treatment, MedicalNote


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

def register_routes():
    """Register all API routes"""
    from resources import (
        DepartmentListResource, DepartmentResource,
        DoctorListResource, DoctorResource,
        PatientListResource, PatientResource,
        AppointmentListResource, AppointmentResource,
        TreatmentResource, AuthResource, DashboardResource,
        ExportResource, SearchResource,
        DoctorAvailabilityListResource, DoctorAvailabilityResource,
        PatientAvailabilityResource, DoctorPatientsResource,
        PatientAppointmentsResource, PatientTreatmentsResource,
        MedicalNotesListResource, MedicalNoteResource,
        PatientOwnAppointmentsResource, PatientOwnTreatmentsResource, TriggerRemindersResource,
        PatientTreatmentHistoryResource, BlacklistedDoctorsResource, BlacklistedPatientsResource,
        UnblockDoctorResource, UnblockPatientResource
    )
    
    # --- API Resource Routing ---
    api.add_resource(AuthResource, '/auth')
    api.add_resource(DashboardResource, '/dashboard')
    api.add_resource(DepartmentListResource, '/departments')
    api.add_resource(DepartmentResource, '/departments/<int:dept_id>')
    api.add_resource(DoctorListResource, '/doctors')
    api.add_resource(DoctorResource, '/doctors/<int:doctor_id>')
    api.add_resource(PatientListResource, '/patients')
    api.add_resource(PatientResource, '/patients/<int:patient_id>')
    api.add_resource(BlacklistedDoctorsResource, '/blacklisted-doctors')
    api.add_resource(BlacklistedPatientsResource, '/blacklisted-patients')
    api.add_resource(UnblockDoctorResource, '/doctors/<int:doctor_id>/unblock')
    api.add_resource(UnblockPatientResource, '/patients/<int:patient_id>/unblock')
    api.add_resource(AppointmentListResource, '/appointments')
    api.add_resource(AppointmentResource, '/appointments/<int:appointment_id>')
    api.add_resource(TreatmentResource, '/treatments/<int:appointment_id>')
    api.add_resource(ExportResource, '/export')
    api.add_resource(SearchResource, '/search')
    api.add_resource(DoctorAvailabilityListResource, '/doctor-availability')
    api.add_resource(DoctorAvailabilityResource, '/doctor-availability/<int:availability_id>')
    api.add_resource(PatientAvailabilityResource, '/doctors/<int:doctor_id>/availability')
    api.add_resource(DoctorPatientsResource, '/doctor/patients')
    api.add_resource(PatientAppointmentsResource, '/patients/<int:patient_id>/appointments')
    api.add_resource(PatientTreatmentsResource, '/patients/<int:patient_id>/treatments')
    api.add_resource(MedicalNotesListResource, '/medical-notes')
    api.add_resource(MedicalNoteResource, '/medical-notes/<int:note_id>')
    api.add_resource(PatientOwnAppointmentsResource, '/patient/appointments')
    
    from resources import PatientDashboardDepartmentsResource
    api.add_resource(PatientDashboardDepartmentsResource, '/patient_dashboard_departments')
    api.add_resource(PatientOwnTreatmentsResource, '/patient/treatments')
    api.add_resource(PatientTreatmentHistoryResource, '/patient/treatments')
    api.add_resource(TriggerRemindersResource, '/trigger-reminders')

@app.route('/')
def index():
    return "<h1>Hospital Management Backend</h1>"

# This function creates roles and the admin user programmatically
def create_roles_and_admin():
    with app.app_context():
        db.create_all()
        
        # Create roles
        admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
        doctor_role = user_datastore.find_or_create_role(name='doctor', description='Doctor')
        patient_role = user_datastore.find_or_create_role(name='patient', description='Patient')
        
        # Create admin user if one doesn't exist
        if not user_datastore.find_user(email='admin@hospital.com'):
            admin_user = user_datastore.create_user(
                email='admin@hospital.com', 
                username='admin', 
                password=hash_password('admin123'),
                active=True,
                roles=[admin_role]
            )
            
        # Create sample departments
        if not Department.query.first():
            departments = [
                Department(name='Cardiology', description='Heart and cardiovascular system'),
                Department(name='Neurology', description='Nervous system and brain'),
                Department(name='Orthopedics', description='Bones, joints, and muscles'),
                Department(name='Pediatrics', description='Medical care for children'),
                Department(name='General Medicine', description='General medical care'),
            ]
            for dept in departments:
                db.session.add(dept)
        
        db.session.commit()


from celery_app import celery as celery_instance
celery = celery_instance
celery.conf.update(
    broker_url=app.config['broker_url'],
    result_backend=app.config['result_backend']
)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

register_routes()
create_roles_and_admin()

import tasks
from tasks import mail_api, report_api
app.register_blueprint(mail_api)
app.register_blueprint(report_api)

if __name__ == '__main__':
    app.run(debug=True)