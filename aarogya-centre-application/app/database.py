from contextlib import closing
from flask_mail import Message
from datetime import date, datetime, timedelta
from pytz import timezone
from flask import current_app as app
from . import mysql
from . import mail
from .constants import TABLE_NAMES, GET_BASIC_DATA_FROM_EMAIL


# Fetch available tables from the database
def get_available_tables():
    with app.app_context():
        with closing(mysql.connection.cursor()) as cursor:
            cursor.execute('SHOW TABLES')
            database_tables = cursor.fetchall()
            return [table[0] for table in database_tables]


# Check schema required for the application
def check_schema():
    try:
        available_tables = get_available_tables()
        missing_tables = [table for table in TABLE_NAMES if table not in available_tables]
        
        if not available_tables:
            app.logger.warn('No required tables found!')
            app.logger.info('Creating required tables')
        elif missing_tables:
            app.logger.warn('Database does not contain all the required tables!')
            app.logger.info('Creating missing tables')

        if create_tables(TABLE_NAMES if not missing_tables else missing_tables):
            app.logger.info('Tables created successfully!')
            
    except Exception as error:
        app.logger.error(f"Database error: {error}")
    finally:
        app.logger.info('Required tables are checked!')
    return True


# Create tables that are required for the application
def create_tables(tables_to_create):
    sql_switcher = {
        'user_basic_data': '''CREATE TABLE user_basic_data (
                                user_id INT AUTO_INCREMENT PRIMARY KEY, 
                                profile_picture VARBINARY(256), 
                                first_name NVARCHAR(25), 
                                last_name NVARCHAR(25), 
                                birth_date DATE, 
                                home_address NVARCHAR(100), 
                                home_city NVARCHAR(25), 
                                mobile_number LONG, 
                                email_address NVARCHAR(50), 
                                password NVARCHAR(50), 
                                member_ids NVARCHAR(100), 
                                logged_in BOOLEAN
                            );''',
        'user_health_data': '''CREATE TABLE user_health_data (
                                user_id INT AUTO_INCREMENT PRIMARY KEY, 
                                gender NVARCHAR(25), 
                                age INT, 
                                blood_group NVARCHAR(10),
                                weight INT, 
                                height INT, 
                                obesity NVARCHAR(25), 
                                disability NVARCHAR(50), 
                                fitzpatrick NVARCHAR(50), 
                                allergies NVARCHAR(50),
                                diabetes NVARCHAR(50), 
                                thyroid NVARCHAR(50), 
                                cancer NVARCHAR(50), 
                                covid NVARCHAR(50), 
                                asthma NVARCHAR(50), 
                                hiv_aids NVARCHAR(50),
                                addiction NVARCHAR(50)
                            );''',
        'user_stats': '''CREATE TABLE user_stats (
                            user_id INT AUTO_INCREMENT PRIMARY KEY, 
                            account_created_on DATE, 
                            number_of_appointments INT,
                            number_of_virtual_appointments INT, 
                            number_of_documents_uploaded INT, 
                            number_of_members_added INT
                        );''',
        'user_documents': '''CREATE TABLE user_documents (
                                user_id INT AUTO_INCREMENT PRIMARY KEY, 
                                document_name NVARCHAR(50), 
                                document_path NVARCHAR(100)
                            );''',
        'doctor_basic_data': '''CREATE TABLE doctor_basic_data (
                                    doctor_id INT AUTO_INCREMENT PRIMARY KEY, 
                                    profile_picture VARBINARY(256),
                                    first_name NVARCHAR(25), 
                                    last_name NVARCHAR(25), 
                                    birth_date DATE, 
                                    home_address NVARCHAR(100), 
                                    home_city NVARCHAR(25),
                                    work_address NVARCHAR(100), 
                                    work_city NVARCHAR(25), 
                                    speciality NVARCHAR(50), 
                                    mobile_number LONG, 
                                    email_address NVARCHAR(50),
                                    password NVARCHAR(50), 
                                    member_ids NVARCHAR(100), 
                                    logged_in BOOLEAN
                                );''',
        'doctor_health_data': '''CREATE TABLE doctor_health_data (
                                    doctor_id INT AUTO_INCREMENT PRIMARY KEY, 
                                    gender NVARCHAR(25), 
                                    age INT, 
                                    blood_group NVARCHAR(10),
                                    weight INT, 
                                    height INT, 
                                    obesity NVARCHAR(25), 
                                    disability NVARCHAR(50), 
                                    fitzpatrick NVARCHAR(50), 
                                    allergies NVARCHAR(50),
                                    diabetes NVARCHAR(50), 
                                    thyroid NVARCHAR(50), 
                                    cancer NVARCHAR(50), 
                                    covid NVARCHAR(50), 
                                    asthma NVARCHAR(50), 
                                    hiv_aids NVARCHAR(50), 
                                    addiction NVARCHAR(50)
                                );''',
        'doctor_stats': '''CREATE TABLE doctor_stats (
                            doctor_id INT AUTO_INCREMENT PRIMARY KEY, 
                            account_created_on DATE, 
                            number_of_appointments INT, 
                            number_of_virtual_appointments INT, 
                            number_of_appointments_diagnosed INT, 
                            number_of_virtual_appointments_diagnosed INT, 
                            number_of_documents_uploaded INT, 
                            number_of_members_added INT
                        );''',
        'doctor_documents': '''CREATE TABLE doctor_documents (
                                doctor_id INT AUTO_INCREMENT PRIMARY KEY, 
                                document_name NVARCHAR(50), 
                                document_path NVARCHAR(100)
                            );''',
        'appointment_data': '''CREATE TABLE appointment_data (
                                appointment_id INT AUTO_INCREMENT PRIMARY KEY, 
                                mode NVARCHAR(25), 
                                user_id INT, 
                                user_name NVARCHAR(50), 
                                doctor_id INT, 
                                doctor_name NVARCHAR(50), 
                                specialist NVARCHAR(50), 
                                appointment_date DATE, 
                                appointment_time  NVARCHAR(25), 
                                appointment_address NVARCHAR(100), 
                                appointment_city NVARCHAR(25)
                            );'''
    }
    with app.app_context():
        with closing(mysql.connection.cursor()) as cursor:
            for table in tables_to_create:
                cursor.execute(sql_switcher.get(table))
            mysql.connection.commit()
    return True


