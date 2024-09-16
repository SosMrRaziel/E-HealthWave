from functools import wraps
from flask import request, jsonify, redirect, url_for
from .models import Users, Doctors, Patients, Red_cross
from flask_login import current_user 
import os
import secrets




def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'message': 'You must be logged in to access this page.'}), 401
            if current_user.role != role:
                return jsonify({'message': 'You do not have permission to access this page.'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def deleted_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        doctor = Doctors.query.join(Users).filter(Users.username).first()
        patient = Patients.query.join(Users).filter(Users.username).first()
        red_cross = Red_cross.query.join(Users).filter(Users.username).first()
        if doctor.is_deleted == True:
            return jsonify({'message': 'You do not have permission to access this page.'}), 403
        if patient.is_deleted == True:
            return jsonify({'message': 'You do not have permission to access this page.'}), 403
        if red_cross.is_deleted == True:
            return jsonify({'message': 'You do not have permission to access this page.'}), 403
        return f(*args, **kwargs)
    return decorated_function

def create_user_folder(username):
    if not os.path.exists(os.path.join(os.getcwd(), 'app', 'static', 'uploads', username)):
        os.makedirs(os.path.join(os.getcwd(), 'app', 'static', 'uploads', username))

def user_folder(username):
    return os.path.join(os.getcwd(), 'app', 'static', 'uploads', username)


def save_file(file, username):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(file.filename)
    file_fn = random_hex + f_ext
    file_path = os.path.join(user_folder(username), file_fn)
    file.save(file_path)
    return file_fn





            
# def role_required(role):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if not current_user.is_authenticated:
#                 return jsonify({'message': 'You must be logged in to access this page.'}), 401
#             if current_user.role != role:
#                 return jsonify({'message': 'You do not have permission to access this page.'}), 403
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator