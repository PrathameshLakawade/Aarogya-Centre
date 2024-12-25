from app.database import db

class MembersData(db.Model):
    __tablename__ = 'members_data'
    member_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    relation = db.Column(db.String)