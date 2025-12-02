from flask import Blueprint, request, jsonify, current_app
from ..models import db, User, Doctor, Patient, Appointment, Treatment, DoctorAvailability
from ..auth import token_required, patient_required
from datetime import datetime, timedelta
import redis

patient_bp = Blueprint('patient', __name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)




@patient_bp.route('/dashboard', methods=['GET'])
@token_required
@patient_required
def patient_dashboard(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if not patient:
        return jsonify({'message': 'Patient profile not found!'}), 404
    
    cache_key = f'patient_dashboard_{patient.id}'
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        import json
        return jsonify(json.loads(cached_data))
    
    today = datetime.today().date()
    
    
    upcoming_appointments = Appointment.query.filter_by(
        patient_id=patient.id
    ).filter(
        Appointment.appointment_date >= today,
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    
    
    past_appointments = Appointment.query.filter_by(
        patient_id=patient.id
    ).filter(
        Appointment.appointment_date < today,
        Appointment.status == 'completed'
    ).order_by(Appointment.appointment_date.desc()).limit(10).all()
    
    dashboard_data = {
        'patient': patient.to_dict(),
        'upcoming_appointments': [appt.to_dict() for appt in upcoming_appointments],
        'past_appointments': []
    }
    
    for appt in past_appointments:
        appt_data = appt.to_dict()
        if appt.treatment:
            appt_data['treatment'] = appt.treatment.to_dict()
        dashboard_data['past_appointments'].append(appt_data)
    
    
    import json
    redis_client.setex(cache_key, 120, json.dumps(dashboard_data))
    
    return jsonify(dashboard_data)

@patient_bp.route('/appointments', methods=['POST'])
@token_required
@patient_required
def book_appointment(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if not patient:
        return jsonify({'message': 'Patient profile not found!'}), 404
    
    data = request.get_json()
    
    required_fields = ['doctor_id', 'appointment_date', 'appointment_time', 'reason']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'{field} is required!'}), 400
    
    
    doctor = Doctor.query.get(data['doctor_id'])
    if not doctor or not doctor.is_available:
        return jsonify({'message': 'Doctor is not available!'}), 400
    
    appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
    appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
    
    
    # Load all scheduled appointments for the doctor on that date and compare times in HH:MM format
    scheduled_appts = Appointment.query.filter_by(
        doctor_id=data['doctor_id'],
        appointment_date=appointment_date,
        status='scheduled'
    ).all()

    requested_time_str = appointment_time.strftime('%H:%M')
    for appt in scheduled_appts:
        if appt.appointment_time.strftime('%H:%M') == requested_time_str:
            return jsonify({'message': 'Time slot is already booked!'}), 400

    # Ensure the requested time falls within an available DoctorAvailability slot for that date
    # cast doctor_id to int to avoid type mismatch
    try:
        doc_id = int(data['doctor_id'])
    except Exception:
        return jsonify({'message': 'Invalid doctor_id'}), 400

    avail_slots = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doc_id,
        DoctorAvailability.date == appointment_date,
        DoctorAvailability.is_available == True
    ).all()

    slot_ok = False
    for avail in avail_slots:
        # avail.start_time and avail.end_time are time objects
        if avail.start_time <= appointment_time < avail.end_time:
            slot_ok = True
            break

    if not slot_ok:
        return jsonify({'message': 'Requested time is not covered by doctor availability!'}), 400
    
    try:
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doc_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=data['reason'],
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Build response payload before any non-essential operations
        appointment_payload = {
            'message': 'Appointment booked successfully!',
            'appointment': appointment.to_dict()
        }

        # Safe cache/redis invalidation
        try:
            redis_client.delete(f'patient_dashboard_{patient.id}')
            redis_client.delete(f'doctor_dashboard_{doc_id}')
            redis_client.delete('admin_dashboard')
        except Exception as cache_err:
            current_app.logger.error(f'Failed to clear cache after booking: {cache_err}')
        
        return jsonify(appointment_payload), 201
        
    except Exception as e:
        # If an error happens here, it's a true failure — rollback and return 500
        db.session.rollback()
        current_app.logger.error(f'Failed to create appointment: {e}')
        return jsonify({'message': 'Failed to book appointment!', 'error': str(e)}), 500

