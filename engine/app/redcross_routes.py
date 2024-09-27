from flask_login import current_user, login_required
from flask import request, jsonify, session
from .helper import role_required, save_file
from datetime import datetime
from app import app, db
from .models import Users, Red_cross, Certificates, Working_days, Appointments, Patients, Documents
from sqlalchemy.exc import IntegrityError


@app.route('/redcross/register', methods=['POST'])
@login_required
@role_required('red cross')
def register_red_cross():
    if not current_user.is_authenticated:
            return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    try:
        data = request.form.to_dict()
        if not data['red_cross_name'] or not data['red_cross_phone'] or not data['red_cross_address'] or not data['red_cross_zip_code']:
            return jsonify({'message': 'Missing data'}), 400
        
        red_cross_logo = None
        if 'red_cross_logo' in request.files and not Red_cross.query.filter_by(user_id=current_user.user_id).first():
            file = request.files['red_cross_logo']
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400
            if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):

                red_cross_logo = save_file(file, current_user.username)
            else:
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
            
        red_cross_banner = None
        if 'red_cross_banner' in request.files and not Red_cross.query.filter_by(user_id=current_user.user_id).first():
            file = request.files['red_cross_banner']
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400
            if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):

                red_cross_banner = save_file(file, current_user.username)
            else:
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
            
        red_cross = Red_cross (
            user_id=current_user.user_id,
            red_cross_name=data['red_cross_name'],
            red_cross_phone=data['red_cross_phone'],
            red_cross_address=data['red_cross_address'],
            red_cross_zip_code=data['red_cross_zip_code'],
            red_cross_logo=red_cross_logo,
            red_cross_banner=red_cross_banner
        )
        db.session.add(red_cross)
        db.session.commit()
        return jsonify({'message': 'Red Cross registered'}), 201
    except IntegrityError:
        return jsonify({'message': 'Red Cross already registered'}), 400


@app.route('/redcross/update', methods=['PUT'])
@login_required
@role_required('red cross')
def update_red_cross():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    data = request.form.to_dict()
    try:
        red_cross = Red_cross.query.filter_by(user_id=current_user.user_id).first()
        if not red_cross:
            return jsonify({'message': 'Red Cross not found'}), 404
        
        if 'red_cross_name' in data and data['red_cross_name'].strip():
            red_cross.red_cross_name = data.get('red_cross_name')
        if 'red_cross_phone' in data and data['red_cross_phone'].strip():
            red_cross.red_cross_phone = data.get('red_cross_phone')
        if 'red_cross_address' in data and data['red_cross_address'].strip():
            red_cross.red_cross_address = data.get('red_cross_address')
        if 'red_cross_zip_code' in data and data['red_cross_zip_code'].strip():
            red_cross.red_cross_zip_code = data.get('red_cross_zip_code')
        
        if 'red_cross_logo' in request.files:
            file = request.files['red_cross_logo']
            if file.filename != '' and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                red_cross.red_cross_logo = save_file(file, current_user.username)
            elif file.filename != '':
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
            
        if 'red_cross_banner' in request.files:
            file = request.files['red_cross_banner']
            if file.filename != '' and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                red_cross.red_cross_banner = save_file(file, current_user.username)
            elif file.filename != '':
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400

        db.session.commit()
        return jsonify({'message': 'Red Cross updated'}), 200
    
    except IntegrityError:
        return jsonify({'message': 'Red Cross already registered'}), 400
    

@app.route('/redcross/profile/<string:username>', methods=['GET'])
@login_required
@role_required('red cross')
def red_cross_profile(username):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    red_cross = Red_cross.query.join(Users).filter(Users.username == username).first()
    if not red_cross:
        return jsonify({'message': 'Red Cross not found'}), 404
    
    if red_cross.is_deleted == True:
        return jsonify({'message': 'Red Cross not found'}), 404
    
    return jsonify({
        'red_cross_name': red_cross.red_cross_name,
        'red_cross_phone': red_cross.red_cross_phone,
        'red_cross_address': red_cross.red_cross_address,
        'red_cross_zip_code': red_cross.red_cross_zip_code,
        'is_active': red_cross.user.is_active
    }), 200


