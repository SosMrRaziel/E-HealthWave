from flask_login import current_user, login_required
from flask import request, jsonify, session
from .helper import role_required, save_file
from datetime import datetime
from app import app, db
from .models import Users, Doctors, Patients, Certificates, Working_days, Appointments, Working_days
from sqlalchemy.exc import IntegrityError



@app.route('/doctor/register', methods=['POST'])
@login_required
@role_required('doctor')
def register_doctor():
    if not current_user.is_authenticated:
            return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    try:

        data = request.form.to_dict()
        if not data['first_name'] or not data['last_name'] or not data['gender'] \
            or not data['date_of_birth'] or not data['phone']\
                or not data['address'] or not data['zip_code'] or not data['specialty']:
            return jsonify({'message': 'Missing data'}), 400
        
        try:
            date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
        
        profile_picture = None
        if 'profile_picture' in request.files and not Doctors.query.filter_by(user_id=current_user.user_id).first():
            file = request.files['profile_picture']
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400
            if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):

                profile_picture = save_file(file, current_user.username)
            else:
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
            
        banner_picture = None
        if 'banner_picture' in request.files and not Doctors.query.filter_by(user_id=current_user.user_id).first():
            file = request.files['banner_picture']
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400
            if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):

                banner_picture = save_file(file, current_user.username)
            else:
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
        
        doctor = Doctors (
            user_id=current_user.user_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            gender=data['gender'],
            date_of_birth= date_of_birth,
            phone=data['phone'],
            address=data['address'],
            zip_code=data['zip_code'],
            specialty=data['specialty'],
            profile_picture=profile_picture,
            banner_picture=banner_picture
        )
        db.session.add(doctor)
        db.session.commit()
        return jsonify({'message': 'Doctor registered'}), 201
    except IntegrityError:
        return jsonify({'message': 'Doctor already registered'}), 400


@app.route('/doctor/update', methods=['PUT'])
@login_required
@role_required('doctor')
def update_doctor():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    data = request.form.to_dict()
    try:
        doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
        if not doctor:
            return jsonify({'message': 'Doctor not found'}), 404
        
        if 'first_name' in data and data['first_name'].strip():
            doctor.first_name = data.get('first_name')
        if 'last_name' in data and data['last_name'].strip():
            doctor.last_name = data.get('last_name')
        if 'gender' in data and data['gender'].strip():
            gender = data.get('gender')
            if gender and gender not in ['male', 'female']:
                return jsonify({'message': 'Only male or female is allowed'}), 400

        if 'date_of_birth' in data and data['date_of_birth'].strip():
            date_of_birth_str = data.get('date_of_birth')
            if date_of_birth_str:
                try:
                    date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
                    doctor.date_of_birth = date_of_birth
                except ValueError:
                    return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
        if 'phone' in data and data['phone'].strip():
            doctor.phone = data.get('phone')
        if 'address' in data and data['address'].strip():
            doctor.address = data.get('address')
        if 'zip_code' in data and data['zip_code'].strip():
            doctor.zip_code = data.get('zip_code')
        if 'specialty' in data and data['specialty'].strip():
            doctor.specialty = data.get('specialty')
        
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '' and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                doctor.profile_picture = save_file(file, current_user.username)
            elif file.filename != '':
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
            
        if 'banner_picture' in request.files:
            file = request.files['banner_picture']
            if file.filename != '' and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                doctor.banner_picture = save_file(file, current_user.username)
            elif file.filename != '':
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400

        db.session.commit()
        return jsonify({'message': 'Doctor updated'}), 200
    
    except IntegrityError:
        return jsonify({'message': 'Doctor already registered'}), 400
    

@app.route('/doctor/profile/<string:username>', methods=['GET'])
@login_required
def doctor_profile(username):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    doctor = Doctors.query.join(Users).filter(Users.username == username).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404
    
    if doctor.is_deleted == True:
        return jsonify({'message': 'Doctor not found'}), 404
    
    return jsonify({
        'first_name': doctor.first_name,
        'last_name': doctor.last_name,
        'gender': doctor.gender,
        'date_of_birth': doctor.date_of_birth,
        'phone': doctor.phone,
        'address': doctor.address,
        'zip_code': doctor.zip_code,
        'specialty': doctor.specialty,
        'is_active': doctor.user.is_active
    }), 200


