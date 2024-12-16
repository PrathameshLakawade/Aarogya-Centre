from app.database import db

class DoctorStats(db.Model):
    __tablename__ = 'doctor_stats'
    id = db.Column(db.Integer, primary_key=True)
    account_created_on = db.Column(db.Date)
    number_of_appointments_diagnosed = db.Column(db.Integer)
    number_of_virtual_appointments_diagnosed = db.Column(db.Integer)