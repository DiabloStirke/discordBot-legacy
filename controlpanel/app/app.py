from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db_path = Path(__file__).parent.parent / 'storage/database.db'
app = Flask(__name__, static_url_path='', static_folder='static')
app.config['SECRET_KEY'] = 'bad_secret'  # TODO: Change this
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

print(app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)
