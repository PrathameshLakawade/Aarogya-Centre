from asyncio.windows_events import NULL
from AarogyaCentreFlask import app
from AarogyaCentreFlask import database 
from flask import render_template, request, redirect, url_for, send_from_directory
import math
from werkzeug.utils import secure_filename
import os

import numpy as np
import pandas as pd
from sklearn.tree import _tree
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


global account_type, basic_data, health_data, stats, appointment_data, documents, \
    member_basic_data, member_health_data, member_stats, member_appointment_data, \
    greetings, home_address, work_address, week_dates, delta_days, upcoming_appointment, upcoming_virtual, complete_percentage, \
    temporary_appointment_data, available_slots, doctor_details, hospital_address, \
    chat_history, tree_, feature_name, name, threshold, node, depth, labelencoder, dimensionality_reduction, doctors, symptoms_present, \
    flag, form_flag


# Home
@app.route("/")
def home():
    database.check_schema()
    return render_template("home.html")


# Register
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        first_name = request.form.get("first-name").capitalize()
        last_name = request.form.get("last-name").capitalize()
        birth_date = request.form.get("birth-date")
        gender = request.form.get("gender")
        city = request.form.get("city").capitalize()
        email = request.form.get("email-address")
        mobile = request.form.get("mobile-number")
        password = request.form.get("password")
        re_password = request.form.get("re-enter-password")
        user_category = request.form.get("user-category")
        speciality = request.form.get("doctor-speciality")
        work_city = request.form.get("work-city").capitalize()

        if password == re_password:
            if database.create_profile(first_name, last_name, birth_date, gender, city, email, mobile, password, 
                user_category, speciality, work_city):
                return render_template("login.html")
            else:
                return redirect(url_for('register'))
        else:
            return redirect(url_for('register'))
    else:
        return render_template("register.html")


# Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    global account_type, basic_data, health_data, stats, appointment_data, documents, \
        member_basic_data, member_health_data, member_stats, member_appointment_data, \
        greetings, home_address, work_address, week_dates, delta_days, upcoming_appointment, upcoming_virtual, complete_percentage, \
        temporary_appointment_data, available_slots, doctor_details, hospital_address, \
        chat_history, tree_, feature_name, name, threshold, node, depth, labelencoder, dimensionality_reduction, doctors, symptoms_present, \
        flag, form_flag

    if request.method == "POST":

        email = request.form.get("user-email")
        password = request.form.get("user-password")

        account, account_type = database.authentication(email, password)

        if account:
            basic_data = database.collect_basic_data(email, password, account_type)

            account_id = basic_data[0]

            health_data = list(database.collect_health_data(account_id, account_type))
            stats = list(database.collect_stats(account_id, account_type))
            appointment_data = list(database.collect_appointment_data(account_id, account_type))
            documents = list(database.collect_documents(account_id, account_type))

            member_basic_data = list(database.collect_member_data(account_id, account_type))
            
            member_health_data = []
            member_stats = []
            member_appointment_data = []
            for member in member_basic_data: 
                member_health_data.append(list(database.collect_health_data(member[0], 'Normal')))
                member_stats.append(list(database.collect_stats(member[0], 'Normal')))
                member_appointment_data.append(list(database.collect_appointment_data(member[0], 'Normal')))

            greetings = database.greetings()

            if account_type == 'Normal':
                if basic_data[5]:
                    home_address = basic_data[5].split(" | ")
                    work_address = ["", "", ""]
                else:
                    home_address = ["", "", ""]
                    work_address = ["", "", ""]
            else:
                if basic_data[5]:
                    home_address = basic_data[5].split(" | ")
                else:
                    home_address = ["", "", ""]

                if basic_data[7]:
                    work_address = basic_data[7].split(" | ")
                else:
                    work_address = ["", "", ""]

            week_dates, delta_days = database.dates(account_id, account_type)

            complete_percentage = math.ceil(database.profile_completion(account_type, basic_data, health_data, stats))

            upcoming_appointment = []
            upcoming_virtual = []
            
            temporary_appointment_data = []
            available_slots = []
            doctor_details = []
            hospital_address = ''

            tree_ = NULL
            feature_name = NULL
            name = NULL
            threshold = NULL
            node = 0
            depth = 1
            labelencoder = NULL
            dimensionality_reduction = NULL
            doctors = NULL
            symptoms_present = []

            flag = False
            form_flag = False


            chat_history = [['Bot', "Welcome to healthcare chatbot. How can I help you today? To diagnose enter \
                            'start' or enter 'diagnose'"]]

            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    global appointment_data, upcoming_appointment, upcoming_virtual

    upcoming_appointment = []
    upcoming_virtual = []

    for date in week_dates:
        for data in appointment_data:
            if date == data[7] and data[1] == 'Virtual':
                upcoming_virtual.append(data)
                break
        
        if upcoming_virtual:
            break

    for date in week_dates:
        for data in appointment_data:
            if date == data[7] and data[1] != 'Virtual':
                upcoming_appointment.append(data)
                break

        if upcoming_appointment:
            break
    
    if stats[2] != 0 and stats[3] != 0:
        virtual = math.ceil((stats[3] / stats[2]) * 100)
        virtual = math.ceil(virtual / 0.28)
    elif stats[2] != 0 and stats[3] == 0:
        virtual = 0
    else:
        virtual = 179

    return render_template("dashboard.html", account_type=account_type, basic_data=basic_data, stats=stats, appointment_data=appointment_data,
                            member_basic_data=member_basic_data, upcoming_appointment=upcoming_appointment, upcoming_virtual=upcoming_virtual,
                            greetings=greetings, week_dates=week_dates, delta_days=delta_days,
                            temporary_appointment_data=temporary_appointment_data, available_slots=available_slots, doctor_details=doctor_details,
                            virtual=virtual, chat_history=chat_history, chat_length=len(chat_history), flag=flag, form_flag=form_flag)


