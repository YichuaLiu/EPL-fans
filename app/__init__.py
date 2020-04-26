from flask import Flask
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
# print(db)
# epl = SQLAlchemy(app)
# epl.session.bind = epl.get_engine(bind='epl')
# print(epl)

bcrypt = Bcrypt(app)
mail = Mail(app)
login = LoginManager(app)

login.login_view = 'login'
login.login_message = 'You must login to access this page'
login.login_message_category = 'info'

from app.routes import *



