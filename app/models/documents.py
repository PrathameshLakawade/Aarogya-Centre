from app.database import db

class Documents(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    document_name = db.Column(db.String(50))
    document = db.Column(db.String(100))
    upload_date = db.Column(db.Date)