# Create a profile inside database from the provided data
def create_profile(first_name, last_name, birth_date, gender, city, email, mobile, password, user_category, 
                   speciality, work_city):

    today = date.today()
    birthdate = birth_date.split("-")
    age = today.year - int(birthdate[0]) - ((today.month, today.day) < (int(birthdate[1]), int(birthdate[2])))

    if user_category == 'Normal':
        with closing(mysql.connection.cursor()) as cursor:
            cursor.execute(GET_BASIC_DATA_FROM_EMAIL, (email,))
            account = cursor.fetchone()

            if account:
                mysql.connection.commit()
                return False
            else:
                cursor.execute("INSERT INTO user_basic_data VALUES (NULL, NULL, %s, %s, %s, NULL, %s, %s, %s, %s, \
                               NULL, %s);", (first_name, last_name, birth_date, city, mobile, email, password, False,))
                cursor.execute("INSERT INTO user_health_data VALUES (NULL, %s, %s, NULL, NULL, NULL, \
                    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);", (gender, age,))
                cursor.execute("INSERT INTO user_stats VALUES (NULL, %s, 0, 0, 0, 0);", (today,))
                mysql.connection.commit()
                return True
    else:
        with closing(mysql.connection.cursor()) as cursor:
            cursor.execute("SELECT * FROM doctor_basic_data WHERE email_address = %s;", (email,))
            account = cursor.fetchone()

            if account:
                mysql.connection.commit()
                return False
            else:
                cursor.execute("INSERT INTO doctor_basic_data VALUES (NULL, NULL, %s, %s, %s, NULL, %s, \
                               NULL, %s, %s, %s, %s, %s, NULL, %s);", (first_name, last_name, birth_date, city, work_city, 
                                                                       speciality, mobile, email, password, False,))
                cursor.execute("INSERT INTO doctor_health_data VALUES (NULL, %s, %s, NULL, NULL, NULL, \
                               NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);", (gender, age,))
                cursor.execute("INSERT INTO doctor_stats VALUES (NULL, %s, 0, 0, 0, 0, 0, 0);", (today))
                mysql.connection.commit()
                return True


