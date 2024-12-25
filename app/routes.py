from flask import Blueprint, render_template, redirect, url_for, send_file, request, session, current_app
from datetime import datetime
from io import BytesIO

import app.utils as utils
import app.services.schema_service as schema
import app.services.profile_service as profile
import app.services.appointment_service as appointment

import pickle, os
import pandas as pd

bp = Blueprint('main', __name__)


# Home
@bp.route("/")
def home():
    schema.check_schema()
    
    session_folder = current_app.config.get('SESSION_FILE_DIR')
    if not session_folder:
        session_folder = os.path.join(current_app.instance_path, 'flask_session')
    
    if os.path.exists(session_folder):
        for filename in os.listdir(session_folder):
            file_path = os.path.join(session_folder, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting session file {file_path}: {e}")
    session.clear()
    return render_template("home.html")


# Register
@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        profile_data = {
            'first_name': request.form.get("first-name").capitalize(),
            'last_name': request.form.get("last-name").capitalize(),
            'birth_date': request.form.get("birth-date"),
            'gender': request.form.get("gender"),
            'city': request.form.get("city").capitalize(),
            'state': request.form.get("state").capitalize(),
            'email': request.form.get("email-address"),
            'mobile': request.form.get("mobile-number"),
            'password': request.form.get("password"),
            're_password': request.form.get("re-enter-password"),
            'user_category': request.form.get("user-category"),
            'speciality': request.form.get("doctor-speciality"),
            'is_doctor': False
        }

        if profile_data['password'] == profile_data['re_password']:
            if profile_data['user_category'] == 'Normal':
                profile.create_profile(profile_data)
            elif profile_data['user_category'] == 'Doctor':
                profile_data['is_doctor'] = True
                profile.create_profile(profile_data)
            else:
                return render_template("register.html", message="Invalid user category")
            return render_template("login.html", message="Registration successful")
        else:
            return render_template("register.html", message="Passwords do not match")
    else:
        return render_template("register.html")


# Login
@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        login_data = {
            'email': request.form.get("user-email"),
            'password': request.form.get("user-password")
        }

        id = profile.authentication(login_data)
        if id:
            profile_data = profile.get_profile(id)
            if profile_data != None:
                profile_data['basic_data']['logged_in'] = True
                session['profile_data'] = profile_data
                
            appointment_data = appointment.get_all_appointments(id)
            if appointment_data != None:
                session['appointment_data'] = appointment_data
                
            members_data = profile.get_members(id)
            if members_data != None:
                session['members_data'] = members_data
                
            greetings = utils.greetings()
            current_date = datetime.today().strftime("%Y-%m-%d")
            account_created_on = profile_data['stats']['account_created_on']
            account_age = datetime.strptime(current_date, "%Y-%m-%d") - datetime.strptime(str(account_created_on), "%Y-%m-%d")
            account_age = str(account_age).split(',')
            completion_percentage = utils.profile_completion(profile_data)
            session['session_stats'] = {
                'greetings': greetings,
                'account_age': account_age[0],
                'completion_percentage': completion_percentage
            }
            
            session['upcoming_appointments'] = appointment.get_upcoming_appointments(id, datetime.today())
            
            session['chat_history'] = {
                "user_id": id,
                "messages": [
                    {
                        "sender": "Bot",
                        "message": "Welcome to healthcare chatbot. How can I help you today?",
                        "timetamp": datetime.now()
                    }
                ]
            }
                
            profile.edit_profile(id, profile_data)
            return redirect(url_for('main.dashboard'))
        else:
            return render_template("login.html", message="User not found")
    else:
        return render_template("login.html")


# Dashboard
@bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html",
                           profile_data=session.get('profile_data'),
                           members_data=session.get('members_data'),
                           session_stats=session.get('session_stats'),
                           upcoming_appointments=session.get('upcoming_appointments'),
                           chat_history=session.get('chat_history'),
                           ongoing_booking=session.get('ongoing_booking'),
                           list_of_doctors=session.get('list_of_doctors'),
                           available_slots=session.get('available_slots')
                           )


