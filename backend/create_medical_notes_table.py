from app import app, db
from models import MedicalNote

with app.app_context():
    db.create_all()
    print('✅ MedicalNote table created successfully!')