@patient_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@token_required
@patient_required
def cancel_appointment(current_user, appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if appointment.patient_id != patient.id:
        return jsonify({'message': 'Access denied!'}), 403
    
    if appointment.status != 'scheduled':
        return jsonify({'message': 'Only scheduled appointments can be cancelled!'}), 400
    
    try:
        appointment.status = 'cancelled'
        appointment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        
        try:
            redis_client.delete(f'patient_dashboard_{patient.id}')
            redis_client.delete(f'doctor_dashboard_{appointment.doctor_id}')
            redis_client.delete('admin_dashboard')
        except Exception as e:
            current_app.logger.error(f"Cache clearing failed: {e}")
        
        return jsonify({
            'message': 'Appointment cancelled successfully!',
            'appointment': appointment.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to cancel appointment!', 'error': str(e)}), 500

@patient_bp.route('/appointments', methods=['GET'])
@token_required
@patient_required
def get_patient_appointments(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if not patient:
        return jsonify({'message': 'Patient profile not found!'}), 404
    
    status = request.args.get('status')
    
    query = Appointment.query.filter_by(patient_id=patient.id)
    
    if status:
        query = query.filter_by(status=status)
    
    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    
    appointments_data = []
    for appt in appointments:
        appt_data = appt.to_dict()
        if appt.treatment:
            appt_data['treatment'] = appt.treatment.to_dict()
        appointments_data.append(appt_data)
    
    return jsonify({'appointments': appointments_data})

@patient_bp.route('/profile', methods=['PUT'])
@token_required
@patient_required
def update_profile(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if not patient:
        return jsonify({'message': 'Patient profile not found!'}), 404
    
    data = request.get_json()
    
    if 'first_name' in data:
        patient.first_name = data['first_name']
    if 'last_name' in data:
        patient.last_name = data['last_name']
    if 'phone' in data:
        patient.phone = data['phone']
    if 'address' in data:
        patient.address = data['address']
    if 'emergency_contact' in data:
        patient.emergency_contact = data['emergency_contact']
    if 'blood_group' in data:
        patient.blood_group = data['blood_group']
    
    try:
        db.session.commit()
        
        
        redis_client.delete(f'patient_dashboard_{patient.id}')
        
        return jsonify({
            'message': 'Profile updated successfully!',
            'patient': patient.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile!', 'error': str(e)}), 500

@patient_bp.route('/treatment-history', methods=['GET'])
@token_required
@patient_required
def get_treatment_history(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if not patient:
        return jsonify({'message': 'Patient profile not found!'}), 404
    
    appointments = Appointment.query.filter_by(
        patient_id=patient.id,
        status='completed'
    ).order_by(Appointment.appointment_date.desc()).all()
    
    history = []
    for appt in appointments:
        if appt.treatment:
            treatment_data = appt.treatment.to_dict()
            treatment_data['doctor_name'] = appt.doctor.full_name
            treatment_data['appointment_date'] = appt.appointment_date.isoformat()
            history.append(treatment_data)
    
    return jsonify({'treatment_history': history})

@patient_bp.route('/export-treatment-history', methods=['POST'])
@token_required
@patient_required
def trigger_export_treatment_history(current_user):
    """Trigger CSV export of treatment history"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if not patient:
        return jsonify({'message': 'Patient profile not found!'}), 404
    
    data = request.get_json()
    email = data.get('email', current_user.email)
    
    try:
        
        celery = current_app.config.get('CELERY')
        
        if celery:
            
            task = celery.send_task('app.tasks.export_patient_treatment_history', args=[patient.id, email])
            return jsonify({
                'message': 'Export started! You will receive an email with the CSV file when it is ready.',
                'task_id': task.id
            }), 202
        else:
            
            from ..tasks import export_patient_treatment_history
            result = export_patient_treatment_history(patient.id, email)
            return jsonify({
                'message': 'Export completed! Check your email for the CSV file.',
                'result': result
            }), 200
        
    except Exception as e:
        
        try:
            from ..tasks import export_patient_treatment_history
            result = export_patient_treatment_history(patient.id, email)
            return jsonify({
                'message': 'Export completed! Check your email for the CSV file.',
                'result': result
            }), 200
        except Exception as e2:
            return jsonify({'message': 'Failed to start export!', 'error': str(e2)}), 500

@patient_bp.route('/doctors/availability', methods=['GET'])
@token_required
@patient_required
def get_doctor_availability(current_user):
    """Get doctor availability for next 7 days"""
    doctor_id = request.args.get('doctor_id')
    date = request.args.get('date')
    
    if not doctor_id:
        return jsonify({'message': 'Doctor ID is required!'}), 400
    
    
    if not date:
        start_date = datetime.today().date()
    else:
        start_date = datetime.strptime(date, '%Y-%m-%d').date()
    
    end_date = start_date + timedelta(days=7)
    
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.date >= start_date,
        DoctorAvailability.date <= end_date,
        DoctorAvailability.is_available == True
    ).order_by(DoctorAvailability.date, DoctorAvailability.start_time).all()
    
    return jsonify({
        'availabilities': [avail.to_dict() for avail in availabilities]
    })

@patient_bp.route('/search/doctors', methods=['GET'])
@token_required
@patient_required
def search_doctors(current_user):
    """Search doctors by name or specialization"""
    query = request.args.get('q', '')
    specialization = request.args.get('specialization', '')
    
    if not query and not specialization:
        return jsonify({'message': 'Search query or specialization is required!'}), 400
    
    search_query = Doctor.query.filter_by(is_available=True)
    
    if query:
        search_query = search_query.filter(
            (Doctor.first_name.ilike(f'%{query}%')) |
            (Doctor.last_name.ilike(f'%{query}%')) |
            (Doctor.specialization.ilike(f'%{query}%'))
        )
    
    if specialization:
        search_query = search_query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
    
    doctors = search_query.all()
    
    return jsonify({
        'doctors': [doctor.to_dict() for doctor in doctors]
    })