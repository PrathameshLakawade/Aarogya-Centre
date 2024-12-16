from sqlalchemy.dialects.postgresql import BYTEA
from app.database import db

class BasicData(db.Model):
    __tablename__ = 'basic_data'
    id = db.Column(db.Integer, primary_key=True)
    profile_picture = db.Column(BYTEA)
    first_name = db.Column(db.String(25))
    last_name = db.Column(db.String(25))
    birth_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    city = db.Column(db.String(25))
    state = db.Column(db.String(25))
    mobile_number = db.Column(db.BigInteger)
    email_address = db.Column(db.String(50))
    password = db.Column(db.String(50))
    speciality = db.Column(db.String(50))
    is_doctor = db.Column(db.Boolean)
    logged_in = db.Column(db.Boolean)