from flask import Blueprint, render_template, redirect, url_for, send_from_directory, request
from datetime import datetime

import app.utils as utils
import app.services.schema_service as schema
import app.services.user_service as user
import app.services.appointment_service as appointment

import math
from werkzeug.utils import secure_filename
import os

import numpy as np
import pandas as pd
from sklearn.tree import _tree
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

bp = Blueprint('main', __name__)

globals = {
    "data": None,
    "greetings": None,
    "completion_percentage": None,
    "chat_history": None,
    "appointment_data": None,
    "list_of_doctors": None,
    "available_slots": None,
    "account_age": None,
    "account_type": None,
    "basic_data": None,
    "health_data": None,
    "stats": None,
    "documents": None,
    "member_basic_data": None,
    "member_health_data": None,
    "member_stats": None,
    "member_appointment_data": None,
    "home_address": None,
    "work_address": None,
    "week_dates": None,
    "delta_days": None,
    "upcoming_appointment": None,
    "upcoming_virtual": None,
    "temporary_appointment_data": None,
    "doctor_details": None,
    "hospital_address": None,
    "tree_": None,
    "feature_name": None,
    "name": None,
    "threshold": None,
    "node": None,
    "depth": None,
    "labelencoder": None,
    "dimensionality_reduction": None,
    "doctors": None,
    "symptoms_present": None,
    "flag": None,
    "form_flag": None,
}


# Home
@bp.route("/")
def home():
    schema.check_schema()
    
    globals["data"] = None
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
                user.create_profile(profile_data)
            elif profile_data['user_category'] == 'Doctor':
                profile_data['is_doctor'] = True
                user.create_profile(profile_data)
            else:
                pass
            return render_template("login.html")
        else:
            return redirect(url_for('main.register'))
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

        id = user.authentication(login_data)
        if id:
            data = user.get_profile(id)
            if data:
                data.get("basic_data")["logged_in"] = True
                user.update_profile(id, data)
                
                print(datetime.today())
                
                globals["data"] = data
                globals['greetings'] = utils.greetings()
                
                current_date = datetime.today().strftime("%Y-%m-%d")
                account_created_on = globals['data']['stats']['account_created_on']
                globals["account_age"] = datetime.strptime(current_date, "%Y-%m-%d") - datetime.strptime(str(account_created_on), "%Y-%m-%d")
                
                globals['completion_percentage'] = utils.profile_completion(data)
                globals['upcoming_appointments'] = appointment.get_upcoming_appointments(id, datetime.today())
                globals['chat_history'] = {
                    "user_id": id,
                    "messages": [
                        {
                            "sender": "Bot",
                            "message": "Welcome to healthcare chatbot. How can I help you today?",
                            "timetamp": datetime.now()
                        }
                    ]
                }

            return redirect(url_for('main.dashboard'))
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")


# Dashboard
@bp.route("/dashboard")
def dashboard():
    
    return render_template("dashboard.html",
                           data=globals["data"],
                           greetings=globals["greetings"],
                           chat_history=globals["chat_history"], 
                           appointment_data=globals["appointment_data"],
                           list_of_doctors=globals["list_of_doctors"],
                           member_basic_data=[], 
                           upcoming_appointment=[],
                           upcoming_virtual=[],
                           week_dates=[], 
                           delta_days=globals["account_age"],
                           temporary_appointment_data=[], 
                           available_slots=globals["available_slots"], 
                           virtual=0, 
                           chat_length=10, flag=True, form_flag=False)


