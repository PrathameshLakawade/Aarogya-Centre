from sqlalchemy.dialects.postgresql import BYTEA
from datetime import datetime
from tzlocal import get_localzone
from app.database import db

local_tz = get_localzone()

class Documents(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    document_name = db.Column(db.String(50), nullable=False)
    document = db.Column(BYTEA, nullable=False)
    upload_date = db.Column(db.Date, default=datetime.now(local_tz), nullable=False)