# Dashboard: Search Doctors
@app.route("/search-doctors", methods=['GET', 'POST'])
def search_doctors():
    global temporary_appointment_data, doctor_details

    if request.method == 'POST':
        mode = request.form.get("appointment-mode")
        member = request.form.get("appointment-member")
        city = request.form.get("appointment-city").capitalize()
        doctor_category = request.form.get("appointment-doctor-category")
        
        if mode == 'Hospital':
            temporary_appointment_data = [mode, member, city, doctor_category]
        elif mode == 'Home':
            temporary_appointment_data = [mode, member, basic_data[6], doctor_category]
        else:
            temporary_appointment_data = [mode, member, 'Virtual', doctor_category]
            
        doctor_details = database.search_doctors(mode, temporary_appointment_data[2], doctor_category)

    return redirect(url_for('dashboard'))


# Dashboard: Check Appointment Availability
@app.route("/check-availability", methods=['GET', 'POST'])
def check_availability():
    global temporary_appointment_data, available_slots, hospital_address

    if request.method == 'POST':
        selected_doctor = request.form.get("appointment-doctor")
        appointment_date = request.form.get("appointment-date")

        selected_doctor = selected_doctor.split(" | ")
        hospital_address = selected_doctor[1]     

        available_slots = database.check_availability(selected_doctor[0], appointment_date)

        temporary_appointment_data.append(selected_doctor[0])
        temporary_appointment_data.append(appointment_date)
        
        return redirect(url_for('dashboard'))


