from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from app.database import db
from app.models.appointment_data import AppointmentData


def create_appointment(data):
    """Create appointment."""
    try:

        appointment_data = AppointmentData(
            mode=data['mode'],
            user_id=data['user_id'],
            user_name=data['user_name'],
            doctor_id=data['doctor_id'],
            doctor_name=data['doctor_name'],
            specialist=data['specialist'],
            appointment_date=data['appointment_date'],
            appointment_time=data['appointment_time'],
            appointment_address=data['appointment_address'],
            appointment_city=data['appointment_city'],
            appointment_state=data['appointment_state']
        )
        db.session.add(appointment_data)
        db.session.commit()
        return True

    except IntegrityError as e:
        db.session.rollback()
        print(f"IntegrityError: {e}")
        return False

    except Exception as e:
        db.session.rollback()
        print(f"Error creating appointment: {e}")
        return False


def get_appointment(id):
    """Fetch appointment data."""
    try:
        app_data = AppointmentData.query.filter_by(id=id).first()

        if not app_data:
            return None
        
        appointment_data = {
            "mode": app_data.mode,
            "user_id": app_data.user_id,
            "user_name": app_data.user_name,
            "doctor_id": app_data.doctor_id,
            "doctor_name": app_data.doctor_name,
            "specialist": app_data.specialist,
            "appointment_date": app_data.appointment_date,
            "appointment_time": app_data.appointment_time,
            "appointment_address": app_data.appointment_address,
            "appointment_city": app_data.appointment_city,
            "appointment_state": app_data.appointment_state
        }
        
        return appointment_data
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return None


def get_all_appointments(id):
    """Fetch all appointment data for user."""
    try:
        app_data = AppointmentData.query.filter_by(user_id=id)
        
        if not app_data:
            return None
        
        appointment_data = []
        
        for data in app_data:
            appointment_data.append(
                {
                    "id": data.id,
                    "mode": data.mode,
                    "user_id": data.user_id,
                    "user_name": data.user_name,
                    "doctor_id": data.doctor_id,
                    "doctor_name": data.doctor_name,
                    "specialist": data.specialist,
                    "appointment_date": data.appointment_date,
                    "appointment_time": data.appointment_time,
                    "appointment_address": data.appointment_address,
                    "appointment_city": data.appointment_city,
                    "appointment_state": data.appointment_state
                }
            )
        return appointment_data
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return None


def get_upcoming_appointments(user_id, date):
    """Fetch the closest upcoming appointments for virtual and physical modes from the given date."""
    try:
        closest_virtual_appointment = AppointmentData.query.filter(
            and_(
                AppointmentData.user_id == user_id,
                AppointmentData.appointment_date > date,
                AppointmentData.mode == 'Virtual'
            )
        ).order_by(AppointmentData.appointment_date).first()

        closest_physical_appointment = AppointmentData.query.filter(
            and_(
                AppointmentData.user_id == user_id,
                AppointmentData.appointment_date > date,
                AppointmentData.mode != 'Virtual'
            )
        ).order_by(AppointmentData.appointment_date).first()

        closest_appointments = {
            'virtual': None,
            'physical': None
        }

        if closest_virtual_appointment:
            closest_appointments['virtual'] = {
                "mode": closest_virtual_appointment.mode,
                "user_name": closest_virtual_appointment.user_name,
                "doctor_name": closest_virtual_appointment.doctor_name,
                "specialist": closest_virtual_appointment.specialist,
                "appointment_date": closest_virtual_appointment.appointment_date,
                "appointment_time": closest_virtual_appointment.appointment_time
            }
        if closest_physical_appointment:
            closest_appointments['physical'] = {
                "mode": closest_physical_appointment.mode,
                "user_name": closest_physical_appointment.user_name,
                "doctor_name": closest_physical_appointment.doctor_name,
                "specialist": closest_physical_appointment.specialist,
                "appointment_date": closest_physical_appointment.appointment_date,
                "appointment_time": closest_physical_appointment.appointment_time,
                "appointment_address": closest_physical_appointment.appointment_address,
                "appointment_city": closest_physical_appointment.appointment_city,
                "appointment_state": closest_physical_appointment.appointment_state
            }
        return closest_appointments

    except Exception as e:
        print(f"Error fetching closest appointments: {e}")
        return None


def check_availability(name, date):
    """Fetch doctors availability for given date."""
    try:
        appointment_slots = [
            "10:00 AM - 10:30 AM", "10:30 AM - 11:00 AM", "11:00 AM - 11:30 AM",
            "11:30 AM - 12:00 PM", "01:00 PM - 01:30 PM", "01:30 PM - 02:00 PM",
            "02:00 PM - 02:30 PM", "02:30 PM - 03:00 PM", "03:00 PM - 03:30 PM",
            "03:30 PM - 04:00 PM", "04:00 PM - 04:30 PM", "04:30 PM - 05:00 PM",
            "06:00 PM - 06:30 PM", "06:30 PM - 07:00 PM", "07:00 PM - 07:30 PM",
            "07:30 PM - 08:00 PM"
        ]
                
        slots = AppointmentData.query.filter_by(
            doctor_name=name,
            appointment_date=date
        )
        
        if not slots:
            return appointment_slots
        
        for slot in slots:
            if slot.appointment_time in appointment_slots:
                appointment_slots.remove(slot.appointment_time)
        
        return appointment_slots
    except Exception as e:
        print(f"Error fetching doctors availability: {e}")
        return None