@app.route('/doctor/certificate/create', methods=['POST'])
@login_required
@role_required('doctor')
def create_certificate():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    # Check if the current user is a doctor
    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    data = request.form.to_dict()
    if not data.get('certificate_name') or not data.get('issue_date'):
        return jsonify({'message': 'Missing required data'}), 400
    
    if Certificates.query.filter_by(doctor_id=doctor.doctor_id, certificate_name=data['certificate_name']).first():
        return jsonify({'message': 'Certificate already exists'}), 400

    expiry_date = None

    issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d').date()

    if data.get('expiry_date'):
        try:
            expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid expiry date format, should be YYYY-MM-DD'}), 400
        
    certificate_picture = None
    if 'certificate_picture' in request.files:
        file = request.files['certificate_picture']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            certificate_picture = save_file(file, current_user.username)
        else:
            return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400

    if issue_date and expiry_date and issue_date > expiry_date:
        return jsonify({'message': 'Issue date cannot be greater than expiry date'}), 400
    
    certificate_picture = None

    if 'certificate_picture' in request.files and not Certificates.query.filter_by(doctor_id=doctor.doctor_id, certificate_name=data['certificate_name']).first():
        file = request.files['certificate_picture']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            certificate_picture = save_file(file, current_user.username)
        else:
            return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400

    certificate = Certificates(
        doctor_id=doctor.doctor_id,
        certificate_name=data['certificate_name'],
        certificate_number=data.get('certificate_number'),
        issue_date=issue_date,
        expiry_date=expiry_date,
        certificate_picture=certificate_picture
    )
    db.session.add(certificate)
    db.session.commit()
    return jsonify({'message': 'Certificate created'}), 201

@app.route('/doctor/certificate/update/<string:certificate_name>', methods=['PUT'])
@login_required
@role_required('doctor')
def update_certificate(certificate_name):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    certificate = Certificates.query.filter_by(doctor_id=doctor.doctor_id, certificate_name=certificate_name).first()
    if not certificate:
        return jsonify({'message': 'Certificate not found'}), 404

    data = request.form.to_dict()
    if not data['certificate_name']:
        return jsonify({'message': 'Missing required data'}), 400

    if 'certificate_number' in data and data.get('certificate_number'):
        certificate.certificate_number = data.get('certificate_number')

    issue_date = None
    expiry_date = None

    if 'issue_date' in data:
        issue_date_str = data.get('issue_date')
        if issue_date_str:
            try:
                issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
                certificate.issue_date = issue_date
            except ValueError:
                return jsonify({'message': 'Invalid issue date format, should be YYYY-MM-DD'}), 400
        
    if 'expiry_date' in data:
        expiry_date_str = data.get('expiry_date')
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                certificate.expiry_date = expiry_date
            except ValueError:
                return jsonify({'message': 'Invalid expiry date format, should be YYYY-MM-DD'}), 400

        
    if issue_date and expiry_date and issue_date > expiry_date:
        return jsonify({'message': 'Issue date cannot be greater than expiry date'}), 400
    
    if 'certificate_picture' in request.files:
        file = request.files['certificate_picture']
        if file.filename != '' and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            certificate.certificate_picture = save_file(file, current_user.username)
        elif file.filename != '':
            return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
    
    db.session.commit()
    return jsonify({'message': 'Certificate updated'}), 200


@app.route('/doctor/certificate/delete/<string:certificate_name>', methods=['PUT'])
@login_required
@role_required('doctor')
def delete_certificate(certificate_name):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    certificate = Certificates.query.filter_by(doctor_id=doctor.doctor_id, certificate_name=certificate_name).first()
    if not certificate:
        return jsonify({'message': 'Certificate not found'}), 404

    if certificate:
        certificate.is_deleted = True
        db.session.commit()
        return jsonify({'message': 'Certificate deleted'}), 200
    return jsonify({'message': 'Certificate not found'}), 404
        