# Dashboard: Book Appointment
@app.route("/book-appointment", methods=['GET', 'POST'])
def book_appointment():
    global stats, appointment_data, \
        member_stats, member_appointment_data, \
        temporary_appointment_data, doctor_details, hospital_address
    
    if request.method == 'POST':
        appointment_time = request.form.get("appointment-time")

        temporary_appointment_data.append(appointment_time)

        if temporary_appointment_data[0] == 'Hospital':
            temporary_appointment_data.append(hospital_address)
        elif temporary_appointment_data[0] == 'Home':
            temporary_appointment_data.append(home_address[1])
        else:
            temporary_appointment_data.append('Virtual')

        doctor_data =  database.book_appointment(temporary_appointment_data)
        if temporary_appointment_data[1] == f"{basic_data[2]} {basic_data[3]}":
            stats[2] += 1

            if temporary_appointment_data[0] == 'Virtual':
                stats[3] += 1

            database.update_stats(basic_data[0], account_type, stats)
            stats = list(database.collect_stats(basic_data[0], account_type))

            appointment_data = database.collect_appointment_data(basic_data[0], account_type)
        else:
            member_name = temporary_appointment_data[1].split(" ")
            
            for member in member_basic_data:
                if member_name[0] == member[2]:
                    for m_stats in member_stats:
                        if m_stats[0] == member[0]:
                            m_stats[2] += 1

                            if temporary_appointment_data[0] == 'Virtual':
                                m_stats[3] += 1

                            database.update_stats(member[0], 'Normal', m_stats)

            member_stats = []
            member_appointment_data = []
            for member in member_basic_data: 
                member_stats.append(list(database.collect_stats(member[0], 'Normal'))) 
                member_appointment_data.append(database.collect_appointment_data(member[0], 'Normal'))

        doctor_stats = list(database.collect_stats(doctor_data[0], 'Doctor'))
        doctor_stats[4] += 1

        if temporary_appointment_data[0] == 'Virtual':
            doctor_stats[5] += 1

        database.update_stats(doctor_data[0], 'Doctor', doctor_stats)

        temporary_appointment_data.clear()
        available_slots.clear()

        recent_appointment = appointment_data[-1]
        subject = 'Appointment Booked Successfully'
        body = f'''Your appointment has been booked successfully. Your appointment details are as follows:\n
Appointment ID: {recent_appointment[0]}
Mode of Appointment: {recent_appointment[1]}
Patient Name: {recent_appointment[3]}
Doctor Name: {recent_appointment[5]}
Doctor's Specialisation: {recent_appointment[6]}
Appointment Date: {recent_appointment[7]}
Appointment Time: {recent_appointment[8]}
Appointment Address: {recent_appointment[9]}
Appointment City: {recent_appointment[10]}'''
        database.send_mail(basic_data[8], subject, body)

        return redirect(url_for('dashboard'))


# Dashboard: Clear Temporary Appointment Data
@app.route("/clear-temporary-appointment-data", methods=['GET', 'POST'])
def clear_temporary_appointment_data():
    global temporary_appointment_data, available_slots, hospital_address

    if request.method == 'POST':
        temporary_appointment_data.clear()
        available_slots.clear()

    return redirect(url_for('dashboard'))


# Communicate
@app.route("/communicate", methods=['GET', 'POST'])
def communicate():
    if request.method == 'POST':
        appointment_member = request.form.get('appointment-member')
        communication_mode = request.form.get('communication-mode')

    return render_template("communicate.html", basic_data=basic_data, member_basic_data=member_basic_data)


# Profile
@app.route("/profile")
def profile():

    if account_type == 'Normal':
        basic_fields = ('', '', 'First Name', 'Last Name', 'Birth Date', 'Address', 'City', 'Mobile', 
                            'Email')
    else:
        basic_fields = ('', '', 'First Name', 'Last Name', 'Birth Date', 'Address', 'City', 'Work Add', 'Work City', 
                            'Specialisation', 'Mobile', 'Email')

    complete_percentage = math.ceil(database.profile_completion(account_type, basic_data, health_data, stats))

    return render_template("profile.html", account_type=account_type, basic_data=basic_data, health_data=health_data, stats=stats, appointment_data=appointment_data, documents=documents,
                            member_basic_data=member_basic_data, member_appointment_data=member_appointment_data,
                            home_address=home_address, work_address=work_address, complete_percentage=complete_percentage,
                            basic_fields=basic_fields, length=len(member_appointment_data))