# Dashboard: Search Doctors
@bp.route("/search-doctors", methods=['GET', 'POST'])
def search_doctors():
    if request.method == 'POST':
        mode = request.form.get("appointment-mode")
        member_id = request.form.get("appointment-member")
        city = request.form.get("appointment-city").capitalize()
        doctor_category = request.form.get("appointment-doctor-category")
        
        member_data = profile.get_profile(member_id)
        
        if mode == 'Hospital':
            session['ongoing_booking'] = {
                "mode": mode,
                "user_id": member_id,
                "user_name": member_data["basic_data"]["first_name"] + ' ' + member_data["basic_data"]["last_name"],
                "appointment_city": city,
                "specialist": doctor_category
            }
        elif mode == 'Home':
            session['ongoing_booking'] = {
                "mode": mode,
                "user_id": member_id,
                "user_name": member_data["basic_data"]["first_name"] + ' ' + member_data["basic_data"]["last_name"],
                "appointment_address": member_data["basic_data"]["address"],
                "appointment_city": member_data["basic_data"]["city"],
                "appointment_state": member_data["basic_data"]["state"],
                "specialist": doctor_category
            }
        else:
            session['ongoing_booking'] = {
                "mode": mode,
                "user_id": member_id,
                "user_name": member_data["basic_data"]["first_name"] + ' ' + member_data["basic_data"]["last_name"],
                "appointment_address": "Virtual",
                "appointment_city": "Virtual",
                "appointment_state": "Virtual",
                "specialist": doctor_category 
            }
        
        ongoing_booking = session.get('ongoing_booking')
        session['list_of_doctors'] = profile.get_doctors(mode, ongoing_booking['appointment_city'], doctor_category)
        
    return redirect(url_for('main.dashboard'))


# Dashboard: Check Appointment Availability
@bp.route("/check-availability", methods=['GET', 'POST'])
def check_availability():
    if request.method == 'POST':
        selected_doctor = request.form.get("appointment-doctor")
        appointment_date = request.form.get("appointment-date")

        session['available_slots'] = appointment.check_availability(selected_doctor, appointment_date)
        
        ongoing_booking = session.get('ongoing_booking')
        for doctor in session.get('list_of_doctors'):
            if doctor['doctor_name'] == selected_doctor:
                ongoing_booking['doctor_id'] = doctor['doctor_id']
        ongoing_booking['doctor_name'] = selected_doctor
        ongoing_booking['appointment_date'] = appointment_date
        
        if ongoing_booking['mode'] == "Hospital":
            doctor_data = profile.get_profile(ongoing_booking['doctor_id'])
            ongoing_booking['appointment_address'] = doctor_data["basic_data"]["address"]
            ongoing_booking['appointment_state'] = doctor_data["basic_data"]["state"]
        
        return redirect(url_for('main.dashboard'))