# Dashboard: Search Doctors
@bp.route("/search-doctors", methods=['GET', 'POST'])
def search_doctors():
    if request.method == 'POST':
        mode = request.form.get("appointment-mode")
        member_id = request.form.get("appointment-member")
        city = request.form.get("appointment-city").capitalize()
        doctor_category = request.form.get("appointment-doctor-category")
        
        member_data = user.get_profile(member_id)
        
        if mode == 'Hospital':
            globals["appointment_data"] = {
                "mode": mode,
                "user_id": member_id,
                "user_name": member_data["data"]["basic_data"]["first_name"] + ' ' + member_data["data"]["basic_data"]["last_name"],
                "appointment_city": city,
                "specialist": doctor_category
            }
        elif mode == 'Home':
            globals["appointment_data"] = {
                "mode": mode,
                "user_id": member_id,
                "user_name": member_data["data"]["basic_data"]["first_name"] + ' ' + member_data["data"]["basic_data"]["last_name"],
                "appointment_address": member_data["data"]["basic_data"]["address"],
                "appointment_city": member_data["data"]["basic_data"]["city"],
                "appointment_state": member_data["data"]["basic_data"]["state"],
                "specialist": doctor_category
            }
        else:
            globals["appointment_data"] = {
                "mode": mode,
                "user_id": member_id,
                "user_name": member_data["data"]["basic_data"]["first_name"] + ' ' + member_data["data"]["basic_data"]["last_name"],
                "appointment_address": "Virtual",
                "appointment_city": "Virtual",
                "appointment_state": "Virtual",
                "specialist": doctor_category 
            }

        globals["list_of_doctors"] = user.get_doctors(mode, globals["appointment_data"]["appointment_city"], doctor_category)
        
    return redirect(url_for('main.dashboard'))


# Dashboard: Check Appointment Availability
@bp.route("/check-availability", methods=['GET', 'POST'])
def check_availability():
    if request.method == 'POST':
        selected_doctor = request.form.get("appointment-doctor")
        appointment_date = request.form.get("appointment-date")

        globals["available_slots"] = appointment.check_availability(selected_doctor, appointment_date)
        for doctor in globals["list_of_doctors"]:
            if doctor['doctor_name'] == selected_doctor:
                globals["appointment_data"]["doctor_id"] = doctor['doctor_id']
        globals["appointment_data"]["doctor_name"] = selected_doctor
        globals["appointment_data"]["appointment_date"] = appointment_date
        
        if globals["appointment_data"]["mode"] == "Hospital":
            doctor_data = user.get_profile(globals["appointment_data"]["doctor_id"])
            globals["appointment_data"]["appointment_address"] = doctor_data["data"]["basic_data"]["address"]
            globals["appointment_data"]["appointment_address"] = doctor_data["data"]["basic_data"]["state"]
        
        return redirect(url_for('main.dashboard'))


# Dashboard: Book Appointment
@bp.route("/book-appointment", methods=['GET', 'POST'])
def book_appointment():    
    if request.method == 'POST':
        appointment_time = request.form.get("appointment-time")
        globals["appointment_data"]["appointment_time"] = appointment_time

        if appointment.create_appointment(globals["appointment_data"]):
            if globals["appointment_data"]["mode"] == 'Virtual':
                globals["data"]["stats"]["number_of_virtual_appointments"] += 1
            else:
                globals["data"]["stats"]["number_of_appointments"] += 1
            
            user.update_profile(globals["data"]["basic_data"]["id"], globals["data"])
            globals["appointment_data"] = None
            globals["list_of_doctors"] = None
            globals["available_slots"] = None

            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.dashboard'))


# Communicate
@bp.route("/communicate", methods=['GET', 'POST'])
def communicate():
    # if request.method == 'POST':
    #     appointment_member = request.form.get('appointment-member')
    #     communication_mode = request.form.get('communication-mode')

    return render_template("communicate.html", basic_data=basic_data, member_basic_data=member_basic_data)


# Profile
@bp.route("/profile")
def profile():

    # if account_type == 'Normal':
    #     basic_fields = ('', '', 'First Name', 'Last Name', 'Birth Date', 'Address', 'City', 'Mobile', 
    #                         'Email')
    # else:
    #     basic_fields = ('', '', 'First Name', 'Last Name', 'Birth Date', 'Address', 'City', 'Work Add', 'Work City', 
    #                         'Specialisation', 'Mobile', 'Email')

    # complete_percentage = math.ceil(database.profile_completion(account_type, basic_data, health_data, stats))

    return render_template("profile.html", 
                           data=globals["data"],
                           appointment_data=globals['appointment_data'], 
                           documents=None,
                           member_basic_data=None, 
                           member_appointment_data=None,
                           home_address=None, 
                           work_address=None, 
                           complete_percentage=globals['completion_percentage'],
                           basic_fields=None, 
                           length=1
                           )


