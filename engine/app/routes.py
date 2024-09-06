from flask import request, jsonify
from app import app
from flask_login import current_user, login_user, logout_user, login_required
from app.role_control import role_required
from app.models import db, Users





@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data['username'] or not data['password'] or not data['role']:
        return jsonify({'message': 'Missing data'}), 400
    
    username = data['username'] 
    password = data['password']
    role = data['role']

    # Check if the username is already taken
    if Users.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already taken'}), 400
    
    # Create a new user
    new_user = Users(username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = Users.query.filter_by(username=data['username']).first()
    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    login_user(user)
    return jsonify({'message': 'Logged in'}), 200