# Fetch an account using the provided credentials
def fetch_account(cursor, table_name, email, password):
    print(f"SELECT * FROM {table_name} WHERE email_address = '{email}' AND password = '{password}';")
    cursor.execute(f"SELECT * FROM aarogya_centre.{table_name} WHERE email_address = '{email}' AND password = '{password}';")
    return cursor.fetchone()


# Authenticate the user using the provided credentials
def authentication(email, password):
    with app.app_context():
        with closing(mysql.connection.cursor()) as cursor:
            user_account = fetch_account(cursor, 'user_basic_data', email, password)
            doctor_account = fetch_account(cursor, 'doctor_basic_data', email, password)

    if user_account:
        return True, 'Normal'
    elif doctor_account:
        return True, 'Doctor'
    return False, ''


# Collect basic data of the user 
def collect_basic_data(email, password, account_type):
    with closing(mysql.connection.cursor()) as cursor:
        if account_type == 'Normal':
            account = 'user'
        else:
            account = 'doctor'

        cursor.execute("SELECT * FROM %s_basic_data WHERE email_address = %s AND password = %s;", 
                       (account, email, password,))
        basic_data = list(cursor.fetchone())
        
        cursor.execute("SELECT CONVERT (profile_picture using utf8) FROM %s_basic_data WHERE %s_id = %s;", 
                       (account, account, basic_data[0],))
        profile_picture_path = list(cursor.fetchone())

        basic_data[1] = profile_picture_path[0]
        mysql.connection.commit()
    return basic_data


# Collect health data of the user
def collect_health_data(account_id, account_type):
    with closing(mysql.connection.cursor()) as cursor:
        if account_type == 'Normal':
            account = 'user'
        else:
            account = 'doctor'

        cursor.execute("SELECT * FROM %s_health_data WHERE %s_id = %s;", (account, account, account_id,))
        health_data = cursor.fetchone()
        mysql.connection.commit()
    return health_data


# Collect stats of the user
def collect_stats(account_id, account_type):
    with closing(mysql.connection.cursor()) as cursor:
        if account_type == 'Normal':
            account = 'user'
        else:
            account = 'doctor'

        cursor.execute("SELECT * FROM %s_stats WHERE %s_id = %s;", (account, account, account_id,))
        stats = cursor.fetchone()
        mysql.connection.commit()
    return stats


# Collect appointment data of the user
def collect_appointment_data(account_id, account_type):
    with closing(mysql.connection.cursor()) as cursor:
        if account_type == 'Normal':
            account = 'user'
        else:
            account = 'doctor'

        cursor.execute("SELECT * FROM appointment_data WHERE %s_id = %s;", (account, account_id,))
        appointment_data = cursor.fetchall()
        mysql.connection.commit()
    return appointment_data


# Collect documents of the user
def collect_documents(account_id, account_type):
    with closing(mysql.connection.cursor()) as cursor:
        if account_type == 'Normal':
            account = 'user'
        else:
            account = 'doctor'

        cursor.execute("SELECT * FROM %s_documents WHERE %s_id = %s;", (account, account, account_id,))
        documents = cursor.fetchall()
        
        cursor.execute("SELECT CONVERT (document_path using utf8) FROM %s_documents WHERE %s_id = %s;", 
                       (account, account, account_id,))
        document_path = cursor.fetchall()
        
        documents_data = []
        temp_list = []
        for data, path in zip(documents, document_path):
            temp_list = [data[0], data[1], path[0]]
            documents_data.append(temp_list)

        mysql.connection.commit()
    return documents_data


# Collect members of the user
def collect_member_data(account_id, account_type):
    with closing(mysql.connection.cursor()) as cursor:

        if account_type == 'Normal':
            cursor.execute("SELECT * FROM user_basic_data WHERE user_id = %s;", (account_id,))
            main_account = cursor.fetchone()

            id_string = main_account[10]
        else:
            cursor.execute("SELECT * FROM doctor_basic_data WHERE doctor_id = %s;", (account_id))
            main_account = cursor.fetchone()

            id_string = main_account[13]

        if id_string:
            member_string = id_string.split(" ")
            member_id = [int(member_string[i]) for i in range(1, len(member_string), 2)]
            member_relation = [member_string[i] for i in range(2, len(member_string) + 1, 2)]

            cursor.execute("SELECT * FROM user_basic_data WHERE user_id IN (%s);" % ','.join(['%s'] * len(member_id)), 
                           tuple(member_id)
            )
            member_data = cursor.fetchall()
            member_data = [list(data) + [relation] for data, relation in zip(member_data, member_relation)]
            return member_data
        else:
            member_data = []
        mysql.connection.commit()
        return member_data


