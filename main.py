from flask import Flask
from flask_session import Session
from flask_mail import Mail
import logging, secrets

from app.database import init_db
from app.routes import bp as routes_bp

def create_app():
    app = Flask(__name__,
                template_folder='./app/templates',
                static_folder='./app/static')
    app.config.from_object('app.config.Config')
    
    # Session Configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_FILE_DIR'] = './app/sessions'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    Session(app)
    
    # Logging Configuration
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    # Initialize Flask-Mail
    mail = Mail(app)

    # Initialize SQLAlchemy
    init_db(app)

    # Register blueprints
    app.register_blueprint(routes_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)