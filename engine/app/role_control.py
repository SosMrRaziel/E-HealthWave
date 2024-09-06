from functools import wraps
from flask import request, jsonify
from .models import Users

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = request.headers.get('user_id')
            user = Users.query.get(user_id)
            if user.role != required_role:
                return jsonify({'message': 'Permission denied'}), 403
            
            user = Users.query.get(user_id)
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            if user.role != required_role:
                return jsonify({'message': 'Permission denied'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
            
