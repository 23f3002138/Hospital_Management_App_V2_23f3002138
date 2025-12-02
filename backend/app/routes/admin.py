from flask import Blueprint, request, jsonify, make_response
from ..models import db, User, Doctor, Patient, Department, Appointment, Treatment, DoctorAvailability
from ..auth import token_required, admin_required
from datetime import datetime, timedelta
import redis
import csv
import io
import calendar
from xhtml2pdf import pisa

admin_bp = Blueprint('admin', __name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@admin_bp.route('/dashboard', methods=['GET'])
@token_required
@admin_required
def admin_dashboard(current_user):
    """Admin dashboard with statistics"""
    cache_key = 'admin_dashboard'
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        import json
        return jsonify(json.loads(cached_data))
    
    today = datetime.today().date()
    
    
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    today_appointments = Appointment.query.filter_by(appointment_date=today).count()
    
    
    recent_appointments = Appointment.query.order_by(
        Appointment.created_at.desc()
    ).limit(10).all()
    
    dashboard_data = {
        'stats': {
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'total_appointments': total_appointments,
            'today_appointments': today_appointments
        },
        'recent_appointments': [appt.to_dict() for appt in recent_appointments]
    }
    
    
    import json
    redis_client.setex(cache_key, 120, json.dumps(dashboard_data))
    
    return jsonify(dashboard_data)

@admin_bp.route('/doctors', methods=['GET'])
@token_required
@admin_required
def get_doctors(current_user):
    """Get all doctors"""
    doctors = Doctor.query.all()
    return jsonify({'doctors': [doctor.to_dict() for doctor in doctors]})

@admin_bp.route('/doctors', methods=['POST'])
@token_required
@admin_required
def add_doctor(current_user):
    """Add a new doctor"""
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 
                      'specialization', 'department_id', 'phone']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'{field} is required!'}), 400
    
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists!'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists!'}), 400
    
    if data.get('license_number') and Doctor.query.filter_by(license_number=data['license_number']).first():
        return jsonify({'message': 'License number already exists!'}), 400
        
    # Validate department
    if not Department.query.get(data['department_id']):
        return jsonify({'message': 'Invalid Department ID!'}), 400
        
    # Validate numeric fields
    try:
        if data.get('consultation_fee'):
            float(data['consultation_fee'])
        if data.get('experience'):
            int(data['experience'])
    except ValueError:
        return jsonify({'message': 'Invalid number format for fee or experience!'}), 400
    
    try:
        
        user = User(
            username=data['username'],
            email=data['email'],
            role='doctor'
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()
        
        
        doctor = Doctor(
            user_id=user.id,
            department_id=data['department_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            specialization=data['specialization'],
            phone=data.get('phone'),
            address=data.get('address'),
            license_number=data.get('license_number'),
            experience=data.get('experience'),
            consultation_fee=data.get('consultation_fee'),
            is_available=data.get('is_available', True)
        )
        
        # Check for missing fields
        if not all([data.get('address'), data.get('license_number'), data.get('experience') is not None, data.get('consultation_fee') is not None]):
             return jsonify({'message': 'All fields are required!'}), 400
        
        db.session.add(doctor)
        db.session.commit()
        
        
        redis_client.delete('admin_dashboard')
        # Clear all doctor list caches
        for key in redis_client.scan_iter("doctors_list_*"):
            redis_client.delete(key)
        
        return jsonify({
            'message': 'Doctor added successfully!',
            'doctor': doctor.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding doctor: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Failed to add doctor!', 'error': str(e)}), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@token_required
@admin_required
def update_doctor(current_user, doctor_id):
    """Update doctor information"""
    doctor = Doctor.query.get_or_404(doctor_id)
    data = request.get_json()
    
    if 'first_name' in data:
        doctor.first_name = data['first_name']
    if 'last_name' in data:
        doctor.last_name = data['last_name']
    if 'specialization' in data:
        doctor.specialization = data['specialization']
    if 'department_id' in data:
        doctor.department_id = data['department_id']
    if 'phone' in data:
        doctor.phone = data['phone']
    if 'address' in data:
        doctor.address = data['address']
    if 'license_number' in data:
        doctor.license_number = data['license_number'] or None
    if 'experience' in data:
        doctor.experience = data['experience']
    if 'consultation_fee' in data:
        doctor.consultation_fee = data['consultation_fee']
    if 'is_available' in data:
        doctor.is_available = data['is_available']
    
    try:
        db.session.commit()
        
        
        redis_client.delete('admin_dashboard')
        redis_client.delete(f'doctor_dashboard_{doctor.id}')
        # Clear all doctor list caches
        for key in redis_client.scan_iter("doctors_list_*"):
            redis_client.delete(key)
        
        return jsonify({
            'message': 'Doctor updated successfully!',
            'doctor': doctor.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update doctor!', 'error': str(e)}), 500

@admin_bp.route('/doctors/<int:doctor_id>/block', methods=['POST'])
@token_required
@admin_required
def block_doctor(current_user, doctor_id):
    """Block/blacklist a doctor"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    try:
        
        doctor.is_available = False
        user = User.query.get(doctor.user_id)
        if user:
            user.is_active = False
        
        db.session.commit()
        
        
        redis_client.delete('admin_dashboard')
        redis_client.delete(f'doctor_dashboard_{doctor.id}')
        # Clear all doctor list caches
        for key in redis_client.scan_iter("doctors_list_*"):
            redis_client.delete(key)
        
        return jsonify({'message': 'Doctor blocked successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to block doctor!', 'error': str(e)}), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_doctor(current_user, doctor_id):
    """Permanently delete a doctor"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    try:
        # Get associated user
        user = User.query.get(doctor.user_id)
        
        # Manually delete appointments first 
        Appointment.query.filter_by(doctor_id=doctor.id).delete()
        
        # Delete doctor profile cascade should handle availabilities
        db.session.delete(doctor)
        
        # Delete user account
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        
        redis_client.delete('admin_dashboard')
        redis_client.delete(f'doctor_dashboard_{doctor_id}')
        # Clear all doctor list caches
        for key in redis_client.scan_iter("doctors_list_*"):
            redis_client.delete(key)
        
        return jsonify({'message': 'Doctor deleted permanently!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete doctor!', 'error': str(e)}), 500

@admin_bp.route('/doctors/<int:doctor_id>/unblock', methods=['POST'])
@token_required
@admin_required
def unblock_doctor(current_user, doctor_id):
    """Unblock a doctor"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    try:
        # Reactivate doctor
        doctor.is_available = True
        user = User.query.get(doctor.user_id)
        if user:
            user.is_active = True
        
        db.session.commit()
        
        # Clear caches
        redis_client.delete('admin_dashboard')
        redis_client.delete(f'doctor_dashboard_{doctor.id}')
        for key in redis_client.scan_iter("doctors_list_*"):
            redis_client.delete(key)
        
        return jsonify({'message': 'Doctor unblocked successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to unblock doctor!', 'error': str(e)}), 500

@admin_bp.route('/patients', methods=['GET'])
@token_required
@admin_required
def get_patients(current_user):
    """Get all patients"""
    patients = Patient.query.all()
    return jsonify({'patients': [patient.to_dict() for patient in patients]})

@admin_bp.route('/patients/<int:patient_id>', methods=['GET'])
@token_required
@admin_required
def get_patient(current_user, patient_id):
    """Get patient details"""
    patient = Patient.query.get_or_404(patient_id)
    return jsonify({'patient': patient.to_dict()})

@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@token_required
@admin_required
def update_patient(current_user, patient_id):
    """Update patient information"""
    patient = Patient.query.get_or_404(patient_id)
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
    if 'date_of_birth' in data:
        patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    
    try:
        db.session.commit()
        
        
        redis_client.delete(f'patient_dashboard_{patient.id}')
        redis_client.delete('admin_dashboard')
        
        return jsonify({
            'message': 'Patient updated successfully!',
            'patient': patient.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update patient!', 'error': str(e)}), 500

@admin_bp.route('/patients/<int:patient_id>/block', methods=['POST'])
@token_required
@admin_required
def block_patient(current_user, patient_id):
    """Block/blacklist a patient"""
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        
        user = User.query.get(patient.user_id)
        if user:
            user.is_active = False
        
        db.session.commit()
        
        
        redis_client.delete('admin_dashboard')
        redis_client.delete(f'patient_dashboard_{patient.id}')
        
        return jsonify({'message': 'Patient blocked successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to block patient!', 'error': str(e)}), 500

@admin_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_patient(current_user, patient_id):
    """Permanently delete a patient"""
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        # Get associated user
        user = User.query.get(patient.user_id)
        
        # Manually delete appointments first
        Appointment.query.filter_by(patient_id=patient.id).delete()
        
        # Delete patient profile
        db.session.delete(patient)
        
        # Delete user account
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        
        redis_client.delete('admin_dashboard')
        redis_client.delete(f'patient_dashboard_{patient_id}')
        
        return jsonify({'message': 'Patient deleted permanently!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete patient!', 'error': str(e)}), 500

@admin_bp.route('/patients/<int:patient_id>/unblock', methods=['POST'])
@token_required
@admin_required
def unblock_patient(current_user, patient_id):
    """Unblock a patient"""
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        # Reactivate patient
        user = User.query.get(patient.user_id)
        if user:
            user.is_active = True
        
        db.session.commit()
        
        # Clear caches
        redis_client.delete('admin_dashboard')
        redis_client.delete(f'patient_dashboard_{patient.id}')
        
        return jsonify({'message': 'Patient unblocked successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to unblock patient!', 'error': str(e)}), 500

@admin_bp.route('/appointments', methods=['GET'])
@token_required
@admin_required
def get_appointments(current_user):
    """Get all appointments with filters"""
    status = request.args.get('status')
    date = request.args.get('date')
    doctor_id = request.args.get('doctor_id')
    patient_id = request.args.get('patient_id')
    
    query = Appointment.query
    
    if status:
        query = query.filter_by(status=status)
    if date:
        query = query.filter_by(appointment_date=datetime.strptime(date, '%Y-%m-%d').date())
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    
    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
    
    appointments_data = []
    for appt in appointments:
        appt_data = appt.to_dict()
        if appt.treatment:
            appt_data['treatment'] = appt.treatment.to_dict()
        appointments_data.append(appt_data)
    
    return jsonify({'appointments': appointments_data})

@admin_bp.route('/appointments/upcoming', methods=['GET'])
@token_required
@admin_required
def get_upcoming_appointments(current_user):
    """Get upcoming appointments"""
    today = datetime.today().date()
    appointments = Appointment.query.filter(
        Appointment.appointment_date >= today,
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    
    return jsonify({'appointments': [appt.to_dict() for appt in appointments]})

@admin_bp.route('/appointments/past', methods=['GET'])
@token_required
@admin_required
def get_past_appointments(current_user):
    """Get past appointments"""
    today = datetime.today().date()
    appointments = Appointment.query.filter(
        Appointment.appointment_date < today
    ).order_by(Appointment.appointment_date.desc()).all()
    
    appointments_data = []
    for appt in appointments:
        appt_data = appt.to_dict()
        if appt.treatment:
            appt_data['treatment'] = appt.treatment.to_dict()
        appointments_data.append(appt_data)
    
    return jsonify({'appointments': appointments_data})

@admin_bp.route('/search/advanced', methods=['GET'])
@token_required
@admin_required
def advanced_search(current_user):
    """Advanced search for patients and doctors"""
    search_type = request.args.get('type', 'all')  
    query = request.args.get('q', '')
    field = request.args.get('field', 'name')  
    
    results = {}
    
    if search_type in ['all', 'patients']:
        patient_query = Patient.query
        
        if query:
            try:
                if field == 'name':
                    patient_query = patient_query.filter(
                        (Patient.first_name.ilike(f'%{query}%')) |
                        (Patient.last_name.ilike(f'%{query}%'))
                    )
                elif field == 'id':
                    patient_query = patient_query.filter(Patient.id == int(query))
                elif field == 'contact':
                    patient_query = patient_query.filter(Patient.phone.ilike(f'%{query}%'))
            except ValueError:
                pass
        
        patients = patient_query.all()
        results['patients'] = [patient.to_dict() for patient in patients]
    
    if search_type in ['all', 'doctors']:
        doctor_query = Doctor.query
        
        if query:
            if field == 'name':
                doctor_query = doctor_query.filter(
                    (Doctor.first_name.ilike(f'%{query}%')) |
                    (Doctor.last_name.ilike(f'%{query}%'))
                )
            elif field == 'specialization':
                doctor_query = doctor_query.filter(Doctor.specialization.ilike(f'%{query}%'))
        
        doctors = doctor_query.all()
        results['doctors'] = [doctor.to_dict() for doctor in doctors]
    
    return jsonify(results)

@admin_bp.route('/departments', methods=['POST'])
@token_required
@admin_required
def add_department(current_user):
    """Add a new department"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'message': 'Department name is required!'}), 400
    
    if Department.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Department already exists!'}), 400
    
    try:
        department = Department(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(department)
        db.session.commit()
        
        
        redis_client.delete('departments_list')
        
        return jsonify({
            'message': 'Department added successfully!',
            'department': department.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add department!', 'error': str(e)}), 500

@admin_bp.route('/jobs/daily-reminders', methods=['POST'])
@token_required
@admin_required
def trigger_daily_reminders(current_user):
    """Manually trigger daily reminders job (for demo/testing)"""
    try:
        from ..tasks import send_daily_reminders_task
        
        result = send_daily_reminders_task()
        return jsonify({
            'message': 'Daily reminders job executed successfully!',
            'result': result
        }), 200
    except Exception as e:
        return jsonify({
            'message': 'Failed to execute daily reminders job!',
            'error': str(e)
        }), 500

@admin_bp.route('/jobs/monthly-reports', methods=['POST'])
@token_required
@admin_required
def trigger_monthly_reports(current_user):
    """Manually trigger monthly reports job (for demo/testing)"""
    try:
        from ..tasks import send_monthly_reports_task
        
        result = send_monthly_reports_task()
        return jsonify({
            'message': 'Monthly reports job executed successfully!',
            'result': result
        }), 200
    except Exception as e:
        return jsonify({
            'message': 'Failed to execute monthly reports job!',
            'error': str(e)
        }), 500

@admin_bp.route('/export/appointments', methods=['GET'])
@token_required
@admin_required
def export_appointments_csv(current_user):
    """Export appointments as CSV for a specific month"""
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not month or not year:
            today = datetime.today()
            month = today.month
            year = today.year

        # Calculate start and end date of the month
        _, last_day = calendar.monthrange(year, month)
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, last_day).date()

        appointments = Appointment.query.filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).order_by(Appointment.appointment_date).all()

        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['ID', 'Date', 'Time', 'Patient Name', 'Doctor Name', 'Department', 'Status', 'Reason', 'Diagnosis'])
        
        for appt in appointments:
            diagnosis = appt.treatment.diagnosis if appt.treatment else 'N/A'
            patient_name = appt.patient.full_name if appt.patient else 'Unknown'
            doctor_name = appt.doctor.full_name if appt.doctor else 'Unknown'
            dept_name = appt.doctor.department.name if (appt.doctor and appt.doctor.department) else 'N/A'
            
            writer.writerow([
                appt.id,
                appt.appointment_date,
                appt.appointment_time,
                patient_name,
                doctor_name,
                dept_name,
                appt.status,
                appt.reason,
                diagnosis
            ])
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename=appointments_{year}_{month}.csv"
        response.headers["Content-type"] = "text/csv"
        return response
        
    except Exception as e:
        return jsonify({'message': 'Export failed!', 'error': str(e)}), 500

@admin_bp.route('/export/monthly-report-pdf', methods=['GET'])
@token_required
@admin_required
def export_monthly_report_pdf(current_user):
    """Export monthly report as PDF"""
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not month or not year:
            today = datetime.today()
            month = today.month
            year = today.year

        # Calculate start and end date
        _, last_day = calendar.monthrange(year, month)
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, last_day).date()
        
        month_name = calendar.month_name[month]
        '''
        # Fetch data
        appointments = Appointment.query.filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).order_by(Appointment.appointment_date).all()'''
        appointments = Appointment.query.filter(
        Appointment.appointment_date.between(start_date, end_date)
        ).order_by(Appointment.appointment_date).all()

        
        total_revenue = sum(appt.doctor.consultation_fee for appt in appointments if appt.doctor)
        
        # Generate HTML for PDF
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Helvetica, Arial, sans-serif; padding: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 20px; }}
                .summary-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #e9ecef; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th {{ background-color: #3498db; color: white; padding: 10px; text-align: left; }}
                td {{ border-bottom: 1px solid #ddd; padding: 8px; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .footer {{ margin-top: 30px; font-size: 10px; text-align: center; color: #7f8c8d; }}
                .badge {{ padding: 3px 8px; border-radius: 10px; font-size: 10px; color: white; }}
                .bg-completed {{ background-color: #28a745; }}
                .bg-scheduled {{ background-color: #007bff; }}
                .bg-cancelled {{ background-color: #dc3545; }}
            </style>
        </head>
        <body>
            <h1>Hospital Monthly Report</h1>
            <p><strong>Period:</strong> {month_name} {year}</p>
            <p><strong>Generated on:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            
            <div class="summary-box">
                <h3>Executive Summary</h3>
                <table style="border: none;">
                    <tr style="background: none;">
                        <td style="border: none;"><strong>Total Appointments:</strong> {len(appointments)}</td>
                        <td style="border: none;"><strong>Estimated Revenue:</strong> ${total_revenue:.2f}</td>
                    </tr>
                </table>
            </div>
            
            <h2>Appointment Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Patient</th>
                        <th>Doctor</th>
                        <th>Dept</th>
                        <th>Status</th>
                        <th>Fee</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for appt in appointments:
            status_color = "bg-secondary"
            if appt.status == 'completed': status_color = "bg-completed"
            elif appt.status == 'scheduled': status_color = "bg-scheduled"
            elif appt.status == 'cancelled': status_color = "bg-cancelled"
            
            fee = appt.doctor.consultation_fee if appt.doctor else 0
            
            html_content += f"""
                    <tr>
                        <td>{appt.appointment_date}</td>
                        <td>{appt.patient.full_name if appt.patient else 'Unknown'}</td>
                        <td>{appt.doctor.full_name if appt.doctor else 'Unknown'}</td>
                        <td>{appt.doctor.department.name if (appt.doctor and appt.doctor.department) else 'N/A'}</td>
                        <td><span class="badge {status_color}">{appt.status}</span></td>
                        <td>${fee:.2f}</td>
                    </tr>
            """
            
        html_content += """
                </tbody>
            </table>
            
            <div class="footer">
                <p>Confidential Report - Hospital Management System</p>
            </div>
        </body>
        </html>
        """
        
        # Convert to PDF
        output = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.StringIO(html_content), dest=output)
        
        if pisa_status.err:
            return jsonify({'message': 'PDF generation error'}), 500
            
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename=report_{year}_{month}.pdf"
        response.headers["Content-type"] = "application/pdf"
        return response
        
    except Exception as e:
        return jsonify({'message': 'Export failed!', 'error': str(e)}), 500