# Calculate the percentage completion of profile
def profile_completion(account_type, basic_data, health_data, stats):
    count = 0
    for data in basic_data:
        if not data:
            count += 1
        
    for data in health_data:
        if not data:
            count += 1

    for data in stats:
        if data == 0:
            count += 1

    if account_type == 'Normal':
        complete_percentage = ((35 - count) / 35) * 100
    else:
        complete_percentage = ((40 - count) / 40) * 100

    return complete_percentage


# Fetch appropriate greeting message based on time
def greetings():
    ind_time = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S.%f').split(" ")
    time = ind_time[1].split(":")
    hour = int(time[0])

    if 5 <= hour < 12:
        return "Good Morning!"
    elif 12 <= hour < 16:
        return "Good Afternoon!"
    elif 16 <= hour < 22:
        return "Good Evening!"
    else:
        return "Good Night!"


# Collect necessary dates of the user
def dates(account_id, account_type):
    week_dates = []

    for count in range(1, 8):
        week_dates.append(str(date.today() + timedelta(days=count)))

    with closing(mysql.connection.cursor()) as cursor:

        if account_type == 'Normal':
            cursor.execute("SELECT account_created_on FROM user_stats WHERE user_id = %s;", (account_id,))
            account_date = cursor.fetchone()
        else:
            cursor.execute("SELECT account_created_on FROM doctor_stats WHERE doctor_id = %s;", (account_id,))
            account_date = cursor.fetchone()

        created_on = str(account_date[0]).split("-")

        delta = date.today() - date(int(created_on[0]), int(created_on[1]), int(created_on[2])) 

    return week_dates, delta.days


# Search doctors based on provided mode
def search_doctors(mode, city, doctor_category):
    with closing(mysql.connection.cursor()) as cursor:

        if mode == 'Home':
            cursor.execute("SELECT * FROM doctor_basic_data WHERE home_city = %s AND speciality = %s;", (city, doctor_category,))
            filtered_doctors = cursor.fetchall()
        elif mode == 'Virtual':
            cursor.execute("SELECT * FROM doctor_basic_data WHERE speciality = %s;", (doctor_category,))
            filtered_doctors = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM doctor_basic_data WHERE work_city = %s AND speciality = %s;", (city, doctor_category,))
            filtered_doctors = cursor.fetchall()

    doctor_names = []
    hospital_address = []
    for data in filtered_doctors:
        doctor_names.append(f"{data[2]} {data[3]}")
        if data[7]:
            hospital_address.append(f"{data[7].split(' | ')[0]}")
        else:
            hospital_address.append("")

    return zip(doctor_names, hospital_address)


# Check availability of appointment for the provided doctor
def check_availability(doctor, appointment_date):
    appointment_slots = ["10:00 AM - 10:30 AM", "10:30 AM - 11:00 AM", "11:00 AM - 11:30 AM",
                        "11:30 AM - 12:00 PM", "01:00 PM - 01:30 PM", "01:30 PM - 02:00 PM",
                        "02:00 PM - 02:30 PM", "02:30 PM - 03:00 PM", "03:00 PM - 03:30 PM",
                        "03:30 PM - 04:00 PM", "04:00 PM - 04:30 PM", "04:30 PM - 05:00 PM",
                        "06:00 PM - 06:30 PM", "06:30 PM - 07:00 PM", "07:00 PM - 07:30 PM",
                        "07:30 PM - 08:00 PM"]
        
    with closing(mysql.connection.cursor()) as cursor:

        cursor.execute("SELECT appointment_time FROM appointment_data WHERE doctor_name = %s AND appointment_date = %s;", 
                       (doctor, appointment_date,))
        time_slots = cursor.fetchall()

        busy_slots = []
        for time in time_slots:
            busy_slots.append(time[0])
        
        available_slots = []
        for slot in appointment_slots:
            if slot not in busy_slots:
                available_slots.append(slot)

        mysql.connection.commit()

    return available_slots


