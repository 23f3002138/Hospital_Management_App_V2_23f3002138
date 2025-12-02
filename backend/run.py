import os
import sys
import redis


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS


app = Flask(__name__)


from config import Config
app.config.from_object(Config)


from app.models import db, bcrypt


db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

CORS(app, 
     resources={r"/api/*": {
         "origins": "*",
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"]
     }})


from app.models import User, Doctor, Patient, Department, Appointment, Treatment, DoctorAvailability


from app.routes.common import common_bp
from app.routes.admin import admin_bp
from app.routes.doctor import doctor_bp
from app.routes.patient import patient_bp

app.register_blueprint(common_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
app.register_blueprint(patient_bp, url_prefix='/api/patient')


from app.tasks import init_celery
celery = init_celery(app)

app.config['CELERY'] = celery

def create_initial_data():
    """Create initial admin user and departments"""
    
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hospital.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("Created admin user: admin / admin123")
    
    
    departments = [
        ('Cardiology', 'Heart and cardiovascular diseases'),
        ('Neurology', 'Brain and nervous system disorders'),
        ('Orthopedics', 'Bones and joints treatment'),
        ('Pediatrics', 'Medical care for children'),
        ('Dermatology', 'Skin diseases and treatments'),
    ]
    
    for dept_name, dept_desc in departments:
        department = Department.query.filter_by(name=dept_name).first()
        if not department:
            department = Department(name=dept_name, description=dept_desc)
            db.session.add(department)
            print(f"Created department: {dept_name}")
    
    db.session.commit()

if __name__ == '__main__':
    
    instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
    
    with app.app_context():
        
        # Clear Redis cache on startup
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.flushall()
            print("Redis cache cleared successfully")
        except Exception as e:
            print(f"Warning: Failed to clear Redis cache: {e}")

        db.create_all()
        create_initial_data()
        
    
    
    print("Starting Flask server on http://localhost:5000")
    app.run(debug=True, port=5000)