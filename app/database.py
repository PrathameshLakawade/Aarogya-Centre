from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager

db = SQLAlchemy()


def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    app.logger.info(f"Database initialization successful!")


@contextmanager
def get_db_connection():
    """Provide a database session for use with queries."""
    connection = None
    try:
        connection = db.engine.connect()
        yield connection
    finally:
        if connection:
            connection.close()