# Book appointment at the provided doctor
def book_appointment(appointment_data):
    with closing(mysql.connection.cursor()) as cursor:

        user_name = appointment_data[1].split(" ")
        cursor.execute("SELECT * FROM user_basic_data WHERE first_name = %s;", (user_name[0]))
        user_data = cursor.fetchone()

        doctor_name = appointment_data[4].split(" ")
        cursor.execute("SELECT * FROM doctor_basic_data WHERE first_name = %s;", (doctor_name[0]))
        doctor_data = cursor.fetchone()

        cursor.execute("INSERT INTO appointment_data VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", 
                       (appointment_data[0], user_data[0], appointment_data[1], doctor_data[0], appointment_data[4], 
                        appointment_data[3], appointment_data[5], appointment_data[6], appointment_data[7], 
                        appointment_data[2],))
        
        mysql.connection.commit()

    return doctor_data


# Add member to a profile
def add_user(first_name, last_name, birth_date, city, email, mobile, relation, basic_data, account_type):
    birthdate = birth_date.split("-")

    today = date.today()
    age = today.year - int(birthdate[0]) - ((today.month, today.day) < (int(birthdate[1]), int(birthdate[2])))

    if relation in ['Mother', 'Wife', 'Daughter', 'Sister']:
        gender = 'Female'
    else:
        gender = 'Male'

    with closing(mysql.connection.cursor()) as cursor:
        cursor.execute(GET_BASIC_DATA_FROM_EMAIL, (email,))
        user_account = cursor.fetchone()

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM doctor_basic_data WHERE email_address = %s;", (email,))
        doctor_account = cursor.fetchone()

        if user_account or doctor_account:
            mysql.connection.commit()

            return False
        else:
            cursor.execute("INSERT INTO user_basic_data VALUES (NULL, NULL, %s, %s, %s, NULL, %s, %s, %s, \
                           NULL, NULL, %s);", (first_name, last_name, birth_date, city, mobile, email, False))
            cursor.execute("INSERT INTO user_health_data VALUES (NULL, %s, %s, NULL, NULL, NULL, NULL, NULL, \
                           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);", (gender, age,))
            cursor.execute("INSERT INTO user_stats VALUES (NULL, %s, 0, 0, 0, 0);", (today,))

            cursor.execute(GET_BASIC_DATA_FROM_EMAIL, (email,))
            member_account = cursor.fetchone()

            member_ids = basic_data[10]

            if member_ids:
                member_ids += f' {member_account[0]} {relation}'
            else:
                member_ids = f' {member_account[0]} {relation}'

            if account_type == 'Normal':
                cursor.execute("UPDATE user_basic_data SET member_ids = %s WHERE user_id = %s;", 
                               (member_ids, basic_data[0],))
            else:
                cursor.execute("UPDATE doctor_basic_data SET member_ids = '[%s, %s]' WHERE doctor_id = %s;", 
                               (member_account[0], relation, basic_data[0],))

            mysql.connection.commit()
            return True


# Upload documents of a user
def upload_documents(account_type, account_id, document_name, document_path):
    with closing(mysql.connection.cursor()) as cursor:

        if account_type == 'Normal':
            account = 'user'
        else:
            account = 'doctor'

        cursor.execute("INSERT INTO %s_documents VALUES (%s, %s, %s);", 
                       (account, account_id, document_name, document_path))
        mysql.connection.commit()

    return True

    
