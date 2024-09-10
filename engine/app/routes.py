from flask import request, jsonify, session, redirect, url_for
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from .helper import role_required
from .models import Users, Doctors, Patients, Certificates
import jwt
import datetime
from dotenv import load_dotenv
import os
from config import Config
from sqlalchemy.exc import IntegrityError, DataError

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
# @login_required
@role_required('doctor')
def register_doctor():
    if not current_user.is_authenticated:
            return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    try:

        data = request.get_json()
        if not data['first_name'] or not data['last_name'] or not data['gender'] \
            or not data['date_of_birth'] or not data['phone']\
                or not data['address'] or not data['zip_code'] or not data['specialty']:
            return jsonify({'message': 'Missing data'}), 400
        
        try:
            date_of_birth = datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
        
        doctor = Doctors (
            user_id=current_user.user_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            gender=data['gender'],
            date_of_birth= date_of_birth,
            phone=data['phone'],
            address=data['address'],
            zip_code=data['zip_code'],
            specialty=data['specialty']
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
    
    data = request.get_json()
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
            if gender not in ['male', 'female']:
                return jsonify({'message': 'Only male or female is allowed'}), 400
            doctor.gender = gender
        if 'date_of_birth' in data:
            try:
                date_of_birth = datetime.datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date()
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
# @login_required
@role_required('patient')
def register_patient():
    if not current_user.is_authenticated:
            return jsonify({'message': 'You must be logged in to access this page'}), 401
    
    try:
        data = request.get_json()
        if not data['first_name'] or not data['last_name'] or not data['gender'] \
            or not data['date_of_birth'] or not data['phone']\
                or not data['address'] or not data['zip_code']:
            return jsonify({'message': 'Missing data'}), 400
        
        try:
            date_of_birth = datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
        
        patient = Patients (
            user_id=current_user.user_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            gender=data['gender'],
            date_of_birth= date_of_birth,
            phone=data['phone'],
            address=data['address'],
            zip_code=data['zip_code']
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
    
    data = request.get_json()
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
            if gender not in ['male', 'female']:
                return jsonify({'message': 'Only male or female is allowed'}), 400
            patient.gender = gender
        if 'date_of_birth' in data:
            try:
                date_of_birth = datetime.datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date()
                patient.date_of_birth = date_of_birth
            except ValueError:
                return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
        if 'phone' in data:
            patient.phone = data.get('phone')
        if 'address' in data:
            patient.address = data.get('address')
        if 'zip_code' in data:
            patient.zip_code = data.get('zip_code')
        
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
    
    
    
    data = request.get_json()
    if not data['certificate_name'] or not data['certificate_number'] or not \
            data['issue_date'] or not data['expiry_date']:
        return jsonify({'message': 'Missing data'}), 400
    
    try:
        issue_date = datetime.datetime.strptime(data['issue_date'], '%Y-%m-%d').date()
        expiry_date = datetime.datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format, should be YYYY-MM-DD'}), 400
    
    certificate = Certificates(
        doctor_id=current_user.user_id,
        certificate_name=data['certificate_name'],
        certificate_number=data['certificate_number'],
        issue_date=issue_date,
        expiry_date=expiry_date
    )
    db.session.add(certificate)
    db.session.commit()
    return jsonify({'message': 'Certificate created'}), 201