# Profile: Add Member
@app.route("/add-member", methods=['GET', 'POST'])
def add_member():
    global basic_data, account_type, stats

    if request.method == 'POST':
        first_name = request.form.get("first-name").capitalize()
        last_name = request.form.get("last-name").capitalize()
        birth_date = request.form.get("birth-date")
        city = request.form.get("city").capitalize()
        email = request.form.get("email-address")
        mobile = request.form.get("mobile-number")
        relation = request.form.get("user-relation")

        if database.add_user(first_name, last_name, birth_date, city, email, mobile, relation, 
            basic_data, account_type=account_type):

            if account_type == 'Normal':
                stats[5] += 1
            else:
                stats[7] += 1

            database.update_stats(basic_data[0], account_type, stats)

            return redirect(url_for('profile'))
        else:
            return redirect(url_for('add_member'))
    else:   
        return render_template("add_member.html", basic_data=basic_data)


# Profile: Upload Documents
@app.route("/upload-documents", methods=['GET', 'POST'])
def upload_documents():
    global stats, documents

    if request.method == 'POST':
        document_name = request.form.get('document-name').title()
        document = request.files['document']

        if document and not document.filename == '':
            def allowed_file(file_name):
                return '.' in file_name and file_name.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'pdf'}

            if allowed_file(document.filename):
                filename = secure_filename(document.filename)

                if account_type == 'Normal':
                    path = f'/Aarogya-Centre/AarogyaCentreFlask/static/documents/user/{basic_data[0]}'

                    if not os.path.exists(path):
                        os.mkdir(path)

                    document_path  = os.path.join(f'{path}/', filename)
                else:
                    document_path  = os.path.join('/Aarogya-Centre/AarogyaCentreFlask/static/documents/doctor/', filename)

                document.save(document_path)

                if database.upload_documents(account_type, basic_data[0], document_name, document_path):

                    documents = database.collect_documents(basic_data[0], account_type)

                    if account_type == 'Normal':
                        stats[4] += 1
                    else:
                        stats[6] += 1

                    database.update_stats(basic_data[0], account_type, stats)

        return redirect(url_for('profile'))
    else:
        return render_template('upload_documents.html', basic_data=basic_data)


# Profile: View Documents
@app.route("/view-document", methods=['GET', 'POST'])
def view_documents():
    if request.method == 'POST':
        document_path = request.form.get('document-button')

        workingdir = os.path.abspath(os.getcwd())

        if account_type == 'Normal':
            temp_path = document_path[40:]
            file_details = temp_path.split("/")
            filepath = workingdir + f'/Aarogya-Centre/AarogyaCentreFlask/static/documents/user/{file_details[2]}/'
            filename = file_details[3]    
        else:
            temp_path = document_path[43:]
            file_details = temp_path.split("/")

            filepath = workingdir + f'/Aarogya-Centre/AarogyaCentreFlask/static/documents/doctor/{file_details[0]}/'
            filename = file_details[1]

        return send_from_directory(filepath, filename)


# Update Profile
@app.route("/update-profile", methods=['GET', 'POST'])
def update_profile():
    global account_type, home_address, work_address

    if account_type == 'Normal':
        if basic_data[5]:
            home_address = basic_data[5].split(" | ")
            work_address = ["", "", ""]
        else:
            home_address = ["", "", ""]
            work_address = ["", "", ""]
    else:
        if basic_data[5]:
            home_address = basic_data[5].split(" | ")
        else:
            home_address = ["", "", ""]

        if basic_data[7]:
            work_address = basic_data[7].split(" | ")
        else:
            work_address = ["", "", ""]

    return render_template("update_profile.html", account_type=account_type, basic_data=basic_data, health_data=health_data,
                                home_address=home_address, work_address=work_address)


