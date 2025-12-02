from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
from ..models import db, User, Doctor, Patient, Department, Appointment
from ..auth import token_required
import redis

common_bp = Blueprint('common', __name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@common_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required!'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401
    
    if not user.is_active:
        return jsonify({'message': 'Account is deactivated!'}), 401
    
    
    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(hours=24),
        additional_claims={
            'username': user.username,
            'role': user.role,
            'user_id': user.id
        }
    )
    
    user_data = user.to_dict()
    if user.role == 'doctor' and user.doctor_profile:
        user_data.update(user.doctor_profile.to_dict())
    elif user.role == 'patient' and user.patient_profile:
        user_data.update(user.patient_profile.to_dict())
    
    return jsonify({
        'access_token': access_token,
        'user': user_data
    }), 200

@common_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 
                      'date_of_birth', 'gender', 'phone']
    
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'{field} is required!'}), 400
    
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists!'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists!'}), 400
    
    try:
        
        user = User(
            username=data['username'],
            email=data['email'],
            role='patient'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  
        
        
        patient = Patient(
            user_id=user.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            gender=data['gender'],
            phone=data['phone'],
            address=data.get('address', ''),
            emergency_contact=data.get('emergency_contact', ''),
            blood_group=data.get('blood_group', '')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24),
            additional_claims={
                'username': user.username,
                'role': user.role,
                'user_id': user.id
            }
        )
        
        user_data = user.to_dict()
        user_data.update(patient.to_dict())
        
        return jsonify({
            'access_token': access_token,
            'user': user_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed!', 'error': str(e)}), 500

@common_bp.route('/departments', methods=['GET'])
def get_departments():
    
    cache_key = 'departments_list'
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        import json
        return jsonify({'departments': json.loads(cached_data)})
    
    departments = Department.query.all()
    departments_data = [dept.to_dict() for dept in departments]
    
    
    import json
    redis_client.setex(cache_key, 3600, json.dumps(departments_data))
    
    return jsonify({'departments': departments_data})

@common_bp.route('/doctors', methods=['GET'])
def get_doctors():
    specialization = request.args.get('specialization')
    department_id = request.args.get('department_id')
    
    cache_key = f'doctors_list_{specialization}_{department_id}'
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        import json
        return jsonify({'doctors': json.loads(cached_data)})
    
    query = Doctor.query.filter_by(is_available=True)
    
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
    if department_id:
        query = query.filter_by(department_id=department_id)
    
    doctors = query.all()
    doctors_data = [doctor.to_dict() for doctor in doctors]
    
    
    import json
    redis_client.setex(cache_key, 1800, json.dumps(doctors_data))
    
    return jsonify({'doctors': doctors_data})

@common_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')  
    
    if not query:
        return jsonify({'message': 'Search query is required!'}), 400
    
    results = {}
    
    if search_type in ['all', 'doctors']:
        doctors = Doctor.query.filter(
            (Doctor.first_name.ilike(f'%{query}%')) |
            (Doctor.last_name.ilike(f'%{query}%')) |
            (Doctor.specialization.ilike(f'%{query}%'))
        ).all()
        results['doctors'] = [doctor.to_dict() for doctor in doctors]
    
    if search_type in ['all', 'patients']:
        patients = Patient.query.filter(
            (Patient.first_name.ilike(f'%{query}%')) |
            (Patient.last_name.ilike(f'%{query}%')) |
            (Patient.phone.ilike(f'%{query}%'))
        ).all()
        results['patients'] = [patient.to_dict() for patient in patients]
    
    return jsonify(results)