@app.route('/redcross/delete', methods=['PUT'])
@login_required
@role_required('red cross')
def delete_red_cross():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    username = current_user.username
    red_cross = Red_cross.query.join(Users).filter(Users.username == username).first()

    if red_cross:
        red_cross.is_deleted = True
        db.session.commit()
        return jsonify({'message': 'Red Cross deleted'}), 200
    return jsonify({'message': 'Red Cross not found'}), 404


@app.route('/redcross/certificate/create', methods=['POST'])
@login_required
@role_required('red cross')
def create_certificate_red_cross():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    # Check if the current user is a red cross
    red_cross = Red_cross.query.filter_by(user_id=current_user.user_id).first()
    if not red_cross:
        return jsonify({'message': 'Red Cross not found'}), 404

    data = request.form.to_dict()
    if not data.get('certificate_name') or not data.get('issue_date'):
        return jsonify({'message': 'Missing required data'}), 400
    
    if Certificates.query.filter_by(red_cross_id=red_cross.red_cross_id, certificate_name=data['certificate_name']).first():
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

    if 'certificate_picture' in request.files and not Certificates.query.filter_by(red_cross_id=red_cross.red_cross_id, certificate_name=data['certificate_name']).first():
        file = request.files['certificate_picture']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            certificate_picture = save_file(file, current_user.username)
        else:
            return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
        
    certificate = Certificates(
        red_cross_id=red_cross.red_cross_id,
        certificate_name=data['certificate_name'],
        certificate_number=data.get('certificate_number'),
        issue_date=issue_date,
        expiry_date=expiry_date,
        certificate_picture=certificate_picture
    )
    db.session.add(certificate)
    db.session.commit()
    return jsonify({'message': 'Certificate created'}), 201


@app.route('/redcross/certificate/update/<string:certificate_name>', methods=['PUT'])
@login_required
@role_required('red cross')
def update_certificate_red_cross(certificate_name):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    red_cross = Red_cross.query.filter_by(user_id=current_user.user_id).first()
    if not red_cross:
        return jsonify({'message': 'Red Cross not found'}), 404

    certificate = Certificates.query.filter_by(red_cross_id=red_cross.red_cross_id, certificate_name=certificate_name).first()
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



@app.route('/redcross/certificate/delete/<string:certificate_name>', methods=['PUT'])
@login_required
@role_required('red cross')
def delete_certificate_red_cross(certificate_name):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    red_cross = Red_cross.query.filter_by(user_id=current_user.user_id).first()
    if not red_cross:
        return jsonify({'message': 'Red Cross not found'}), 404

    certificate = Certificates.query.filter_by(red_cross_id=red_cross.red_cross_id, certificate_name=certificate_name).first()
    if not certificate:
        return jsonify({'message': 'Certificate not found'}), 404

    if certificate:
        certificate.is_deleted = True
        db.session.commit()
        return jsonify({'message': 'Certificate deleted'}), 200
    return jsonify({'message': 'Certificate not found'}), 404


@app.route('/redcross/<string:username>/certificates', methods=['GET'])
@login_required
@role_required('red cross')
def list_certificates_red_cross(username):
    red_cross = Red_cross.query.join(Users).filter(Users.username == username).first()
    if not red_cross:
        return jsonify({'message': 'Red Cross not found'}), 404

    certificates = Certificates.query.filter_by(red_cross_id=red_cross.red_cross_id).all()
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