# Profile: Add Member
@bp.route("/add-member", methods=['GET', 'POST'])
def add_member():
    # global basic_data, account_type, stats

    if request.method == 'POST':
        # first_name = request.form.get("first-name").capitalize()
        # last_name = request.form.get("last-name").capitalize()
        # birth_date = request.form.get("birth-date")
        # city = request.form.get("city").capitalize()
        # email = request.form.get("email-address")
        # mobile = request.form.get("mobile-number")
        # relation = request.form.get("user-relation")

        # if database.add_user(first_name, last_name, birth_date, city, email, mobile, relation, 
        #     basic_data, account_type=account_type):

        #     if account_type == 'Normal':
        #         stats[5] += 1
        #     else:
        #         stats[7] += 1

        #     database.update_stats(basic_data[0], account_type, stats)

        #     return redirect(url_for('profile'))
        # else:
            return redirect(url_for('add_member'))
    else:   
        return render_template("add_member.html", basic_data=basic_data)


# Profile: Upload Documents
@bp.route("/upload-documents", methods=['GET', 'POST'])
def upload_documents():
    global stats, documents

    if request.method == 'POST':
        # document_name = request.form.get('document-name').title()
        # document = request.files['document']

        # if document and not document.filename == '':
        #     def allowed_file(file_name):
        #         return '.' in file_name and file_name.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'pdf'}

        #     if allowed_file(document.filename):
        #         filename = secure_filename(document.filename)

        #         if account_type == 'Normal':
        #             path = f'./aarogya-centre-application/AarogyaCentreFlask/static/documents/user/{basic_data[0]}'

        #             if not os.path.exists(path):
        #                 os.mkdir(path)

        #             document_path  = os.path.join(f'{path}/', filename)
        #         else:
        #             document_path  = os.path.join('./aarogya-centre-application/AarogyaCentreFlask/static/documents/doctor/', filename)

        #         document.save(document_path)

        #         if database.upload_documents(account_type, basic_data[0], document_name, document_path):

        #             documents = database.collect_documents(basic_data[0], account_type)

        #             if account_type == 'Normal':
        #                 stats[4] += 1
        #             else:
        #                 stats[6] += 1

        #             database.update_stats(basic_data[0], account_type, stats)

        return redirect(url_for('main.profile'))
    else:
        return render_template('upload_documents.html', basic_data=None)


# Profile: View Documents
@bp.route("/view-document", methods=['GET', 'POST'])
def view_documents():
    if request.method == 'POST':
        # document_path = request.form.get('document-button')

        # workingdir = os.path.abspath(os.getcwd())

        # if account_type == 'Normal':
        #     temp_path = document_path[40:]
        #     file_details = temp_path.split("/")
        #     filepath = workingdir + f'./aarogya-centre-application/AarogyaCentreFlask/static/documents/user/{file_details[2]}/'
        #     filename = file_details[3]    
        # else:
        #     temp_path = document_path[43:]
        #     file_details = temp_path.split("/")

        #     filepath = workingdir + f'./aarogya-centre-application/AarogyaCentreFlask/static/documents/doctor/{file_details[0]}/'
        #     filename = file_details[1]

        return send_from_directory(filepath, filename)


# # Update Profile
# @app.route("/update-profile", methods=['GET', 'POST'])
# def update_profile():
#     global account_type, home_address, work_address

#     if account_type == 'Normal':
#         if basic_data[5]:
#             home_address = basic_data[5].split(" | ")
#             work_address = ["", "", ""]
#         else:
#             home_address = ["", "", ""]
#             work_address = ["", "", ""]
#     else:
#         if basic_data[5]:
#             home_address = basic_data[5].split(" | ")
#         else:
#             home_address = ["", "", ""]

#         if basic_data[7]:
#             work_address = basic_data[7].split(" | ")
#         else:
#             work_address = ["", "", ""]

#     return render_template("update_profile.html", account_type=account_type, basic_data=basic_data, health_data=health_data,
#                                 home_address=home_address, work_address=work_address)


# # Update Profile: Update Basic Data
# @app.route("/update-basic-data", methods=['GET', 'POST'])
# def update_basic_data():
#     global account_type, basic_data

#     if request.method == 'POST':
#         profile_picture = request.files["profile-picture"]
#         first_name = request.form.get("first-name").capitalize()
#         last_name = request.form.get("last-name").capitalize()
#         birth_date = request.form.get("birth-date")
#         address_first = request.form.get("address-first").title()
#         address_second = request.form.get("address-second").title()
#         address_third = request.form.get("address-third").title()
#         city = request.form.get("city").capitalize()
#         mobile_number = request.form.get("mobile-number")

