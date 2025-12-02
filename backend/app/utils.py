import re
from datetime import datetime, date
from flask import jsonify
import jwt
from .models import User

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def validate_date(date_string):
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_time(time_string):
    """Validate time format (HH:MM)"""
    try:
        datetime.strptime(time_string, '%H:%M')
        return True
    except ValueError:
        return False

def calculate_age(birth_date):
    """Calculate age from birth date"""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def format_response(message, data=None, status=200):
    """Standard response formatter"""
    response = {
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status

def error_response(message, status=400):
    """Standard error response formatter"""
    return format_response(message, None, status)

def get_user_from_token(token):
    """Extract user from JWT token"""
    try:
        from backend import create_app
        app = create_app()
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return User.query.get(payload['user_id'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
        return None

def generate_time_slots(start_time, end_time, duration_minutes=30):
    """Generate time slots between start and end time"""
    from datetime import timedelta
    slots = []
    current_time = datetime.strptime(start_time, '%H:%M')
    end_time_dt = datetime.strptime(end_time, '%H:%M')
    
    while current_time < end_time_dt:
        slots.append(current_time.strftime('%H:%M'))
        current_time = current_time + timedelta(minutes=duration_minutes)
    
    return slots

def is_valid_appointment_time(appointment_time, doctor_availabilities):
    """Check if appointment time is within doctor's available slots"""
    appointment_dt = datetime.strptime(appointment_time, '%H:%M').time()
    
    for availability in doctor_availabilities:
        if availability.start_time <= appointment_dt <= availability.end_time:
            return True
    return False

def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return text
    
    sanitized = re.sub(r'[<>&\"\']', '', str(text))
    return sanitized.strip()

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"

def get_upcoming_dates(days=7):
    """Get list of upcoming dates"""
    from datetime import timedelta
    today = date.today()
    return [today + timedelta(days=i) for i in range(days)]

def is_weekend(date_obj):
    """Check if date is weekend"""
    return date_obj.weekday() >= 5  

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is strong"