# Dashboard: Book Appointment
@bp.route("/book-appointment", methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        appointment_time = request.form.get("appointment-time")
        ongoing_booking = session.get('ongoing_booking')
        ongoing_booking['appointment_time'] = appointment_time

        profile_data = session.get('profile_data')
        if appointment.create_appointment(ongoing_booking):
            if ongoing_booking['mode'] == 'Virtual':
                profile_data["stats"]["number_of_virtual_appointments"] += 1
            else:
                profile_data["stats"]["number_of_appointments"] += 1
            
            profile.edit_profile(profile_data["basic_data"]["id"], profile_data)
            session.pop('ongoing_booking')
            session.pop('list_of_doctors')
            session.pop('available_slots')
            
            session['upcoming_appointments'] = appointment.get_upcoming_appointments(profile_data['basic_data']['id'], datetime.today())

            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.dashboard'))


# Dashboard: Clear Selection
@bp.route("/clear-selection", methods=['GET', 'POST'])
def clear_selection():
    if session.get('ongoing_booking'):
        session.pop('ongoing_booking')
    elif session.get('list_of_doctors'):
        session.pop('list_of_doctors')
    elif session.get('available_slots'):
        session.pop('available_slots')
    return redirect(url_for('main.dashboard'))


# Communicate
@bp.route("/communicate", methods=['GET', 'POST'])
def communicate():
    if request.method == 'POST':
        appointment_member = request.form.get('appointment-member')
        communication_mode = request.form.get('communication-mode')

    return render_template("communicate.html", 
                           profile_data=session.get('profile_data')
                           )


# Profile
@bp.route("/profile")
def view_profile():
    members_data = session.get('members_data')
    
    members_appointment_data = []
    print(members_data)
    for member in members_data:
        members_appointment_data.append(
            {
                'id': member['id'],
                'name': member['first_name'] + ' ' + member['last_name'],
                'appointments': appointment.get_all_appointments(member['id'])
            }
        )
    
    print(members_appointment_data)
    
    return render_template("profile.html", 
                           profile_data=session.get('profile_data'),
                           members_data=members_data,
                           members_appointment_data=members_appointment_data,
                           appointment_data=session.get('appointment_data'), 
                           session_stats=session.get('session_stats')
                           )


# Profile: Add Member
@bp.route("/add-member", methods=['GET', 'POST'])
def add_member():
    profile_data = session.get('profile_data')
    if request.method == 'POST':
        member_data = {
            'first_name': request.form.get("first-name").capitalize(),
            'last_name': request.form.get("last-name").capitalize(),
            'birth_date': request.form.get("birth-date"),
            'gender': request.form.get("gender"),
            'city': request.form.get("city").capitalize(),
            'state': request.form.get("state").capitalize(),
            'email': request.form.get("email-address"),
            'mobile': request.form.get("mobile-number"),
            'relation': request.form.get("user-relation"),
            'is_doctor': False
        }

        if profile.create_profile(member_data):
            if profile.create_relation(profile_data["basic_data"]["id"], member_data["email"], member_data["relation"]):
                if profile_data['stats']['number_of_documents_uploaded'] >= 0:
                    profile_data['stats']['number_of_documents_uploaded'] += 1
                    profile.edit_profile(profile_data)
                return redirect(url_for('main.view_profile'))
            else:
                return redirect(url_for('main.add_member'))
        else:
            return redirect(url_for('main.add_member'))
    else:   
        return render_template("add_member.html", profile_data=profile_data)


# Profile: Upload Documents
@bp.route("/upload-documents", methods=['GET', 'POST'])
def upload_documents():
    if request.method == 'POST':
        file_name = request.form.get("document-name").capitalize()
        file = request.files['document']
        profile_data = session.get('profile_data')
        if not file:
            return render_template('profile.html', profile_data=profile_data)

        if profile.insert_document(file, file_name, profile_data['basic_data']['id']):
            return redirect(url_for('main.view_profile'))
        else:
            render_template('profile.html', profile_data=profile_data)
    else:
        return render_template('profile.html', profile_data=profile_data)


# Profile: View Documents
@bp.route("/view-document", methods=['POST'])
def view_documents():
    document_id = request.form.get('document-button')
    # Redirect to the GET endpoint to serve the document
    return redirect(url_for('main.get_document', document_id=document_id))


# Profile: Get Document
@bp.route("/get-document/<document_id>", methods=['GET'])
def get_document(document_id):
    profile_data = session.get('profile_data')
    
    # Locate the document in the user's session data
    for doc in profile_data['documents']:
        if doc['id'] == document_id:
            doc_content = profile.get_document(document_id)  # Fetch binary content
            return send_file(
                BytesIO(doc_content),
                mimetype='application/pdf',
                as_attachment=False,  # Opens inline
                download_name=doc['document_name']
            )
    
    # If document not found, redirect back to profile
    return redirect(url_for('main.view_profile'))


# Update Profile
@bp.route("/update-profile", methods=['GET', 'POST'])
def update_profile():
    return render_template("update_profile.html", profile_data=session.get('profile_data'))


# Update Profile: Update Basic Data
@bp.route("/update-basic-data", methods=['GET', 'POST'])
def update_basic_data():
    if request.method == 'POST':
        profile_data = session.get('profile_data')
        
        profile_data['basic_data']['profile_picture'] = request.files['profile-picture'].read()
        profile_data['basic_data']['first_name'] = request.form.get('first-name').capitalize()
        profile_data['basic_data']['last_name'] = request.form.get('last-name').capitalize()
        profile_data['basic_data']['birth_date'] = request.form.get("birth-date")
        profile_data['basic_data']['address'] = request.form.get("address").title()
        profile_data['basic_data']['city'] = request.form.get("city").capitalize()
        profile_data['basic_data']['state'] = request.form.get("state").capitalize()
        profile_data['basic_data']['mobile_number'] = request.form.get("mobile-number")

        if profile_data["basic_data"]["speciality"] != None:
            profile_data["basic_data"]["speciality"] = request.form.get("doctor-speciality")

        if not profile.edit_profile(profile_data["basic_data"]["id"], profile_data):
            return None

        return redirect(url_for('main.update_profile'))


# Update Profile: Update Health Data
@bp.route("/update-health-data", methods=['GET', 'POST'])
def update_health_data():
    if request.method == 'POST':
        profile_data = session.get('profile_data')
        
        profile_data["health_data"]["gender"] = request.form.get("gender")
        profile_data["health_data"]["blood_group"] = request.form.get("blood-group")
        profile_data["health_data"]["weight"] = request.form.get("weight")
        profile_data["health_data"]["height"] = request.form.get("height")
        profile_data["health_data"]["disability"] = request.form.get("disability")
        profile_data["health_data"]["fitzpatrick"] = request.form.get("fitzpatrick-skin-type")
        profile_data["health_data"]["allergies"] = request.form.get("allergies")
        profile_data["health_data"]["cancer"] = request.form.get("cancer")
        profile_data["health_data"]["diabetes"] = request.form.get("diabetes")
        profile_data["health_data"]["thyroid"] = request.form.get("thyroid")
        profile_data["health_data"]["covid"] = request.form.get("covid")
        profile_data["health_data"]["asthma"] = request.form.get("asthma")
        profile_data["health_data"]["hiv_aids"] = request.form.get("hiv-aids")
        profile_data["health_data"]["addiction"] = request.form.get("addiction")
        
        profile.edit_profile(profile_data["basic_data"]["id"], profile_data)

        return redirect(url_for('main.update_profile'))


# Update Profile: Update Login Data
@bp.route("/update-login-data", methods=['GET', 'POST'])
def update_login_data():
    if request.method == "POST":
        profile_data = session.get('profile_data')
        
        profile_data["basic_data"]["email"] = request.form.get("email-address")
        password = request.form.get("password")
        re_enter_password = request.form.get("re-enter-password")

        if password == re_enter_password:
            profile_data["basic_data"]["password"] = password
            profile.edit_profile(profile_data["basic_data"]["id"], profile_data)

        return redirect(url_for('main.update_profile'))


# Healthcare Chatbot
@bp.route("/healthcare-chatbot", methods=['GET', 'POST'])
def healthcare_chatbot():
    if request.method == 'POST':
        response = request.form.get('user-response').lower()
        chat_history = session.get('chat_history')
        
        message = {
            "sender": "User",
            "message": response,
            "timestamp": datetime.now()
        }
        
        chat_history['messages'].append(message)

        with open('disease_model.pkl', 'rb') as file:
            model = pickle.load(file)
            data = pd.read_csv('./Training.csv')
            X = data.iloc[:, :-1]
            symptoms = X.columns.tolist()

            user_symptoms = {symptom: 0 for symptom in symptoms}
            for symptom in symptoms:
                chat_history['messages'].append(f"Do you have {symptom.replace('_', ' ')}? (yes/no): ")
                if chat_history['messages'] == 'yes':
                    user_symptoms[symptom] = 1

            user_data = pd.DataFrame([user_symptoms])
            prediction = model.predict(user_data)[0]
            chat_history['messages'].append(f"\nBased on your symptoms, you may have: {prediction}")
            return redirect(url_for('main.dashboard'))