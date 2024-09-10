from functools import wraps
from flask import request, jsonify, redirect, url_for
from .models import Users, Doctors, Patients
from flask_login import current_user 






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
        if doctor.is_deleted == True:
            return jsonify({'message': 'You do not have permission to access this page.'}), 403
        if patient.is_deleted == True:
            return jsonify({'message': 'You do not have permission to access this page.'}), 403
        return f(*args, **kwargs)
    return decorated_function







            
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