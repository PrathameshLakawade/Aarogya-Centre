from sqlalchemy.inspection import inspect
from sqlalchemy.exc import SQLAlchemyError
import logging
import traceback

from app.database import db
from app.models import appointment_data, basic_data, documents, health_data, user_stats, doctor_stats, members_data

logger = logging.getLogger(__name__)


def get_available_tables():
    """Fetch available tables from the PostgreSQL database."""
    try:
        with db.engine.connect() as conn:
            inspector = inspect(conn)
            return inspector.get_table_names(schema='public')
    except SQLAlchemyError as e:
        logger.error(f"Error fetching available tables: {e}")
        return []


def check_schema():
    """Check if the required tables exist and create them if they don't."""
    try:
        logger.info("Starting an inspection for required tables")
        available_tables = get_available_tables()
        required_tables = db.metadata.tables.keys()
        missing_tables = [table for table in list(required_tables) if table not in available_tables]

        if missing_tables:
            logger.info(f"Missing tables found: {missing_tables}")
            create_tables(missing_tables)
            logger.info("Inspecting complete!")
            return True
        else:
            logger.info("All required tables are present.")
            logger.info("Inspecting complete!")
            return False
    except Exception as e:
        logger.error(f"Error checking schema: {e}")
        logger.error(traceback.format_exc())
        return False


def create_tables(missing_tables):
    """Create missing tables using model metadata."""
    try:
        logger.info(f"Creating missing tables: {missing_tables}")

        if 'basic_data' in missing_tables and 'appointment_data' in missing_tables:
            appointment_data = missing_tables.pop(missing_tables.index('appointment_data'))
            missing_tables.append(appointment_data)

        db.metadata.bind = db.engine

        for table_name in missing_tables:
            if table_name in db.metadata.tables:
                table = db.metadata.tables[table_name]
                logger.info(f"Creating table: {table_name}")
                db.metadata.create_all(bind=db.engine, tables=[table])
            else:
                logger.warning(f"Table '{table_name}' not found in metadata.")

        logger.info("Missing tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        logger.error(traceback.format_exc())