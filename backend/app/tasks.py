from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
import csv
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os


celery = None

def make_celery(app):
    celery_app = Celery(
        app.import_name,
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )
    
    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app.Task = ContextTask
    
    
    
    import platform
    worker_pool = 'solo' if platform.system() == 'Windows' else 'prefork'
    
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        worker_pool=worker_pool,
        beat_schedule={
            'daily-reminders': {
                'task': 'app.tasks.send_daily_reminders',
                # Actual schedule: Daily at 8:00 AM 
                'schedule': crontab(hour=8, minute=0),
                #'schedule': 60.0,  # DEMO: Uncomment this line to run every 1 minute
            },
            'monthly-reports': {
                'task': 'app.tasks.send_monthly_reports',
                # Actual schedule: 1st day of every month at 9:00 AM 
                'schedule': crontab(day_of_month=1, hour=9, minute=0),
                #'schedule': 60.0,  # DEMO: Uncomment this line to run every 1 minute
            },
        }
    )
    
    return celery_app

def send_email(to_email, subject, body, html_body=None, attachment=None, filename=None):
    """Send email using SMTP"""
    print(f"Sending email to {to_email}: {subject}")
    try:
        
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        
        if not smtp_user or not smtp_password:
            print(f"Email not configured. Would send to {to_email}: {subject}")
            print(f"Body: {body}")
            return True
        
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        if attachment and filename:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            msg.attach(part)
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_daily_reminders_task():
    """Send daily reminders for appointments"""
    from .models import Appointment, Patient, Doctor, User
    
    today = datetime.today().date()
    appointments = Appointment.query.filter_by(
        appointment_date=today,
        status='scheduled'
    ).all()
    
    print(f"=== DAILY REMINDERS: {len(appointments)} appointments ===")
    
    for appointment in appointments:
        patient = Patient.query.get(appointment.patient_id)
        doctor = Doctor.query.get(appointment.doctor_id)
        user = User.query.get(patient.user_id)
        
        if not user or not user.email:
            continue
        
        message = f"""
Dear {patient.first_name} {patient.last_name},

This is a reminder that you have an appointment scheduled today:

Date: {appointment.appointment_date}
Time: {appointment.appointment_time}
Doctor: Dr. {doctor.first_name} {doctor.last_name}
Specialization: {doctor.specialization}

Please arrive 10 minutes before your scheduled time.

Thank you,
Hospital Management System
"""
        
        html_message = f"""
<html>
<body>
<h2>Appointment Reminder</h2>
<p>Dear {patient.first_name} {patient.last_name},</p>
<p>This is a reminder that you have an appointment scheduled today:</p>
<ul>
<li><strong>Date:</strong> {appointment.appointment_date}</li>
<li><strong>Time:</strong> {appointment.appointment_time}</li>
<li><strong>Doctor:</strong> Dr. {doctor.first_name} {doctor.last_name}</li>
<li><strong>Specialization:</strong> {doctor.specialization}</li>
</ul>
<p>Please arrive 10 minutes before your scheduled time.</p>
<p>Thank you,<br>Hospital Management System</p>
</body>
</html>
"""
        
        send_email(
            to_email=user.email,
            subject=f"Appointment Reminder - {appointment.appointment_time}",
            body=message,
            html_body=html_message
        )
        print(f"Sent reminder to {user.email}")
    
    return f"Processed reminders for {len(appointments)} appointments"