# Update basic data of the user
def update_basic_data(account_id, account_type, basic_data):
    with closing(mysql.connection.cursor()) as cursor:

        birthdate = basic_data[4].split("-")

        today = date.today()
        age = today.year - int(birthdate[0]) - ((today.month, today.day) < (int(birthdate[1]), int(birthdate[2])))

        if account_type == 'Normal':
            cursor.execute("UPDATE user_basic_data SET profile_picture = %s, first_name = %s, last_name = %s, \
                           birth_date = %s, home_address = %s, home_city = %s, mobile_number = %s WHERE user_id = %s;", 
                           (basic_data[1], basic_data[2], basic_data[3], basic_data[4], basic_data[5], basic_data[6], 
                            basic_data[7], account_id,))
            cursor.execute("UPDATE user_health_data SET age = %s WHERE user_id = %s;", (age, account_id,))
            mysql.connection.commit()
            cursor.close()
        else:
            cursor.execute("UPDATE doctor_basic_data SET profile_picture = %s, first_name = %s, last_name = %s, \
                           birth_date = %s, home_address = %s, home_city = %s, work_address = %s, work_city = %s, \
                           specialist = %s, mobile_number = %s WHERE doctor_id = %s;", 
                           (basic_data[1], basic_data[2], basic_data[3], basic_data[4], basic_data[5], basic_data[6], 
                            basic_data[7], basic_data[8], basic_data[9], basic_data[10], account_id,))
            cursor.execute("UPDATE doctor_health_data SET age = %s WHERE doctor_id = %s;", (age, account_id,))
            mysql.connection.commit()

    return True


# Update health data of the user
def update_health_data(account_id, account_type, health_data):
    with closing(mysql.connection.cursor()) as cursor:

        if account_type == 'Normal':
            account = 'user'
        else:
            account = 'doctor'

        if health_data[4] and health_data[5]:
            height = int(health_data[5]) / 100
            bmi = int(health_data[4]) / height ** 2

            if bmi <= 18.5:
                obesity = 'Under Weight'
            elif bmi <= 24.9:
                obesity = 'Normal'
            elif bmi <= 29.9:
                obesity = 'Over Weight'
            else:
                obesity = 'Obese'
        else:
            health_data[3], health_data[4], health_data[5], obesity = 'Not Available'
        cursor.execute("UPDATE %s_health_data SET gender = %s, blood_group = %s, weight = %s, height = %s, \
                       obesity = %s, disability = %s, fitzpatrick = %s, allergies = %s, diabetes = %s, thyroid = %s, \
                       cancer = %s, covid = %s, asthma = %s, hiv_aids = %s, addiction = %s WHERE %s_id = %s;", 
                       (account, health_data[1], health_data[2], health_data[3], health_data[4], health_data[5], obesity,
                        health_data[7], health_data[8], health_data[9], health_data[10], health_data[11], health_data[12],
                        health_data[13], health_data[14], health_data[15], health_data[16], account, account_id,))

        mysql.connection.commit()

    return True


# Update login data of the user
def update_login_data(account_id, account_type, email, password):
    with closing(mysql.connection.cursor()) as cursor:

        if account_type == 'Normal':
            cursor.execute("UPDATE user_basic_data SET email_address = %s, password = %s WHERE user_id = %s;", 
                           (email, password, account_id,))
            mysql.connection.commit()
        else:
            cursor.execute("UPDATE doctor_basic_data SET email_address = %s, password = %s WHERE doctor_id = %s;", 
                           (email, password, account_id,))
            mysql.connection.commit()

    return True


# Update stats of the user
def update_stats(account_id, account_type, stats):
    with closing(mysql.connection.cursor()) as cursor:

        if account_type == 'Normal':
            cursor.execute("UPDATE user_stats SET number_of_appointments = %s, number_of_virtual_appointments = %s, \
                            number_of_documents_uploaded = %s, number_of_members_added = %s WHERE user_id = %s;", 
                            (stats[2], stats[3], stats[4], stats[5], account_id,))
            mysql.connection.commit()
        else:
            cursor.execute("UPDATE doctor_stats SET number_of_appointments = %s, number_of_virtual_appointments = %s, \
                            number_of_appointments_diagnosed = %s, number_of_virtual_appointments_diagnosed = %s, \
                            number_of_documents_uploaded = %s, number_of_members_added = %s WHERE doctor_id = %s;", 
                            (stats[2], stats[3], stats[4], stats[5], stats[6], stats[7], account_id,))
            mysql.connection.commit()

    return True


# Send Email
def send_mail(recipient, subject, body):
    msg = Message(subject, sender = 'contact.aarogyacentre@gmail.com', recipients = [recipient])
    msg.body = body
    mail.send(msg)

    return True