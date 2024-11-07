from flask import Flask
from config import Config
from flask_mysqldb import MySQL
from flask_mail import Mail

mysql = MySQL()
mail = Mail()

def aarogya_centre():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from . import routes
        return app