def send_monthly_reports_task():
    """Send monthly activity reports to doctors"""
    from .models import Doctor, Appointment, Treatment, User
    
    # Use current month for demo purposes so users see immediate data
    today = datetime.today()
    start_date = today.replace(day=1)
    end_date = today
    
    report_month_str = start_date.strftime('%B %Y')
    
    doctors = Doctor.query.all()
    
    print(f"=== MONTHLY REPORTS ({report_month_str}): {len(doctors)} doctors ===")
    print(f"Querying period: {start_date.date()} to {end_date.date()}")
    
    for doctor in doctors:
        user = User.query.get(doctor.user_id)
        if not user or not user.email:
            continue
        print(user.email)
        #  Check for any appointments for this doctor regardless of status/date
        total_appts = Appointment.query.filter_by(doctor_id=doctor.id).count()
        print(f"Doctor {doctor.id} ({doctor.first_name} {doctor.last_name}): Total appointments in DB: {total_appts}")

        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= start_date.date(),
            Appointment.appointment_date <= end_date.date()
        ).all()
        
        print(f"  -> Found {len(appointments)} appointments for report period.")

        html_report = f"""
<html>
<head>
<style>
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background-color: #4CAF50; color: white; }}
</style>
</head>
<body>
<h2>Monthly Activity Report - {report_month_str}</h2>
<p>Dear Dr. {doctor.first_name} {doctor.last_name},</p>
<p>Here is your activity report for the current month:</p>

<h3>Summary</h3>
<ul>
<li><strong>Total Appointments:</strong> {len(appointments)}</li>
<li><strong>Period:</strong> {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}</li>
</ul>

<h3>Appointment Details</h3>
<table>
<tr>
<th>Date</th>
<th>Patient</th>
<th>Status</th>
<th>Diagnosis</th>
<th>Treatment</th>
</tr>
"""
        
        if not appointments:
             html_report += """
<tr>
<td colspan="5" style="text-align:center;">No appointments found for this period.</td>
</tr>
"""

        for appointment in appointments:
            patient = appointment.patient
            treatment = appointment.treatment
            diagnosis = treatment.diagnosis if treatment else "N/A"
            prescription = treatment.prescription[:50] + "..." if treatment and treatment.prescription and len(treatment.prescription) > 50 else (treatment.prescription if treatment else "N/A")
            
            html_report += f"""
<tr>
<td>{appointment.appointment_date}</td>
<td>{patient.first_name} {patient.last_name}</td>
<td>{appointment.status}</td>
<td>{diagnosis[:50]}</td>
<td>{prescription}</td>
</tr>
"""
        
        html_report += """
</table>
<p>Thank you for your service.</p>
<p>Hospital Management System</p>
</body>
</html>
"""
        
        send_email(
            to_email=user.email,
            subject=f"Monthly Activity Report - {report_month_str}",
            body=f"Monthly report for {report_month_str}. {len(appointments)} appointments completed.",
            html_body=html_report
        )
        print(f"Sent report to Dr. {doctor.first_name} {doctor.last_name} ({user.email}) - {len(appointments)} appts")
    
    return f"Generated reports for {len(doctors)} doctors (Period: {report_month_str})"

def export_patient_treatment_history(patient_id, email):
    """Export patient treatment history as CSV"""
    from .models import Patient, Appointment, Treatment
    
    patient = Patient.query.get(patient_id)
    
    if not patient:
        return "Patient not found"
    
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        status='completed'
    ).order_by(Appointment.appointment_date).all()
    
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'User ID', 'Username', 'Consulting Doctor', 'Appointment Date', 
        'Diagnosis', 'Treatment', 'Next Visit Suggested'
    ])
    
    for appointment in appointments:
        treatment = appointment.treatment
        user = appointment.patient.user
        
        writer.writerow([
            user.id,
            user.username,
            appointment.doctor.full_name,
            appointment.appointment_date.isoformat(),
            treatment.diagnosis if treatment else 'N/A',
            treatment.prescription if treatment and treatment.prescription else 'N/A',
            treatment.follow_up_date.isoformat() if treatment and treatment.follow_up_date else 'N/A'
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    
    message = f"""
Dear {patient.first_name} {patient.last_name},

Your treatment history has been exported successfully.

Please find the CSV file attached.

Thank you,
Hospital Management System
"""
    
    send_email(
        to_email=email,
        subject="Treatment History Export",
        body=message,
        attachment=csv_content.encode('utf-8'),
        filename=f"treatment_history_{patient_id}_{datetime.now().strftime('%Y%m%d')}.csv"
    )
    
    print(f"=== CSV EXPORT for {patient.first_name} {patient.last_name} ===")
    print(f"Records: {len(appointments)}")
    print(f"Sent to: {email}")
    
    return f"Exported {len(appointments)} records and sent to {email}"

def init_celery(app):
    """Initialize Celery and register tasks"""
    global celery
    celery = make_celery(app)
    
    
    @celery.task(name='app.tasks.send_daily_reminders')
    def send_daily_reminders():
        return send_daily_reminders_task()
    
    @celery.task(name='app.tasks.send_monthly_reports')
    def send_monthly_reports():
        return send_monthly_reports_task()
    
    @celery.task(name='app.tasks.export_patient_treatment_history')
    def export_patient_treatment_history_task(patient_id, email):
        return export_patient_treatment_history(patient_id, email)
    
    
    celery.export_patient_treatment_history = export_patient_treatment_history_task
    
    return celery


def get_export_task():
    """Get the export task function"""
    if celery:
        return celery.export_patient_treatment_history
    else:
        
        def dummy_task(patient_id, email):
            return export_patient_treatment_history(patient_id, email)
        return dummy_task
