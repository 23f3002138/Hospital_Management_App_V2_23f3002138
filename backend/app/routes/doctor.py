from flask import Blueprint, request, jsonify
from ..models import db, User, Doctor, Patient, Appointment, Treatment, DoctorAvailability
from ..auth import token_required, doctor_required
from datetime import datetime, timedelta
import redis

doctor_bp = Blueprint('doctor', __name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)



@doctor_bp.route('/dashboard', methods=['GET'])
@token_required
@doctor_required
def doctor_dashboard(current_user):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        return jsonify({'message': 'Doctor profile not found!'}), 404
    
    cache_key = f'doctor_dashboard_{doctor.id}'
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        import json
        return jsonify(json.loads(cached_data))
    
    today = datetime.today().date()
    
    
    today_appointments = Appointment.query.filter_by(
        doctor_id=doctor.id,
        appointment_date=today
    ).order_by(Appointment.appointment_time).all()
    
    
    next_week = today + timedelta(days=7)
    upcoming_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= today,
        Appointment.appointment_date <= next_week,
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    
    
    patient_count = db.session.query(db.func.count(db.distinct(Appointment.patient_id))).filter_by(doctor_id=doctor.id).scalar()
    
    dashboard_data = {
        'doctor': doctor.to_dict(),
        'today_appointments': [appt.to_dict() for appt in today_appointments],
        'upcoming_appointments': [appt.to_dict() for appt in upcoming_appointments],
        'stats': {
            'today_appointments_count': len(today_appointments),
            'upcoming_appointments_count': len(upcoming_appointments),
            'total_patients': patient_count
        }
    }
    
    
    import json
    redis_client.setex(cache_key, 120, json.dumps(dashboard_data))
    
    return jsonify(dashboard_data)

@doctor_bp.route('/appointments', methods=['GET'])
@token_required
@doctor_required
def get_doctor_appointments(current_user):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        return jsonify({'message': 'Doctor profile not found!'}), 404
    
    status = request.args.get('status')
    date = request.args.get('date')
    
    query = Appointment.query.filter_by(doctor_id=doctor.id)
    
    if status:
        query = query.filter_by(status=status)
    if date:
        query = query.filter_by(appointment_date=datetime.strptime(date, '%Y-%m-%d').date())
    
    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    
    return jsonify({'appointments': [appt.to_dict() for appt in appointments]})

@doctor_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@token_required
@doctor_required
def cancel_appointment(current_user, appointment_id):
    """Cancel an appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if appointment.doctor_id != doctor.id:
        return jsonify({'message': 'Access denied!'}), 403
    
    if appointment.status != 'scheduled':
        return jsonify({'message': 'Only scheduled appointments can be cancelled!'}), 400
    
    try:
        appointment.status = 'cancelled'
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        
        redis_client.delete(f'doctor_dashboard_{doctor.id}')
        redis_client.delete(f'patient_dashboard_{appointment.patient_id}')
        redis_client.delete('admin_dashboard')
        
        return jsonify({
            'message': 'Appointment cancelled successfully!',
            'appointment': appointment.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to cancel appointment!', 'error': str(e)}), 500

@doctor_bp.route('/availability', methods=['POST'])
@token_required
@doctor_required
def set_availability(current_user):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        return jsonify({'message': 'Doctor profile not found!'}), 404
    
    data = request.get_json()
    
    required_fields = ['date', 'start_time', 'end_time']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'{field} is required!'}), 400
    
    try:
        availability = DoctorAvailability(
            doctor_id=doctor.id,
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M').time()
        )
        
        db.session.add(availability)
        db.session.commit()
        
        return jsonify({
            'message': 'Availability set successfully!',
            'availability': availability.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to set availability!', 'error': str(e)}), 500

@doctor_bp.route('/patients', methods=['GET'])
@token_required
@doctor_required
def get_doctor_patients(current_user):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        return jsonify({'message': 'Doctor profile not found!'}), 404
    
    
    patient_ids = db.session.query(Appointment.patient_id).filter_by(doctor_id=doctor.id).distinct().all()
    patient_ids = [pid[0] for pid in patient_ids]
    
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
    
    return jsonify({'patients': [patient.to_dict() for patient in patients]})

@doctor_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@token_required
@doctor_required
def get_patient_history(current_user, patient_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        return jsonify({'message': 'Doctor profile not found!'}), 404
    
    
    appointments = Appointment.query.filter_by(
        doctor_id=doctor.id,
        patient_id=patient_id
    ).order_by(Appointment.appointment_date.desc()).all()
    
    history = []
    for appt in appointments:
        appt_data = appt.to_dict()
        if appt.treatment:
            appt_data['treatment'] = appt.treatment.to_dict()
        history.append(appt_data)
    
    return jsonify({'history': history})

@doctor_bp.route('/availability', methods=['GET'])
@token_required
@doctor_required
def get_availability(current_user):
    """Get doctor's availability"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        return jsonify({'message': 'Doctor profile not found!'}), 404
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = datetime.today().date().isoformat()
    if not end_date:
        end_date = (datetime.today() + timedelta(days=7)).date().isoformat()
    
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
        DoctorAvailability.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
    ).order_by(DoctorAvailability.date, DoctorAvailability.start_time).all()
    
    return jsonify({
        'availabilities': [avail.to_dict() for avail in availabilities]
    })

