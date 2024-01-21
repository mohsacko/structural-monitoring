from flask import Flask
from flask_migrate import Migrate

import os
#from dotenv import load_dotenv
database_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')

from .models import db

#load_dotenv()

# Explicitly set the path to the static folder
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'), static_folder=static_path, static_url_path='/static')

# Only load .env file if not on Heroku
if os.environ.get('HEROKU') is None:
    from dotenv import load_dotenv
    load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['STATIC_FOLDER'] = 'static'

db.init_app(app)

migrate = Migrate(app, db)

# Import views after the app instance is created
from . import views, models