@app.route('/doctor/<string:username>/certificates', methods=['GET'])
@login_required
# @role_required('doctor')
def list_certificates(username):
    doctor = Doctors.query.join(Users).filter(Users.username == username).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    certificates = Certificates.query.filter_by(doctor_id=doctor.doctor_id).all()
    if not certificates:
        return jsonify({'message': 'No certificates found'}), 404

    certificate_list = []
    for certificate in certificates:
        certificate_list.append({
            'certificate_name': certificate.certificate_name,
            'certificate_number': certificate.certificate_number,
            'issue_date': certificate.issue_date,
            'expiry_date': certificate.expiry_date,
            'certificate_picture': certificate.certificate_picture
        })
    return jsonify(certificate_list), 200


@app.route('/doctor/workdays/create', methods=['POST'])
@login_required
@role_required('doctor')
def create_workdays():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    data = request.get_json()
    print(data)
    if not data.get('day') or not data.get('start_time') or not data.get('end_time'):
        return jsonify({'message': 'Missing required data'}), 400

    day = data.get('day').capitalize()
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    if day not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        return jsonify({'message': 'Invalid day'}), 400

    if Working_days.query.filter_by(doctor_id=doctor.doctor_id, day=day).first():
        return jsonify({'message': 'Day already exists'}), 400

    workday = Working_days(
        doctor_id=doctor.doctor_id,
        day=day,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(workday)
    db.session.commit()
    return jsonify({'message': 'Workday created'}), 201



@app.route('/doctor/workdays/update/<string:day>', methods=['PUT'])
@login_required
@role_required('doctor')
def update_workdays(day):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Workday not found'}), 404

    workday = Working_days.query.filter_by(doctor_id=doctor.doctor_id, day=day).first()
    if not workday:
        return jsonify({'message': 'Workday not found'}), 404

    data = request.get_json()
    if not data.get('start_time') or not data.get('end_time') or not data.get('is_active'):
        return jsonify({'message': 'Missing required data'}), 400

    start_time = data.get('start_time')
    end_time = data.get('end_time')
    is_active = data.get('is_active').lower() == 'true'

    workday.start_time = start_time
    workday.end_time = end_time
    workday.is_active = is_active
    db.session.commit()
    return jsonify({'message': 'Workday updated'}), 200


@app.route('/doctor/workdays/active/<string:day>', methods=['PUT'])
@login_required
@role_required('doctor')
def active_workdays(day):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Workday not found'}), 404

    workday = Working_days.query.filter_by(doctor_id=doctor.doctor_id, day=day).first()
    if not workday:
        return jsonify({'message': 'Workday not found'}), 404

    if workday.is_active == True:
        workday.is_active = False
        db.session.commit()
        return jsonify({'message': 'Workday activated'}), 200
    workday.is_active = True
    db.session.commit()
    return jsonify({'message': 'Workday deactivated'}), 200

@app.route('/doctor/<string:username>/workdays', methods=['GET'])
@login_required
def list_workdays(username):
    doctor = Doctors.query.join(Users).filter(Users.username == username).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    workdays = Working_days.query.filter_by(doctor_id=doctor.doctor_id).all()
    if not workdays:
        return jsonify({'message': 'No workdays found'}), 404

    workday_list = []
    for workday in workdays:
        workday_list.append({
            'day': workday.day,
            'start_time': workday.start_time.strftime('%H:%M:%S'),
            'end_time': workday.end_time.strftime('%H:%M:%S'),
            'is_active': workday.is_active
        })
    return jsonify(workday_list), 200


@app.route('/doctor/appointment/create', methods=['POST'])
@login_required
@role_required('doctor')
def create_appointment():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    data = request.get_json()
    required_fields = ['appointment_name', 'appointment_type', 'appointment_date', 'appointment_time', 'username']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required data'}), 400

    patient = Patients.query.join(Users).filter(Users.username == data['username']).first()
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    try:
        appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
    try:
        appointment_time = datetime.strptime(data['appointment_time'], '%H:%M:%S').time()
    except ValueError:
        return jsonify({'message': 'Invalid time format, should be HH:MM:SS'}), 400

    if Appointments.query.filter_by(doctor_id=doctor.doctor_id, patient_id=patient.patient_id, appointment_date=appointment_date, appointment_time=appointment_time).first():
        return jsonify({'message': 'Appointment already exists'}), 400

    appointment = Appointments(
        doctor_id=doctor.doctor_id,
        patient_id=patient.patient_id,
        appointment_type=data['appointment_type'],
        appointment_name=data['appointment_name'],
        appointment_description=data.get('appointment_description'),
        appointment_date=appointment_date,
        appointment_time=appointment_time
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment created'}), 201


@app.route('/doctor/appointment/update/<string:appointment_name>', methods=['PUT'])
@login_required
@role_required('doctor')
def update_appointment(appointment_name):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    appointment = Appointments.query.filter_by(doctor_id=doctor.doctor_id, appointment_name=appointment_name).first()
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404

    data = request.get_json()
    if not data.get('appointment_name'):
        return jsonify({'message': 'Missing required data: appointment_name'}), 400

    appointment.appointment_name = data.get('appointment_name')

    if data.get('appointment_type'):
        appointment.appointment_type = data.get('appointment_type')
    if data.get('appointment_description'):
        appointment.appointment_description = data.get('appointment_description')
    if data.get('appointment_date'):
        try:
            appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
            appointment.appointment_date = appointment_date
        except ValueError:
            return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
    if data.get('appointment_time'):
        try:
            appointment_time = datetime.strptime(data['appointment_time'], '%H:%M:%S').time()
            appointment.appointment_time = appointment_time
        except ValueError:
            return jsonify({'message': 'Invalid time format, should be HH:MM:SS'}), 400

    appointment.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Appointment updated'}), 200


@app.route('/doctor/appointment/active/<string:appointment_name>', methods=['PUT'])
@login_required
@role_required('doctor')
def active_appointment(appointment_name):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    appointment = Appointments.query.filter_by(doctor_id=doctor.doctor_id, appointment_name=appointment_name).first()
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404

    if appointment.is_active == True:
        appointment.is_active = False
        db.session.commit()
        return jsonify({'message': 'Appointment activated'}), 200
    appointment.is_active = True
    appointment.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Appointment deactivated'}), 200


@app.route('/doctor/appointment/delete/<string:appointment_name>', methods=['PUT'])
@login_required
@role_required('doctor')
def delete_appointment(appointment_name):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    appointment = Appointments.query.filter_by(doctor_id=doctor.doctor_id, appointment_name=appointment_name).first()
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404

    if appointment:
        appointment.is_deleted = True
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Appointment deleted'}), 200
    return jsonify({'message': 'Appointment not found'}), 404



# @app.route('/doctor/<string:username>/appointments', methods=['GET'])
# @login_required
# @role_required('doctor')
# def list_appointments(username):
#     doctor = Doctors.query.join(Users).filter(Users.username == username).first()
#     if not doctor:
#         return jsonify({'message': 'Doctor not found'}), 404

#     appointments = Appointments.query.filter_by(doctor_id=doctor.doctor_id).all()
#     if not appointments:
#         return jsonify({'message': 'No appointments found'}), 404

#     appointment_list = []
#     for appointment in appointments:
#         appointment_list.append({
#             'appointment_name': appointment.appointment_name,
#             'appointment_type': appointment.appointment_type,
#             'appointment_description': appointment.appointment_description,
#             'appointment_date': appointment.appointment_date,
#             'appointment_time': appointment.appointment_time,
#             'is_active': appointment.is_active
#         })
#     return jsonify(appointment_list), 200


@app.route('/doctor/appointments', methods=['GET'])
@login_required
@role_required('doctor')
def list_doctor_appointments():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    doctor = Doctors.query.filter_by(user_id=current_user.user_id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    appointments = db.session.query(Appointments, Patients).join(Patients, Appointments.patient_id == Patients.patient_id).filter(Appointments.doctor_id == doctor.doctor_id).all()
    if not appointments:
        return jsonify({'message': 'No appointments found'}), 404

    appointment_list = []
    for appointment, patient in appointments:
        appointment_list.append({
            'appointment_name': appointment.appointment_name,
            'appointment_type': appointment.appointment_type,
            'appointment_description': appointment.appointment_description,
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
            'is_active': appointment.is_active,
            'patient_username': patient.user.username,
            'patient_first_name': patient.first_name,
            'patient_last_name': patient.last_name
        })
    return jsonify(appointment_list), 200