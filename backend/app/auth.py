from flask import jsonify, request, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from .models import User, db

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            
            auth_header = request.headers.get('Authorization', '')
            current_app.logger.info(f'Authorization header: {auth_header[:50] if auth_header else "MISSING"}')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                current_app.logger.error('Missing or invalid Authorization header')
                return jsonify({'message': 'Missing or invalid Authorization header!', 'header': auth_header}), 401
            
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            current_app.logger.info(f'JWT verified, user_id: {user_id}')
            
            
            user_id = int(user_id) if user_id else None
            current_user = User.query.get(user_id)
            
            if not current_user or not current_user.is_active:
                current_app.logger.error(f'User not found or inactive: {user_id}')
                return jsonify({'message': 'Token is invalid!'}), 401
                
        except Exception as e:
            current_app.logger.error(f'JWT verification error: {str(e)}')
            import traceback
            current_app.logger.error(traceback.format_exc())
            return jsonify({'message': 'Token is invalid or expired!', 'error': str(e)}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def doctor_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'doctor':
            return jsonify({'message': 'Doctor access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def patient_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'patient':
            return jsonify({'message': 'Patient access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated