from flask import request, jsonify, session, redirect, url_for
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from .helper import role_required
from .models import Users, Doctors, Patients
import jwt
import datetime
from dotenv import load_dotenv
import os
from config import Config
from sqlalchemy.exc import IntegrityError

# load_dotenv()
# SECRET_KEY = os.getenv('SECRET_KEY')



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


@app.route('/patient/register', methods=['POST'])
@login_required
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
    
