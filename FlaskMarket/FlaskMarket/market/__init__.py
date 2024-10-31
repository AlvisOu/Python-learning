from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'

app.config['SECRET_KEY'] = 'eec4b7c68f1e3b68b32aeed2'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login_page" # So @login_required knows where to direct user to
login_manager.login_message_category = "info"

from market import routes