from app.database import db

class AppointmentData(db.Model):
    __tablename__ = 'appointment_data'
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.String(25))
    user_id = db.Column(db.Integer, db.ForeignKey('basic_data.id'))
    user_name = db.Column(db.String(50))
    doctor_id = db.Column(db.Integer, db.ForeignKey('basic_data.id'))
    doctor_name = db.Column(db.String(50))
    specialist = db.Column(db.String(50))
    appointment_date = db.Column(db.Date)
    appointment_time = db.Column(db.String(25))
    appointment_address = db.Column(db.String(100))
    appointment_city = db.Column(db.String(25))
    appointment_state = db.Column(db.String(25))