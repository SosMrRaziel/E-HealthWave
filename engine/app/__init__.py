from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager




app = Flask(__name__)
app.config['DEBUG'] = True
app.config.from_object(Config)




db = SQLAlchemy(app)
Migrate = Migrate(app, db)
login = LoginManager(app)
# redirect to login page if user is not logged in
# login.login_view = "login"

from .models import Users
@login.user_loader
def load_user(user_id):
    return Users.query.get(user_id)



from app import models, routes