#         if profile_picture and not profile_picture.filename == '':
#             def allowed_file(file_name):
#                 return '.' in file_name and file_name.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

#             if allowed_file(profile_picture.filename):
#                 filename = secure_filename(profile_picture.filename)

#                 if account_type == 'Normal':
#                     profile_picture_path  = os.path.join('./aarogya-centre-application/AarogyaCentreFlask/static/profile_picture/user/', filename)
#                 else:
#                     profile_picture_path  = os.path.join('./aarogya-centre-application/AarogyaCentreFlask/static/profile_picture/doctor/', filename)

#                 profile_picture.save(profile_picture_path)

#                 basic_data[1] = profile_picture_path[32:]

#         if account_type == 'Doctor':
#             work_address_first = request.form.get("work-address-first").title()
#             work_address_second = request.form.get("work-address-second").title()
#             work_address_third = request.form.get("work-address-third").title()
#             work_city = request.form.get("work-city").capitalize()
#             specialization = request.form.get("doctor-speciality")

#             h_address = address_first + ' | ' + address_second + ' | ' + address_third
#             w_address = work_address_first + ' | ' + work_address_second + ' | ' + work_address_third
#             basic_variables = ['', '', first_name, last_name, birth_date, h_address, city, w_address, work_city, specialization, mobile_number]

#             for i in range(2, 11):
#                 basic_data[i] = basic_variables[i]

#             database.update_basic_data(basic_data[0], account_type, basic_data)
#         else:
#             h_address = address_first + ' | ' + address_second + ' | ' + address_third
#             basic_variables = ['', '', first_name, last_name, birth_date, h_address, city, mobile_number]

#             for i in range(2, 8):
#                 basic_data[i] = basic_variables[i]
        
#             database.update_basic_data(basic_data[0], account_type, basic_data)

#         return redirect(url_for('update_profile'))


# # Update Profile: Update Health Data
# @app.route("/update-health-data", methods=['GET', 'POST'])
# def update_health_data():
#     global account_type, health_data

#     if request.method == 'POST':
#         gender = request.form.get("gender")
#         blood_group = request.form.get("blood-group")
#         weight = request.form.get("weight")
#         height = request.form.get("height")
#         disability = request.form.get("disability")
#         fitzpatrick = request.form.get("fitzpatrick-skin-type")
#         allergies = request.form.get("allergies")
#         cancer = request.form.get("cancer")
#         diabetes = request.form.get("diabetes")
#         thyroid = request.form.get("thyroid")
#         covid = request.form.get("covid")
#         asthma = request.form.get("asthma")
#         hiv_aids = request.form.get("hiv-aids")
#         addiction = request.form.get("addiction")

#         health_variables = [health_data[0], gender, health_data[2], blood_group, weight, height, health_data[6], disability, \
#                             fitzpatrick, allergies, diabetes, thyroid, cancer, covid, asthma, hiv_aids, addiction]

#         for i in range(1, 17):
#             health_data[i] = health_variables[i]

#         database.update_health_data(health_data[0], account_type, health_data)

#         return redirect(url_for('update_profile'))


# # Update Profile: Update Login Data
# @app.route("/update-login-data", methods=['GET', 'POST'])
# def update_login_data():
#     global account_type, basic_data

#     if request.method == "POST":
#         email = request.form.get("email-address")
#         password = request.form.get("password")
#         re_enter_password = request.form.get("re-enter-password")

#         if password == re_enter_password:
#             database.update_login_data(basic_data[0], account_type, email, password)

#         return redirect(url_for('update_profile'))


# # Healthcare Chatbot
# @app.route("/healthcare-chatbot", methods=['GET', 'POST'])
# def healthcare_chatbot():
#     global chat_history, threshold, node, depth, dimensionality_reduction, doctors, flag, form_flag

#     if request.method == 'POST':
#         response = request.form.get('user-response').lower()
#         chat_history.append(['User', response])

#         if response == 'start' or response == 'diagnose':
#             flag = True
#             form_flag = True
#             chat_history.append(['Bot', 'Please enter yes/no for the questions provided below.'])
#             classifier, cols = train_chatbot()
#             tree_to_code(classifier, cols)
#             recurse(node, depth)
#             return redirect(url_for('dashboard'))
#         elif response == 'end' or response == 'stop':
#             flag = False
#             form_flag = False
#             return redirect(url_for('dashboard'))


