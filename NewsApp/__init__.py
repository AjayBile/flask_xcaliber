import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
app.config['SECRET_KEY'] = 'bbc6f35cb0e9994f0f7677798fba89dc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = "smtp.googlemail.com"
app.config['MAIL_PORT'] = "587"
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "ajay.bile007@gmail.com"
app.config['MAIL_PASSWORD'] = "autakiotmhxkjxma"
mail = Mail(app)

from NewsApp import routes
