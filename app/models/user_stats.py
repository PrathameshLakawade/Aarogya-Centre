from app.database import db

class UserStats(db.Model):
    __tablename__ = 'user_stats'
    id = db.Column(db.Integer, primary_key=True)
    account_created_on = db.Column(db.Date)
    number_of_appointments = db.Column(db.Integer)
    number_of_virtual_appointments = db.Column(db.Integer)
    number_of_documents_uploaded = db.Column(db.Integer)
    number_of_members_added = db.Column(db.Integer)