@doctor_bp.route('/availability/<int:availability_id>', methods=['DELETE'])
@token_required
@doctor_required
def delete_availability(current_user, availability_id):
    """Delete an availability slot"""
    availability = DoctorAvailability.query.get_or_404(availability_id)
    
    
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if availability.doctor_id != doctor.id:
        return jsonify({'message': 'Access denied!'}), 403
    
    try:
        db.session.delete(availability)
        db.session.commit()
        
        return jsonify({'message': 'Availability deleted successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete availability!', 'error': str(e)}), 500

@doctor_bp.route('/availability/batch', methods=['POST'])
@token_required
@doctor_required
def set_availability_batch(current_user):
    """Set availability for multiple time slots"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        return jsonify({'message': 'Doctor profile not found!'}), 404
    
    data = request.get_json()
    slots = data.get('slots', [])
    
    if not slots:
        return jsonify({'message': 'No time slots provided!'}), 400
    
    try:
        for slot in slots:
            
            existing = DoctorAvailability.query.filter_by(
                doctor_id=doctor.id,
                date=datetime.strptime(slot['date'], '%Y-%m-%d').date(),
                start_time=datetime.strptime(slot['start_time'], '%H:%M').time(),
                end_time=datetime.strptime(slot['end_time'], '%H:%M').time()
            ).first()
            
            if not existing:
                availability = DoctorAvailability(
                    doctor_id=doctor.id,
                    date=datetime.strptime(slot['date'], '%Y-%m-%d').date(),
                    start_time=datetime.strptime(slot['start_time'], '%H:%M').time(),
                    end_time=datetime.strptime(slot['end_time'], '%H:%M').time(),
                    is_available=slot.get('is_available', True)
                )
                db.session.add(availability)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Availability set for {len(slots)} time slots!'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to set availability!', 'error': str(e)}), 500

@doctor_bp.route('/appointments/<int:appointment_id>/treatment', methods=['POST'])
@token_required
@doctor_required
def add_treatment(current_user, appointment_id):
    """Add or update treatment details for an appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if appointment.doctor_id != doctor.id:
        return jsonify({'message': 'Access denied!'}), 403
    
    data = request.get_json()
    
    if not data.get('diagnosis'):
        return jsonify({'message': 'Diagnosis is required!'}), 400
    
    try:
        
        appointment.status = 'completed'
        appointment.updated_at = datetime.utcnow()
        
        
        treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()
        if not treatment:
            treatment = Treatment(appointment_id=appointment_id)
            db.session.add(treatment)
        
        treatment.diagnosis = data['diagnosis']
        treatment.prescription = data.get('prescription', '')
        treatment.notes = data.get('notes', '')
        treatment.follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date() if data.get('follow_up_date') else None
        
        db.session.commit()
        
        
        redis_client.delete(f'doctor_dashboard_{doctor.id}')
        redis_client.delete(f'patient_dashboard_{appointment.patient_id}')
        redis_client.delete('admin_dashboard')
        
        return jsonify({
            'message': 'Treatment details saved successfully!',
            'treatment': treatment.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to save treatment details!', 'error': str(e)}), 500

@doctor_bp.route('/patients/<int:patient_id>/full-history', methods=['GET'])
@token_required
@doctor_required
def get_patient_full_history(current_user, patient_id):
    """Get complete treatment history of a patient (across all doctors)"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        return jsonify({'message': 'Doctor profile not found!'}), 404
    
    
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        status='completed'
    ).order_by(Appointment.appointment_date.desc()).all()
    
    history = []
    for appt in appointments:
        appt_data = appt.to_dict()
        if appt.treatment:
            appt_data['treatment'] = appt.treatment.to_dict()
        history.append(appt_data)
    
    return jsonify({
        'patient_history': history,
        'total_records': len(history)
    })