# # Healthcare Chatbot: Train Chatbot
# def train_chatbot():
#     global labelencoder, dimensionality_reduction, doctors

#     training_dataset = pd.read_csv('./Training.csv')
#     test_dataset = pd.read_csv('./Testing.csv')

#     X = training_dataset.iloc[:, 0:132].values
#     y = training_dataset.iloc[:, -1].values

#     dimensionality_reduction = training_dataset.groupby(training_dataset['prognosis']).max()

#     labelencoder = LabelEncoder()
#     y = labelencoder.fit_transform(y)

#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 0)
    
#     classifier = DecisionTreeClassifier()
#     classifier.fit(X_train, y_train)

#     cols = training_dataset.columns
#     cols = cols[:-1]

#     importances = classifier.feature_importances_
#     indices = np.argsort(importances)[::-1]
#     features = cols

#     doc_dataset = pd.read_csv('./aarogya-centre-application/AarogyaCentreFlask/doctors_dataset.csv', names=['Name', 'Description'])

#     diseases = dimensionality_reduction.index
#     diseases = pd.DataFrame(diseases)

#     doctors = pd.DataFrame()
#     doctors['name'] = np.nan
#     doctors['link'] = np.nan
#     doctors['disease'] = np.nan

#     doctors['disease'] = diseases['prognosis']


#     doctors['name'] = doc_dataset['Name']
#     doctors['link'] = doc_dataset['Description']

#     record = doctors[doctors['disease'] == 'AIDS']
#     record['name']
#     record['link']

#     return classifier, cols


# # Healthcare Chatbot: Tree to Code
# def tree_to_code(tree, feature_names):
#     global tree_, feature_name

#     tree_ = tree.tree_

#     feature_name = [
#         feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
#         for i in tree_.feature
#     ]


# # Healthcare Chatbot: Recurse
# def recurse(node, depth):
#     global name, threshold, symptoms_present

#     indent = "  " * depth

#     if tree_.feature[node] != _tree.TREE_UNDEFINED:
#         name = feature_name[node]
#         threshold = tree_.threshold[node]

#         chat_history.append(['Bot', name + ' ?'])

#         return redirect(url_for('dashboard'))
#     else:
#         disease = print_disease(tree_.value[node])
#         chat_history.append(['Bot', f'You may have { disease[0] }'])

#         red_cols = dimensionality_reduction.columns
#         symptoms_given = red_cols[dimensionality_reduction.loc[disease].values[0].nonzero()]

#         chat_history.append(['Bot', f'Symptoms present {str(list(symptoms_present)[0])}'])
#         chat_history.append(['Bot', f'symptoms given {str(list(symptoms_given))}'])

#         confidence_level = ((1.0*len(symptoms_present))/len(symptoms_given))*100
#         chat_history.append(['Bot', f'Accuracy level is {str(round(confidence_level, 2))}%'])

#         row = doctors[doctors['disease'] == disease[0]]
#         chat_history.append(['Bot', f'The model suggests to consult {str(row["name"].values[0])}'])

#         chat_history.append(['Bot', "Welcome to healthcare chatbot. How can I help you today? To diagnose enter \
#                             'start' or enter 'diagnose'"])

#         return redirect(url_for('dashboard'))


# Healthcare Chatbot: Get Response
@bp.route("/get-response", methods=['GET', 'POST'])
def get_response():
    # global chat_history, node, depth, threshold, flag

    # if request.method == 'POST':
    #     response = request.form.get('user-response').lower()
    #     chat_history.append(['User', response])

    #     if response == 'yes':
    #         val = 1
    #         flag = False
    #     else:
    #         val = 0

    #     if val <= threshold:
    #         node += 1
    #         depth += 1
    #         recurse(tree_.children_left[node], depth)
    #     else:
    #         node += 1
    #         depth += 1
    #         symptoms_present.append(name)
    #         recurse(tree_.children_right[node], depth)

    return redirect(url_for('dashboard'))


# Healthcare Chatbot: Print Disease
def print_disease(node):
    # global labelencoder

    # node = node[0]
    # val = node.nonzero()

    # disease = labelencoder.inverse_transform(val[0])

    return disease