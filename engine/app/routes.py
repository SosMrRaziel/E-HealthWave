from flask import request, jsonify
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from .helper import create_user_folder
from .models import Users, Doctors, Patients
import jwt
import datetime
from config import Config
from sqlalchemy.exc import IntegrityError




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
    
    if role != 'patient' and role != 'doctor' and role != 'red cross':
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
    return jsonify({'message': 'Logged out'}), 200


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
