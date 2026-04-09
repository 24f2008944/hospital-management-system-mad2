from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
import os

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

def create_app():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    frontend_dir = os.path.join(BASE_DIR, 'frontend')
    
    app = Flask(__name__,
                static_folder=os.path.join(frontend_dir, 'static'),
                static_url_path='/static')

    app.config['SECRET_KEY'] = 'hms-secret-key-2024-unique'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'hms.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-hms-secret-2024'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_DEBUG'] = True

    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    from backend.routes.auth import auth_bp
    from backend.routes.admin import admin_bp
    from backend.routes.doctor import doctor_bp
    from backend.routes.patient import patient_bp
    from backend.routes.appointment import appointment_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(appointment_bp, url_prefix='/api/appointment')

    @app.route('/')
    def index():
        return send_from_directory(frontend_dir, 'index.html')

    with app.app_context():
        os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)
        db.create_all()
        seed_data()

    return app


def seed_data():
    from backend.models.user import User, Department
    from werkzeug.security import generate_password_hash

    if not User.query.filter_by(role='admin').first():
        admin = User(
            username='admin', email='admin@hospital.com',
            password_hash=generate_password_hash('admin123'),
            role='admin', full_name='System Administrator', is_active=True
        )
        db.session.add(admin)

    departments = [
        ('Cardiology', 'Heart and cardiovascular diseases'),
        ('Neurology', 'Brain, spinal cord, and nervous system'),
        ('Orthopedics', 'Bones, joints, and musculoskeletal system'),
        ('Pediatrics', 'Medical care for infants and children'),
        ('Dermatology', 'Skin, hair, and nail conditions'),
        ('Ophthalmology', 'Eye diseases and disorders'),
        ('ENT', 'Ear, nose, and throat conditions'),
        ('Gynecology', "Women's reproductive health"),
        ('Oncology', 'Cancer diagnosis and treatment'),
        ('Psychiatry', 'Mental health disorders'),
    ]
    for name, desc in departments:
        if not Department.query.filter_by(name=name).first():
            db.session.add(Department(name=name, description=desc))

    db.session.commit()
