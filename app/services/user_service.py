from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError
from datetime import date

from app.database import db
from app.models.basic_data import BasicData
from app.models.health_data import HealthData
from app.models.user_stats import UserStats
from app.models.doctor_stats import DoctorStats
from app.models.documents import Documents


def authentication(login_data):
    """Authenticate a user or doctor based on email and password."""
    Session = sessionmaker(bind=db.engine)
    session = Session()
    
    try:
        account = session.query(BasicData).filter_by(
            email_address=login_data['email'],
            password=login_data['password']
        ).first()
        
        return account.id
    except SQLAlchemyError as e:
        print(f"Error during authentication: {e}")
        return False, ''
    finally:
        session.close()


def create_profile(profile_data):
    """Create user profile."""
    today = date.today()
    birthdate = profile_data['birth_date'].split("-")
    age = today.year - int(birthdate[0]) - ((today.month, today.day) < (int(birthdate[1]), int(birthdate[2])))
    try:
        existing_user = BasicData.query.filter_by(email_address=profile_data['email']).first()
        if existing_user:
            return False

        basic_data = BasicData(
            first_name=profile_data['first_name'],
            last_name=profile_data['last_name'],
            birth_date=profile_data['birth_date'],
            city=profile_data['city'],
            state=profile_data['state'],
            mobile_number=profile_data['mobile'],
            email_address=profile_data['email'],
            password=profile_data['password'],
            speciality=profile_data['speciality'],
            is_doctor=profile_data['is_doctor'],
            logged_in=False
        )
        db.session.add(basic_data)
        db.session.flush()

        user_health_data = HealthData(
            id=basic_data.id,
            gender=profile_data['gender'],
            age=age
        )
        db.session.add(user_health_data)
        
        if profile_data['is_doctor']:
            doctor_stats = DoctorStats(
                id=basic_data.id,
                account_created_on=today,
                number_of_appointments_diagnosed=0,
                number_of_virtual_appointments_diagnosed=0
            )
            db.session.add(doctor_stats)
            db.session.commit()
        else:
            user_stats = UserStats(
                id=basic_data.id,
                account_created_on=today,
                number_of_appointments=0,
                number_of_virtual_appointments=0,
                number_of_documents_uploaded=0,
                number_of_members_added=0
            )
            db.session.add(user_stats)
            db.session.commit()
        return True

    except IntegrityError as e:
        db.session.rollback()
        print(f"IntegrityError: {e}")
        return False

    except Exception as e:
        db.session.rollback()
        print(f"Error creating profile: {e}")
        return False


def get_profile(id):
    """Fetch user profile data from UserBasicData, UserHealthData, UserDocuments, and UserStats."""
    try:
        basic_data = BasicData.query.filter_by(id=id).first()

        if not basic_data:
            return None
        
        health_data = HealthData.query.filter_by(id=id).first()
        documents = Documents.query.filter_by(id=id).all()
        
        data = {
            "basic_data": {
                "id": basic_data.id,
                "first_name": basic_data.first_name,
                "last_name": basic_data.last_name,
                "profile_picture": basic_data.profile_picture,
                "email_address": basic_data.email_address,
                "birth_date": basic_data.birth_date,
                "address": basic_data.address,
                "city": basic_data.city,
                "state": basic_data.state,
                "mobile_number": basic_data.mobile_number,
                "speciality": basic_data.speciality
            },
            "health_data": {
                "gender": health_data.gender,
                "age": health_data.age,
                "blood_group": health_data.blood_group,
                "weight": health_data.weight,
                "height": health_data.height,
                "obesity": health_data.obesity,
                "disability": health_data.disability,
                "fitzpatrick": health_data.fitzpatrick,
                "allergies": health_data.allergies,
                "diabetes": health_data.diabetes,
                "thyroid": health_data.thyroid,
                "cancer": health_data.cancer,
                "covid": health_data.covid,
                "asthma": health_data.asthma,
                "hiv_aids": health_data.hiv_aids,
                "addiction": health_data.addiction
            },
            "documents": [
                {
                    "document_id": doc.id,
                    "document_name": doc.document_name,
                    "upload_date": doc.upload_date
                }
                for doc in documents
            ]
        }
        
        if basic_data.is_doctor:
            doctor_stats = DoctorStats.query.filter_by(id=id).first()
            data["stats"] = {
                "account_created_on": doctor_stats.account_created_on,
                "number_of_appointments_diagnosed": doctor_stats.number_of_appointments,
                "number_of_virtual_appointments_diagnosed": doctor_stats.number_of_virtual_appointments
            }
        else:
            user_stats = UserStats.query.filter_by(id=id).first()
            data["stats"] = {
                "account_created_on": user_stats.account_created_on,
                "number_of_appointments": user_stats.number_of_appointments,
                "number_of_virtual_appointments": user_stats.number_of_virtual_appointments,
                "number_of_documents_uploaded": user_stats.number_of_documents_uploaded,
                "number_of_members_added": user_stats.number_of_members_added
            }    
        
        return data
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return None


def get_doctors(mode, city, speciality):
    """Fetch doctor profile based on mode, city, and speciality"""
    try:
        if mode == 'Virtual':
            doctors = BasicData.query.filter_by(
                is_doctor=True,
                speciality=speciality
            )
        else:
            doctors = BasicData.query.filter_by(
                is_doctor=True,
                city=city,
                speciality=speciality
            )

        if not doctors:
            return None
        
        list_of_doctors = [
            {
                "doctor_id": doctor.id,
                "doctor_name": doctor.first_name + " " + doctor.last_name
            }
            for doctor in doctors
        ]
        
        return list_of_doctors
    except Exception as e:
        print(f"Error fetching doctors: {e}")
        return None


def update_profile(id, update_data):
    """Update user profile data in UserBasicData, UserHealthData, UserDocuments, and UserStats."""
    try:
        basic_data = BasicData.query.filter_by(id=id).first()
        if not basic_data:
            return False

        for key, value in update_data.get("basic_data", {}).items():
            setattr(basic_data, key, value)

        health_data = HealthData.query.filter_by(id=id).first()
        if health_data:
            for key, value in update_data.get("health_data", {}).items():
                setattr(health_data, key, value)

        if basic_data.is_doctor:
            doctor_stats = DoctorStats.query.filter_by(id=id).first()
            if doctor_stats:
                for key, value in update_data.get("stats", {}).items():
                    setattr(doctor_stats, key, value)
        else:
            user_stats = UserStats.query.filter_by(id=id).first()
            if user_stats:
                for key, value in update_data.get("stats", {}).items():
                    setattr(user_stats, key, value)

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error updating user profile: {e}")
        return False
