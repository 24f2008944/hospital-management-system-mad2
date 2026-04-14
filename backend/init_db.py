# backend/init_db.py

from app import app, db, user_datastore
from models import User, Role, Department, Doctor, Patient, Appointment, Treatment
from flask_security import hash_password

def init_database():
    """Initialize the database with default data"""
    with app.app_context():
        # Create all tables
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
            print("Created admin user: admin@hospital.com / admin123")
            
        # Create sample departments
        if not Department.query.first():
            departments = [
                Department(name='Cardiology', description='Heart and cardiovascular system'),
                Department(name='Neurology', description='Nervous system and brain'),
                Department(name='Orthopedics', description='Bones, joints, and muscles'),
                Department(name='Pediatrics', description='Medical care for children'),
                Department(name='General Medicine', description='General medical care'),
                Department(name='Dermatology', description='Skin, hair, and nail disorders'),
                Department(name='Gynecology', description='Women\'s reproductive health'),
                Department(name='ENT', description='Ear, Nose, and Throat'),
            ]
            for dept in departments:
                db.session.add(dept)
            print("Created sample departments")
        
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()
