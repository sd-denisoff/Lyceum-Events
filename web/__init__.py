from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

mail = Mail()
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
mail.init_app(app)

from web import views
