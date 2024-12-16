from app.database import db

class HealthData(db.Model):
    __tablename__ = 'health_data'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(25))
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String(10))
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)
    obesity = db.Column(db.String(25))
    disability = db.Column(db.String(50))
    fitzpatrick = db.Column(db.String(50))
    allergies = db.Column(db.String(50))
    diabetes = db.Column(db.String(50))
    thyroid = db.Column(db.String(50))
    cancer = db.Column(db.String(50))
    covid = db.Column(db.String(50))
    asthma = db.Column(db.String(50))
    hiv_aids = db.Column(db.String(50))
    addiction = db.Column(db.String(50))