# Update Profile: Update Basic Data
@app.route("/update-basic-data", methods=['GET', 'POST'])
def update_basic_data():
    global account_type, basic_data

    if request.method == 'POST':
        profile_picture = request.files["profile-picture"]
        first_name = request.form.get("first-name").capitalize()
        last_name = request.form.get("last-name").capitalize()
        birth_date = request.form.get("birth-date")
        address_first = request.form.get("address-first").title()
        address_second = request.form.get("address-second").title()
        address_third = request.form.get("address-third").title()
        city = request.form.get("city").capitalize()
        mobile_number = request.form.get("mobile-number")

        if profile_picture and not profile_picture.filename == '':
            def allowed_file(file_name):
                return '.' in file_name and file_name.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

            if allowed_file(profile_picture.filename):
                filename = secure_filename(profile_picture.filename)

                if account_type == 'Normal':
                    profile_picture_path  = os.path.join('/Aarogya-Centre/AarogyaCentreFlask/static/profile_picture/user/', filename)
                else:
                    profile_picture_path  = os.path.join('/Aarogya-Centre/AarogyaCentreFlask/static/profile_picture/doctor/', filename)

                profile_picture.save(profile_picture_path)

                basic_data[1] = profile_picture_path[32:]

        if account_type == 'Doctor':
            work_address_first = request.form.get("work-address-first").title()
            work_address_second = request.form.get("work-address-second").title()
            work_address_third = request.form.get("work-address-third").title()
            work_city = request.form.get("work-city").capitalize()
            specialization = request.form.get("doctor-speciality")

            h_address = address_first + ' | ' + address_second + ' | ' + address_third
            w_address = work_address_first + ' | ' + work_address_second + ' | ' + work_address_third
            basic_variables = ['', '', first_name, last_name, birth_date, h_address, city, w_address, work_city, specialization, mobile_number]

            for i in range(2, 11):
                basic_data[i] = basic_variables[i]

            database.update_basic_data(basic_data[0], account_type, basic_data)
        else:
            h_address = address_first + ' | ' + address_second + ' | ' + address_third
            basic_variables = ['', '', first_name, last_name, birth_date, h_address, city, mobile_number]

            for i in range(2, 8):
                basic_data[i] = basic_variables[i]
        
            database.update_basic_data(basic_data[0], account_type, basic_data)

        return redirect(url_for('update_profile'))


# Update Profile: Update Health Data
@app.route("/update-health-data", methods=['GET', 'POST'])
def update_health_data():
    global account_type, health_data

    if request.method == 'POST':
        gender = request.form.get("gender")
        blood_group = request.form.get("blood-group")
        weight = request.form.get("weight")
        height = request.form.get("height")
        disability = request.form.get("disability")
        fitzpatrick = request.form.get("fitzpatrick-skin-type")
        allergies = request.form.get("allergies")
        cancer = request.form.get("cancer")
        diabetes = request.form.get("diabetes")
        thyroid = request.form.get("thyroid")
        covid = request.form.get("covid")
        asthma = request.form.get("asthma")
        hiv_aids = request.form.get("hiv-aids")
        addiction = request.form.get("addiction")

        health_variables = [health_data[0], gender, health_data[2], blood_group, weight, height, health_data[6], disability, \
                            fitzpatrick, allergies, diabetes, thyroid, cancer, covid, asthma, hiv_aids, addiction]

        for i in range(1, 17):
            health_data[i] = health_variables[i]

        database.update_health_data(health_data[0], account_type, health_data)

        return redirect(url_for('update_profile'))


# Update Profile: Update Login Data
@app.route("/update-login-data", methods=['GET', 'POST'])
def update_login_data():
    global account_type, basic_data

    if request.method == "POST":
        email = request.form.get("email-address")
        password = request.form.get("password")
        re_enter_password = request.form.get("re-enter-password")

        if password == re_enter_password:
            database.update_login_data(basic_data[0], account_type, email, password)

        return redirect(url_for('update_profile'))


# Healthcare Chatbot
@app.route("/healthcare-chatbot", methods=['GET', 'POST'])
def healthcare_chatbot():
    global chat_history, threshold, node, depth, dimensionality_reduction, doctors, flag, form_flag

    if request.method == 'POST':
        response = request.form.get('user-response').lower()
        chat_history.append(['User', response])

        if response == 'start' or response == 'diagnose':
            flag = True
            form_flag = True
            chat_history.append(['Bot', 'Please enter yes/no for the questions provided below.'])
            classifier, cols = train_chatbot()
            tree_to_code(classifier, cols)
            recurse(node, depth)
            return redirect(url_for('dashboard'))
        elif response == 'end' or response == 'stop':
            flag = False
            form_flag = False
            return redirect(url_for('dashboard'))