@app.route('/redcross/workdays/create', methods=['POST'])
@login_required
@role_required('red cross')
def create_workdays_red_cross():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    red_cross = Red_cross.query.filter_by(user_id=current_user.user_id).first()
    if not red_cross:
        return jsonify({'message': 'Red Cross not found'}), 404

    data = request.get_json()
    print(data)
    if not data.get('day') or not data.get('start_time') or not data.get('end_time'):
        return jsonify({'message': 'Missing required data'}), 400

    day = data.get('day').capitalize()
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    if day not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        return jsonify({'message': 'Invalid day'}), 400

    if Working_days.query.filter_by(red_cross_id=red_cross.red_cross_id, day=day).first():
        return jsonify({'message': 'Day already exists'}), 400

    workday = Working_days(
        red_cross_id=red_cross.red_cross_id,
        day=day,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(workday)
    db.session.commit()
    return jsonify({'message': 'Workday created'}), 201


@app.route('/redcross/workdays/update/<string:day>', methods=['PUT'])
@login_required
@role_required('red cross')
def update_workdays_red_cross(day):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    red_cross = Red_cross.query.filter_by(user_id=current_user.user_id).first()
    if not red_cross:
        return jsonify({'message': 'Workday not found'}), 404

    workday = Working_days.query.filter_by(red_cross_id=red_cross.red_cross_id, day=day).first()
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


@app.route('/redcross/workdays/active/<string:day>', methods=['PUT'])
@login_required
@role_required('red cross')
def active_workdays_red_cross(day):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    red_cross = Red_cross.query.filter_by(user_id=current_user.user_id).first()
    if not red_cross:
        return jsonify({'message': 'Workday not found'}), 404

    workday = Working_days.query.filter_by(red_cross_id=red_cross.red_cross_id, day=day).first()
    if not workday:
        return jsonify({'message': 'Workday not found'}), 404

    if workday.is_active == True:
        workday.is_active = False
        db.session.commit()
        return jsonify({'message': 'Workday activated'}), 200
    workday.is_active = True
    db.session.commit()
    return jsonify({'message': 'Workday deactivated'}), 200


@app.route('/redcross/<string:username>/workdays', methods=['GET'])
@login_required
@role_required('red cross')
def list_workdays_red_cross(username):
    red_cross = Red_cross.query.join(Users).filter(Users.username == username).first()
    if not red_cross:
        return jsonify({'message': 'Red Cross not found'}), 404

    workdays = Working_days.query.filter_by(red_cross_id=red_cross.red_cross_id).all()
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


@app.route('/redcross/appointment/create', methods=['POST'])
@login_required
@role_required('red cross')
def create_appointment_red_cross():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    red_cross = Red_cross.query.filter_by(user_id=current_user.user_id).first()
    if not red_cross:
        return jsonify({'message': 'Red Cross not found'}), 404

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
    
    if Appointments.query.filter_by(patient_id=red_cross.red_cross_id, appointment_date=appointment_date, appointment_time=appointment_time).first():
        return jsonify({'message': 'Appointment already exists'}), 400
    
    appointment = Appointments(
        patient_id=patient.patient_id,
        red_cross_id=red_cross.red_cross_id,
        appointment_name=data['appointment_name'],
        appointment_type=data['appointment_type'],
        appointment_description=data.get('appointment_description'),
        appointment_date=appointment_date,
        appointment_time=appointment_time
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment created'}), 201


@app.route('/redcross/appointment/update/<string:appointment_name>', methods=['PUT'])
@login_required
@role_required('red cross')
def update_appointment_red_cross(appointment_name):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    red_cross = Red_cross.query.filter_by(user_id=current_user.user_id).first()
    if not red_cross:
        return jsonify({'message': 'Doctor not found'}), 404

    appointment = Appointments.query.filter_by(red_cross_id=red_cross.red_cross_id, appointment_name=appointment_name).first()
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


@app.route('/redcross/appointment/active/<string:appointment_name>', methods=['PUT'])
@login_required
@role_required('red cross')
def active_appointment_red_cross(appointment_name):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    red_cross = Red_cross.query.filter_by(user_id=current_user.user_id).first()
    if not red_cross:
        return jsonify({'message': 'Doctor not found'}), 404

    appointment = Appointments.query.filter_by(red_cross_id=red_cross.red_cross_id, appointment_name=appointment_name).first()
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404

    if appointment.is_active == True:
        appointment.is_active = False
        db.session.commit()
        return jsonify({'message': 'Appointment activated'}), 200
    appointment.is_active = True
    db.session.commit()
    return jsonify({'message': 'Appointment deactivated'}), 200


@app.route('/redcross/appointment/delete/<string:appointment_name>', methods=['PUT'])
@login_required
@role_required('red cross')
def delete_appointment_red_cross(appointment_name):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    red_cross = Red_cross.query.filter_by(user_id=current_user.user_id).first()
    if not red_cross:
        return jsonify({'message': 'Doctor not found'}), 404

    appointment = Appointments.query.filter_by(red_cross_id=red_cross.red_cross_id, appointment_name=appointment_name).first()
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404

    if appointment:
        appointment.is_deleted = True
        db.session.commit()
        return jsonify({'message': 'Appointment deleted'}), 200
    return jsonify({'message': 'Appointment not found'}), 404



@app.route('/redcross/appointment/documents/create', methods=['POST'])
@login_required
@role_required('red cross')
def create_document_red_cross():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    data = request.form.to_dict()
    if not data.get('appointment_name') or not data.get('document_name') or not data.get('document_type'):
        return jsonify({'message': 'Missing required data'}), 400

    appointment = Appointments.query.filter_by(appointment_name=data['appointment_name']).first()
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    # Check if a document with the same name already exists for the patient
    existing_document = Documents.query.join(Appointments).filter(
        Appointments.patient_id == appointment.patient_id,
        Documents.document_name == data['document_name']
    ).first()
    if existing_document:
        return jsonify({'message': 'Document with this name already exists for the patient'}), 400

    document_file = None
    if 'document_file' in request.files:
        file = request.files['document_file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            document_file = save_file(file, current_user.username)
        else:
            return jsonify({'message': 'Invalid file format, should be PNG, JPG, JPEG, or PDF'}), 400

    document = Documents(
        appointment_id=appointment.appointment_id,
        document_name=data['document_name'],
        document_type=data['document_type'],
        document_description=data.get('document_description'),
        document_file=document_file,
        document_url=data.get('document_url'),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_deleted=False
    )
    db.session.add(document)
    db.session.commit()
    return jsonify({'message': 'Document created'}), 201


@app.route('/redcross/appointment/documents/update/<string:document_name>', methods=['PUT'])
@login_required
@role_required('red cross')
def update_document_redcross(document_name):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    document = Documents.query.filter_by(document_name=document_name).first()
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    data = request.form.to_dict()
    patient_username = data.get('patient_username')
    if not patient_username:
        return jsonify({'message': 'Missing patient username'}), 400

    user = Users.query.filter_by(username=patient_username).first()
    if not user or not user.patient:
        return jsonify({'message': 'Patient not found'}), 404

    patient = user.patient

    appointment = Appointments.query.filter_by(appointment_id=document.appointment_id, patient_id=patient.patient_id).first()
    if not appointment:
        return jsonify({'message': 'Appointment not found for the specified patient'}), 404

    new_document_name = data.get('document_name')
    if not new_document_name:
        return jsonify({'message': 'Missing required data'}), 400
    
    existing_document = Documents.query.join(Appointments).filter(
        Appointments.patient_id == patient.patient_id,
        Documents.document_name == new_document_name,
        Documents.document_id != document.document_id
    ).first()
    if existing_document:
        return jsonify({'message': 'Document name already exists for the patient'}), 400

    document.document_name = new_document_name
    if data.get('document_type'):
        document.document_type = data.get('document_type')
    if data.get('document_description'):
        document.document_description = data.get('document_description')
    if data.get('document_url'):
        document.document_url = data.get('document_url')
    if 'document_file' in request.files:
        file = request.files['document_file']
        if file.filename != '' and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            document.document_file = save_file(file, current_user.username)
        elif file.filename != '':
            return jsonify({'message': 'Invalid file format, should be PNG, JPG, JPEG, or PDF'}), 400

    document.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Document updated'}), 200



@app.route('/redcross/appointment/documents/active/<string:document_id>', methods=['PUT'])
@login_required
@role_required('red cross')
def active_document_red_cross(document_id):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    document = Documents.query.filter_by(document_id=document_id).first()
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    if document.is_active == True:
        document.is_active = False
        db.session.commit()
        return jsonify({'message': 'Document activated'}), 200
    document.is_active = True
    db.session.commit()
    return jsonify({'message': 'Document deactivated'}), 200



@app.route('/redcross/appointment/documents/delete/<string:document_id>', methods=['PUT'])
@login_required
@role_required('red cross')
def delete_document_red_cross(document_id):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401

    document = Documents.query.filter_by(document_id=document_id).first()
    if not document:
        return jsonify({'message': 'Document not found'}), 404

    if document:
        document.is_deleted = True
        db.session.commit()
        return jsonify({'message': 'Document deleted'}), 200
    return jsonify({'message': 'Document not found'}), 404
