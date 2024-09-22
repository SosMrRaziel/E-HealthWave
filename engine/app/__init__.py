from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import jwt




app = Flask(__name__)
app.config['DEBUG'] = True
app.config.from_object(Config)




db = SQLAlchemy(app)
Migrate = Migrate(app, db)
login = LoginManager()
login.init_app(app)
# redirect to login page if user is not logged in
login.login_view = "login"

# Set up the request loader
@login.request_loader
def load_user_from_request(request):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data['user_id']
            return Users.query.get(user_id)
        except Exception as e:
            print(f"Token validation error: {e}")
            return None
    return None

from .models import Users
@login.user_loader
def load_user(user_id):
    return Users.query.get(user_id)



from app import models, routes, doctor_routes, patient_routes, redcross_routes

