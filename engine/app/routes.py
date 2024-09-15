from flask import request, jsonify, session, redirect, url_for
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from .helper import role_required, create_user_folder, save_file
from .models import Users, Doctors, Patients, Certificates, Working_days
import jwt
import datetime
from dotenv import load_dotenv
# import os
from config import Config
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename


# load_dotenv()
# SECRET_KEY = os.getenv('SECRET_KEY')

# @app.before_request
# def log_ip():
#     ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
#     print(f'User IP: {ip_address}')

@app.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return jsonify({'message': 'Already logged in'}), 200
    data = request.get_json()
    if not data['username'] or not data['password'] or not data['role'] or not data["email"]:
        return jsonify({'message': 'Missing data'}), 400
    
    username = data['username']
    password = data['password']
    role = data['role']
    email = data['email']

    # Check if the username is already taken
    if Users.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already taken'}), 400
    
    if role != 'patient' and role != 'doctor':
        return jsonify({'message': 'Invalid role'}), 400
    
    # Create a new user
    new_user = Users(username=username, role=role, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

@app.route('/user/update', methods=['PUT'])
@login_required
def update_user():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    data = request.get_json()
    try:
        user = Users.query.filter_by(user_id=current_user.user_id).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if 'username' in data:
            if Users.query.filter_by(username=data.get('username')).first():
                return jsonify({'message': 'Username already taken'}), 400
            user.username = data.get('username')
            
        if 'email' in data:
            if Users.query.filter_by(email=data.get('email')).first():
                return jsonify({'message': 'Email already taken'}), 400
            user.email = data.get('email')
        

        
        db.session.commit()
        return jsonify({'message': 'User updated'}), 200
    
    except IntegrityError:
        return jsonify({'message': 'User already registered'}), 400



@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        print('current_user:', current_user)
        return jsonify({'message': 'Already logged in'}), 200

    data = request.get_json()
    user = Users.query.filter_by(username=data['username']).first()
    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    create_user_folder(user.username)

    login_user(user)

    token = jwt.encode({
        'user_id': user.user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, Config.SECRET_KEY, algorithm='HS256')

    return jsonify({'token': token, 'message': 'Logged in'}), 200



@app.route('/logout', methods=['POST'])
@login_required
def logout():
    if not current_user.is_authenticated:
        return jsonify({'message': 'Not logged in'}), 200

    print('current_user:', current_user)
    logout_user()
    session.clear()
    return jsonify({'message': 'Logged out'}), 200


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
            date_of_birth = datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
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
        
        if 'first_name' in data:
            doctor.first_name = data.get('first_name')
        if 'last_name' in data:
            doctor.last_name = data.get('last_name')
        if 'gender' in data:
            gender = data.get('gender')
            if gender and gender not in ['male', 'female']:
                return jsonify({'message': 'Only male or female is allowed'}), 400

        if 'date_of_birth' in data:
            date_of_birth_str = data.get('date_of_birth')
            if date_of_birth_str:
                try:
                    date_of_birth = datetime.datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
                    doctor.date_of_birth = date_of_birth
                except ValueError:
                    return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
        if 'phone' in data:
            doctor.phone = data.get('phone')
        if 'address' in data:
            doctor.address = data.get('address')
        if 'zip_code' in data:
            doctor.zip_code = data.get('zip_code')
        if 'specialty' in data:
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




@app.route('/patient/register', methods=['POST'])
@login_required
@role_required('patient')
def register_patient():
    if not current_user.is_authenticated:
            return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    try:
        data = request.form.to_dict()
        if not data['first_name'] or not data['last_name'] or not data['gender'] \
            or not data['date_of_birth'] or not data['phone']\
                or not data['address'] or not data['zip_code']:
            return jsonify({'message': 'Missing data'}), 400
        
        try:
            date_of_birth = datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
        
        profile_picture = None
        if 'profile_picture' in request.files and not Patients.query.filter_by(user_id=current_user.user_id).first():
            file = request.files['profile_picture']
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400
            if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):

                profile_picture = save_file(file, current_user.username)
            else:
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
            
        banner_picture = None
        if 'banner_picture' in request.files and not Patients.query.filter_by(user_id=current_user.user_id).first():
            file = request.files['banner_picture']
            if file.filename == '':
                return jsonify({'message': 'No selected file'}), 400
            if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):

                banner_picture = save_file(file, current_user.username)
            else:
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
        
        patient = Patients (
            user_id=current_user.user_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            gender=data['gender'],
            date_of_birth= date_of_birth,
            phone=data['phone'],
            address=data['address'],
            zip_code=data['zip_code'],
            profile_picture=profile_picture,
            banner_picture=banner_picture
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify({'message': 'Patient registered'}), 201
    except IntegrityError:
        return jsonify({'message': 'Patient already registered'}), 400
    

@app.route('/patient/update', methods=['PUT'])
@login_required
@role_required('patient')
def update_patient():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    data = request.form.to_dict()
    try:
        patient = Patients.query.filter_by(user_id=current_user.user_id).first()
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        
        if 'first_name' in data:
            patient.first_name = data.get('first_name')
        if 'last_name' in data:
            patient.last_name = data.get('last_name')
        if 'gender' in data:
            gender = data.get('gender')
            if gender and gender not in ['male', 'female']:
                return jsonify({'message': 'Only male or female is allowed'}), 400

        if 'date_of_birth' in data:
            date_of_birth_str = data.get('date_of_birth')
            if date_of_birth_str:
                try:
                    date_of_birth = datetime.datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
                    patient.date_of_birth = date_of_birth
                except ValueError:
                    return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
        if 'phone' in data:
            patient.phone = data.get('phone')
        if 'address' in data:
            patient.address = data.get('address')
        if 'zip_code' in data:
            patient.zip_code = data.get('zip_code')

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '' and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                patient.profile_picture = save_file(file, current_user.username)
            elif file.filename != '':
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
            
        if 'banner_picture' in request.files:
            file = request.files['banner_picture']
            if file.filename != '' and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                patient.banner_picture = save_file(file, current_user.username)
            elif file.filename != '':
                return jsonify({'message': 'Invalid file format, should be PNG or JPG'}), 400
        
        db.session.commit()
        return jsonify({'message': 'Patient updated'}), 200
    
    except IntegrityError:
        return jsonify({'message': 'Patient already registered'}), 400
    

@app.route('/patient/profile/<string:username>', methods=['GET'])
@login_required
def patient_profile(username):
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    patient = Patients.query.join(Users).filter(Users.username == username).first()
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
    
    if patient.is_deleted == True:
        return jsonify({'message': 'Patient not found'}), 404
    
    return jsonify({
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'gender': patient.gender,
        'date_of_birth': patient.date_of_birth,
        'phone': patient.phone,
        'address': patient.address,
        'zip_code': patient.zip_code,
        'is_active': patient.user.is_active
    }), 200


@app.route('/user/delete', methods=['PUT'])
@login_required
def delete_user():
    if not current_user.is_authenticated:
        return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    username = current_user.username
    doctor = Doctors.query.join(Users).filter(Users.username == username).first()
    patient = Patients.query.join(Users).filter(Users.username == username).first()

    if doctor:
        doctor.is_deleted = True
        db.session.commit()
        return jsonify({'message': 'Doctor deleted'}), 200
    if patient:
        patient.is_deleted = True
        db.session.commit()
        return jsonify({'message': 'Patient deleted'}), 200
    return jsonify({'message': 'User not found'}), 404


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

    issue_date = datetime.datetime.strptime(data['issue_date'], '%Y-%m-%d').date()

    if data.get('expiry_date'):
        try:
            expiry_date = datetime.datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
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
                issue_date = datetime.datetime.strptime(issue_date_str, '%Y-%m-%d').date()
                certificate.issue_date = issue_date
            except ValueError:
                return jsonify({'message': 'Invalid issue date format, should be YYYY-MM-DD'}), 400
        
    if 'expiry_date' in data:
        expiry_date_str = data.get('expiry_date')
        if expiry_date_str:
            try:
                expiry_date = datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
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
        return jsonify({'message': 'Doctor not found'}), 404

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