# Healthcare Chatbot: Train Chatbot
def train_chatbot():
    global labelencoder, dimensionality_reduction, doctors

    training_dataset = pd.read_csv('AarogyaCentre/AarogyaCentreFlask/Training.csv')
    test_dataset = pd.read_csv('AarogyaCentre/AarogyaCentreFlask/Testing.csv')

    X = training_dataset.iloc[:, 0:132].values
    y = training_dataset.iloc[:, -1].values

    dimensionality_reduction = training_dataset.groupby(training_dataset['prognosis']).max()

    labelencoder = LabelEncoder()
    y = labelencoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 0)
    
    classifier = DecisionTreeClassifier()
    classifier.fit(X_train, y_train)

    cols = training_dataset.columns
    cols = cols[:-1]

    importances = classifier.feature_importances_
    indices = np.argsort(importances)[::-1]
    features = cols

    doc_dataset = pd.read_csv('AarogyaCentre/AarogyaCentreFlask/doctors_dataset.csv', names=['Name', 'Description'])

    diseases = dimensionality_reduction.index
    diseases = pd.DataFrame(diseases)

    doctors = pd.DataFrame()
    doctors['name'] = np.nan
    doctors['link'] = np.nan
    doctors['disease'] = np.nan

    doctors['disease'] = diseases['prognosis']


    doctors['name'] = doc_dataset['Name']
    doctors['link'] = doc_dataset['Description']

    record = doctors[doctors['disease'] == 'AIDS']
    record['name']
    record['link']

    return classifier, cols


# Healthcare Chatbot: Tree to Code
def tree_to_code(tree, feature_names):
    global tree_, feature_name

    tree_ = tree.tree_

    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]


# Healthcare Chatbot: Recurse
def recurse(node, depth):
    global name, threshold, symptoms_present

    indent = "  " * depth

    if tree_.feature[node] != _tree.TREE_UNDEFINED:
        name = feature_name[node]
        threshold = tree_.threshold[node]

        chat_history.append(['Bot', name + ' ?'])

        return redirect(url_for('dashboard'))
    else:
        disease = print_disease(tree_.value[node])
        chat_history.append(['Bot', f'You may have { disease[0] }'])

        red_cols = dimensionality_reduction.columns
        symptoms_given = red_cols[dimensionality_reduction.loc[disease].values[0].nonzero()]

        chat_history.append(['Bot', f'Symptoms present {str(list(symptoms_present)[0])}'])
        chat_history.append(['Bot', f'symptoms given {str(list(symptoms_given))}'])

        confidence_level = ((1.0*len(symptoms_present))/len(symptoms_given))*100
        chat_history.append(['Bot', f'Accuracy level is {str(round(confidence_level, 2))}%'])

        row = doctors[doctors['disease'] == disease[0]]
        chat_history.append(['Bot', f'The model suggests to consult {str(row["name"].values[0])}'])

        chat_history.append(['Bot', "Welcome to healthcare chatbot. How can I help you today? To diagnose enter \
                            'start' or enter 'diagnose'"])

        return redirect(url_for('dashboard'))


# Healthcare Chatbot: Get Response
@app.route("/get-response", methods=['GET', 'POST'])
def get_response():
    global chat_history, node, depth, threshold, flag

    if request.method == 'POST':
        response = request.form.get('user-response').lower()
        chat_history.append(['User', response])

        if response == 'yes':
            val = 1
            flag = False
        else:
            val = 0

        if val <= threshold:
            node += 1
            depth += 1
            recurse(tree_.children_left[node], depth)
        else:
            node += 1
            depth += 1
            symptoms_present.append(name)
            recurse(tree_.children_right[node], depth)

    return redirect(url_for('dashboard'))


# Healthcare Chatbot: Print Disease
def print_disease(node):
    global labelencoder

    node = node[0]
    val = node.nonzero()

    disease = labelencoder.inverse_transform(val[0])

    return disease