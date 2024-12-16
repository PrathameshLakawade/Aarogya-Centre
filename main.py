from flask import Flask
from flask_mail import Mail
import logging

from app.database import init_db
from app.routes import bp as routes_bp

def create_app():
    app = Flask(__name__,
                template_folder='./app/templates',
                static_folder='./app/static')
    app.config.from_object('app.config.Config')
    
    # Set up logging
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