from flask_mysqldb import MySQL
from datetime import date, datetime, timedelta
from pytz import timezone
from AarogyaCentreFlask import app
from flask_mail import Mail, Message

# Constants for database configurations
DATABASE_SECRET_KEY = 'AarogyaCentre'
DATABASE_HOST = 'localhost'
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'root@00'
DATABASE_NAME = 'aarogya_centre'    

# Constants for email configurations
SENDER_SERVER = 'smtp.gmail.com'
SENDER_PORT = 465
SENDER_EMAIL_ADDRESS = 'contact.aarogyacentre@gmail.com'
SENDER_PASSWORD = 'aarogya@2022'

# Constants for names of the different tables
USER_BASIC_DATA = 'user_basic_data'
USER_HEALTH_DATA = 'user_health_data'
USER_STATS = 'user_stats'
USER_DOCUMENTS = 'user_documents'
DOCTOR_BASIC_DATA = 'doctor_basic_data'
DOCTOR_HEALTH_DATA = 'doctor_health_data'
DOCTOR_STATS = 'doctor_stats'
DOCTOR_DOCUMENTS = 'doctor_documents'
APPOINTMENT_DATA = 'appointment_data'

# Constant for list of the table names
LIST_OF_TABLES = [USER_BASIC_DATA, USER_HEALTH_DATA, USER_STATS, USER_DOCUMENTS, DOCTOR_BASIC_DATA, DOCTOR_HEALTH_DATA, DOCTOR_STATS, DOCTOR_DOCUMENTS, APPOINTMENT_DATA]

# Database configuration
app.secret_key = DATABASE_SECRET_KEY
app.config["MYSQL_HOST"] = DATABASE_HOST
app.config["MYSQL_USER"] = DATABASE_USER
app.config["MYSQL_PASSWORD"] = DATABASE_PASSWORD
app.config["MYSQL_DB"] = DATABASE_NAME
mysql = MySQL(app)

# Email configuration
app.config["MAIL_SERVER"] = SENDER_SERVER
app.config["MAIL_PORT"] = SENDER_PORT
app.config["MAIL_USERNAME"] = SENDER_EMAIL_ADDRESS
app.config["MAIL_PASSWORD"] = SENDER_PASSWORD
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)


# Function to check the schema before starting the application
def check_schema():
    try:
        available_tables= get_available_tables()

        if not available_tables:
            app.logger.warn('No required tables found!')
            app.logger.info('Creating required tables')
            if create_tables(LIST_OF_TABLES):
                app.logger.info('Required tables created successfully!')
        else:
            missing_tables = [table for table in LIST_OF_TABLES if table not in available_tables]
            if missing_tables:
                app.logger.warn('Database does not contain all the required tables!')
                app.logger.info('Creating missing tables')
                if create_tables(missing_tables):
                    app.logger.info('Missing tables created successfully!')

    except (mysql.connection.Error, mysql.connection.Warning) as error:
        app.logger.error(error)
    finally:
        app.logger.info('Required tables are checked!')
    return True


# Function to fetch the available tables from the database
def get_available_tables():
    cursor = mysql.connection.cursor()
    cursor.execute('SHOW TABLES')
    database_tables = cursor.fetchall()
    available_tables = [table[0] for table in database_tables]
    mysql.connection.commit()
    cursor.close()
    return available_tables


# Function to create tables that are required for proper functioning of the application
def create_tables(tables_to_create):
    sql_switcher = {
        USER_BASIC_DATA: f'CREATE TABLE {USER_BASIC_DATA} (user_id INT AUTO_INCREMENT PRIMARY KEY, profile_picture VARBINARY(256), \
                            first_name NVARCHAR(25), last_name NVARCHAR(25), birth_date DATE, home_address NVARCHAR(100), home_city NVARCHAR(25), \
                            mobile_number LONG, email_address NVARCHAR(50), password NVARCHAR(50), member_ids NVARCHAR(100), logged_in BOOLEAN);',
        USER_HEALTH_DATA: f'CREATE TABLE {USER_HEALTH_DATA} (user_id INT AUTO_INCREMENT PRIMARY KEY, gender NVARCHAR(25), age INT, blood_group NVARCHAR(10), \
                            weight INT, height INT, obesity NVARCHAR(25), disability NVARCHAR(50), fitzpatrick NVARCHAR(50), allergies NVARCHAR(50), \
                            diabetes NVARCHAR(50), thyroid NVARCHAR(50), cancer NVARCHAR(50), covid NVARCHAR(50), asthma NVARCHAR(50), hiv_aids NVARCHAR(50), \
                            addiction NVARCHAR(50));',
        USER_STATS: f'CREATE TABLE {USER_STATS} (user_id INT AUTO_INCREMENT PRIMARY KEY, account_created_on DATE, number_of_appointments INT, \
                        number_of_virtual_appointments INT, number_of_documents_uploaded INT, number_of_members_added INT);',
        USER_DOCUMENTS: f'CREATE TABLE {USER_DOCUMENTS} (user_id INT AUTO_INCREMENT PRIMARY KEY, document_name NVARCHAR(50), document_path NVARCHAR(100));',
        DOCTOR_BASIC_DATA: f'CREATE TABLE {DOCTOR_BASIC_DATA} (doctor_id INT AUTO_INCREMENT PRIMARY KEY, profile_picture VARBINARY(256), \
                            first_name NVARCHAR(25), last_name NVARCHAR(25), birth_date DATE, home_address NVARCHAR(100), home_city NVARCHAR(25), \
                            work_address NVARCHAR(100), work_city NVARCHAR(25), speciality NVARCHAR(50), mobile_number LONG, email_address NVARCHAR(50), \
                            password NVARCHAR(50), member_ids NVARCHAR(100), logged_in BOOLEAN);',
        DOCTOR_HEALTH_DATA: f'CREATE TABLE {DOCTOR_HEALTH_DATA} (doctor_id INT AUTO_INCREMENT PRIMARY KEY, gender NVARCHAR(25), age INT, blood_group NVARCHAR(10), \
                            weight INT, height INT, obesity NVARCHAR(25), disability NVARCHAR(50), fitzpatrick NVARCHAR(50), allergies NVARCHAR(50), \
                            diabetes NVARCHAR(50), thyroid NVARCHAR(50), cancer NVARCHAR(50), covid NVARCHAR(50), asthma NVARCHAR(50), hiv_aids NVARCHAR(50), \
                            addiction NVARCHAR(50));',
        DOCTOR_STATS: f'CREATE TABLE {DOCTOR_STATS} (doctor_id INT AUTO_INCREMENT PRIMARY KEY, account_created_on DATE, number_of_appointments INT, \
                        number_of_virtual_appointments INT, number_of_appointments_diagnosed INT, number_of_virtual_appointments_diagnosed INT, \
                        number_of_documents_uploaded INT, number_of_members_added INT);',
        DOCTOR_DOCUMENTS: f'CREATE TABLE {DOCTOR_DOCUMENTS} (doctor_id INT AUTO_INCREMENT PRIMARY KEY, document_name NVARCHAR(50), document_path NVARCHAR(100));',
        APPOINTMENT_DATA: f'CREATE TABLE {APPOINTMENT_DATA} (appointment_id INT AUTO_INCREMENT PRIMARY KEY, mode NVARCHAR(25), user_id INT, user_name NVARCHAR(50), \
                            doctor_id INT, doctor_name NVARCHAR(50), specialist NVARCHAR(50), appointment_date DATE, appointment_time  NVARCHAR(25), \
                            appointment_address NVARCHAR(100), appointment_city NVARCHAR(25));'
    }

    cursor = mysql.connection.cursor()
    for table in tables_to_create:
        cursor.execute(sql_switcher.get(table))
    mysql.connection.commit()
    cursor.close()
    return True


# Function to save the created profile data into the database
def create_profile(first_name, last_name, birth_date, gender, city, email, mobile, password, user_category, speciality, work_city):
    birthdate = birth_date.split("-")

    today = date.today()
    age = today.year - int(birthdate[0]) - ((today.month, today.day) < (int(birthdate[1]), int(birthdate[2])))

    if user_category == 'Normal':
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT * FROM user_basic_data WHERE email_address = '{email}';")
        account = cursor.fetchone()

        if account:
            mysql.connection.commit()
            cursor.close()

            return False
        else:
            cursor.execute(f"INSERT INTO user_basic_data VALUES (NULL, NULL, '{first_name}', '{last_name}', '{birth_date}', \
                NULL, '{city}', '{mobile}', '{email}', '{password}', NULL, {False});")
            cursor.execute(f"INSERT INTO user_health_data VALUES (NULL, '{gender}', '{age}', NULL, NULL, NULL, \
                NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);")
            cursor.execute(f"INSERT INTO user_stats VALUES (NULL, '{today}', 0, 0, 0, 0);")
            mysql.connection.commit()
            cursor.close()

            return True
    else:
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT * FROM doctor_basic_data WHERE email_address = '{email}';")
        account = cursor.fetchone()

        if account:
            mysql.connection.commit()
            cursor.close()

            return False
        else:
            cursor.execute(f"INSERT INTO doctor_basic_data VALUES (NULL, NULL, '{first_name}', '{last_name}', '{birth_date}', \
                NULL, '{city}', NULL, '{work_city}', '{speciality}', '{mobile}', '{email}', '{password}', NULL, {False});")
            cursor.execute(f"INSERT INTO doctor_health_data VALUES (NULL, '{gender}', '{age}', NULL, NULL, NULL, \
                NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);")
            cursor.execute(f"INSERT INTO doctor_stats VALUES (NULL, '{today}', 0, 0, 0, 0, 0, 0);")
            mysql.connection.commit()
            cursor.close()

            return True


# Function to authenticate the user
def authentication(email, password):
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM user_basic_data WHERE email_address = '{email}' AND password = '{password}';")
    user_account = cursor.fetchone()

    cursor.execute(f"SELECT * FROM doctor_basic_data WHERE email_address = '{email}' AND password = '{password}';")
    doctor_account = cursor.fetchone()

    mysql.connection.commit()
    cursor.close()

    if user_account or doctor_account:
        if user_account:
            account_type = 'Normal'
            return True, account_type
        else:
            account_type = 'Doctor'
            return True, account_type
    else:
        account_type = ''
        return False, account_type


# Login: Collect Basic Data 
def collect_basic_data(email, password, account_type):
    cursor = mysql.connection.cursor()

    if account_type == 'Normal':
        account = 'user'
    else:
        account = 'doctor'

    cursor.execute(f"SELECT * FROM {account}_basic_data WHERE email_address = '{email}' AND password = '{password}';")
    basic_data = list(cursor.fetchone())
    
    cursor.execute(f"SELECT CONVERT (profile_picture using utf8) FROM {account}_basic_data WHERE {account}_id = {basic_data[0]};")
    profile_picture_path = list(cursor.fetchone())

    basic_data[1] = profile_picture_path[0]
    mysql.connection.commit()
    cursor.close()

    return basic_data


# Login: Collect Health Data
def collect_health_data(account_id, account_type):
    cursor = mysql.connection.cursor()

    if account_type == 'Normal':
        account = 'user'
    else:
        account = 'doctor'

    cursor.execute(f"SELECT * FROM {account}_health_data WHERE {account}_id = {account_id};")
    health_data = cursor.fetchone()

    mysql.connection.commit()
    cursor.close()

    return health_data


# Login: Collect Stats
def collect_stats(account_id, account_type):
    cursor = mysql.connection.cursor()

    if account_type == 'Normal':
        account = 'user'
    else:
        account = 'doctor'

    cursor.execute(f"SELECT * FROM {account}_stats WHERE {account}_id = {account_id};")
    stats = cursor.fetchone()

    mysql.connection.commit()
    cursor.close()

    return stats


# Login: Collect Appointment Data
def collect_appointment_data(account_id, account_type):
    cursor = mysql.connection.cursor()

    if account_type == 'Normal':
        account = 'user'
    else:
        account = 'doctor'

    cursor.execute(f"SELECT * FROM appointment_data WHERE {account}_id = {account_id};")
    appointment_data = cursor.fetchall()

    mysql.connection.commit()
    cursor.close()

    return appointment_data


# Login: Collect Documents
def collect_documents(account_id, account_type):
    cursor = mysql.connection.cursor()

    if account_type == 'Normal':
        account = 'user'
    else:
        account = 'doctor'

    cursor.execute(f"SELECT * FROM {account}_documents WHERE {account}_id = {account_id};")
    documents = cursor.fetchall()
    
    cursor.execute(f"SELECT CONVERT (document_path using utf8) FROM {account}_documents WHERE {account}_id = {account_id};")
    document_path = cursor.fetchall()
    
    documents_data = []
    temp_list = []
    for data, path in zip(documents, document_path):
        temp_list = [data[0], data[1], path[0]]
        documents_data.append(temp_list)

    mysql.connection.commit()
    cursor.close()

    return documents_data


# Login: Collect Member Data
def collect_member_data(account_id, account_type):
    cursor = mysql.connection.cursor()

    if account_type == 'Normal':
        cursor.execute(f"SELECT * FROM user_basic_data WHERE user_id = {account_id};")
        main_account = cursor.fetchone()

        id_string = main_account[10]
    else:
        cursor.execute(f"SELECT * FROM doctor_basic_data WHERE doctor_id = {account_id};")
        main_account = cursor.fetchone()

        id_string = main_account[13]

    if id_string:
        member_string = id_string.split(" ")

        str_member_id = []
        for _ in range(1, len(member_string), 2):
            str_member_id.append(member_string[_])

        member_id = []
        for id in str_member_id:
            member_id.append(int(id))

        member_relation = []
        for _ in range(2, len(member_string) + 1, 2):
            member_relation.append(member_string[_])

        data = []
        for id in member_id:
            cursor.execute(f"SELECT * FROM user_basic_data WHERE user_id = {id};")
            data.append(cursor.fetchone())

        member_data = []
        for i in data:
            member_data.append(list(i))

        for data, relation in zip(member_data, member_relation):
            data.append(relation)

        mysql.connection.commit()
        cursor.close()

        return member_data
    else:
        member_data = []

        mysql.connection.commit()
        cursor.close()

        return member_data


# Login: Profile Completion
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


# Login: Greetings
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


# Login: Dates
def dates(account_id, account_type):
    week_dates = []

    for count in range(1, 8):
        week_dates.append(str(date.today() + timedelta(days=count)))

    cursor = mysql.connection.cursor()

    if account_type == 'Normal':
        cursor.execute(f"SELECT account_created_on FROM user_stats WHERE user_id = {account_id};")
        account_date = cursor.fetchone()
    else:
        cursor.execute(f"SELECT account_created_on FROM doctor_stats WHERE doctor_id = {account_id};")
        account_date = cursor.fetchone()

    created_on = str(account_date[0]).split("-")

    delta = date.today() - date(int(created_on[0]), int(created_on[1]), int(created_on[2])) 

    return week_dates, delta.days


# Dashboard: Search Doctors
def search_doctors(mode, city, doctor_category):
    cursor = mysql.connection.cursor()

    if mode == 'Home':
        cursor.execute(f"SELECT * FROM doctor_basic_data WHERE home_city = '{city}' AND speciality = '{doctor_category}';")
        filtered_doctors = cursor.fetchall()
    elif mode == 'Virtual':
        cursor.execute(f"SELECT * FROM doctor_basic_data WHERE speciality = '{doctor_category}';")
        filtered_doctors = cursor.fetchall()
    else:
        cursor.execute(f"SELECT * FROM doctor_basic_data WHERE work_city = '{city}' AND speciality = '{doctor_category}';")
        filtered_doctors = cursor.fetchall()
    
    mysql.connection.commit()
    cursor.close()

    doctor_names = []
    hospital_address = []
    for data in filtered_doctors:
        doctor_names.append(f"{data[2]} {data[3]}")
        if data[7]:
            hospital_address.append(f"{data[7].split(' | ')[0]}")
        else:
            hospital_address.append("")

    return zip(doctor_names, hospital_address)


# Dashboard: Check Appointment Availability
def check_availability(doctor, appointment_date):
    appointment_slots = ["10:00 AM - 10:30 AM", "10:30 AM - 11:00 AM", "11:00 AM - 11:30 AM",
                        "11:30 AM - 12:00 PM", "01:00 PM - 01:30 PM", "01:30 PM - 02:00 PM",
                        "02:00 PM - 02:30 PM", "02:30 PM - 03:00 PM", "03:00 PM - 03:30 PM",
                        "03:30 PM - 04:00 PM", "04:00 PM - 04:30 PM", "04:30 PM - 05:00 PM",
                        "06:00 PM - 06:30 PM", "06:30 PM - 07:00 PM", "07:00 PM - 07:30 PM",
                        "07:30 PM - 08:00 PM"]
        
    cursor = mysql.connection.cursor()

    cursor.execute(f"SELECT appointment_time FROM appointment_data WHERE doctor_name = '{doctor}' AND appointment_date = '{appointment_date}';")
    time_slots = cursor.fetchall()

    busy_slots = []
    for time in time_slots:
        busy_slots.append(time[0])
    
    available_slots = []
    for slot in appointment_slots:
        if slot not in busy_slots:
            available_slots.append(slot)

    mysql.connection.commit()
    cursor.close()

    return available_slots


# Dashboard: Book Appointment
def book_appointment(appointment_data):
    cursor = mysql.connection.cursor()

    user_name = appointment_data[1].split(" ")
    cursor.execute(f"SELECT * FROM user_basic_data WHERE first_name = '{user_name[0]}';")
    user_data = cursor.fetchone()

    doctor_name = appointment_data[4].split(" ")
    cursor.execute(f"SELECT * FROM doctor_basic_data WHERE first_name = '{doctor_name[0]}';")
    doctor_data = cursor.fetchone()

    cursor.execute(f"INSERT INTO appointment_data VALUES (NULL, '{appointment_data[0]}', {user_data[0]}, '{appointment_data[1]}', \
                    {doctor_data[0]}, '{appointment_data[4]}', '{appointment_data[3]}', '{appointment_data[5]}', '{appointment_data[6]}', \
                    '{appointment_data[7]}', '{appointment_data[2]}');")
    
    mysql.connection.commit()
    cursor.close()

    return doctor_data


# Profile: Add Member
def add_user(first_name, last_name, birth_date, city, email, mobile, relation, basic_data, account_type):
    birthdate = birth_date.split("-")

    today = date.today()
    age = today.year - int(birthdate[0]) - ((today.month, today.day) < (int(birthdate[1]), int(birthdate[2])))

    if relation in ['Mother', 'Wife', 'Daughter', 'Sister']:
        gender = 'Female'
    else:
        gender = 'Male'

    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM user_basic_data WHERE email_address = '{email}';")
    user_account = cursor.fetchone()

    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM doctor_basic_data WHERE email_address = '{email}';")
    doctor_account = cursor.fetchone()

    if user_account or doctor_account:
        mysql.connection.commit()
        cursor.close()

        return False
    else:
        cursor.execute(f"INSERT INTO user_basic_data VALUES (NULL, NULL, '{first_name}', '{last_name}', '{birth_date}', \
            NULL, '{city}', '{mobile}', '{email}', NULL, NULL, {False});")
        cursor.execute(f"INSERT INTO user_health_data VALUES (NULL, '{gender}', '{age}', NULL, NULL, NULL, \
            NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);")
        cursor.execute(f"INSERT INTO user_stats VALUES (NULL, '{today}', 0, 0, 0, 0);")

        cursor.execute(f"SELECT * FROM user_basic_data WHERE email_address = '{email}';")
        member_account = cursor.fetchone()

        member_ids = basic_data[10]

        if member_ids:
            member_ids += f' {member_account[0]} {relation}'
        else:
            member_ids = f' {member_account[0]} {relation}'

        if account_type == 'Normal':
            cursor.execute(f"UPDATE user_basic_data SET member_ids = '{member_ids}' WHERE user_id = {basic_data[0]};")
        else:
            cursor.execute(f"UPDATE doctor_basic_data SET member_ids = '[{member_account[0]}, {relation}]' WHERE doctor_id = {basic_data[0]};")

        mysql.connection.commit()
        cursor.close()
        return True


# Profile: Upload Documents
def upload_documents(account_type, account_id, document_name, document_path):
    cursor = mysql.connection.cursor()

    if account_type == 'Normal':
        account = 'user'
    else:
        account = 'doctor'

    cursor.execute(f"INSERT INTO {account}_documents VALUES ({account_id}, '{document_name}', '{document_path}');")
    mysql.connection.commit()
    cursor.close()

    return True

    
# Update Profile: Update Basic Data
def update_basic_data(account_id, account_type, basic_data):
    cursor = mysql.connection.cursor()

    birthdate = basic_data[4].split("-")

    today = date.today()
    age = today.year - int(birthdate[0]) - ((today.month, today.day) < (int(birthdate[1]), int(birthdate[2])))

    if account_type == 'Normal':
        cursor.execute(f"UPDATE user_basic_data SET profile_picture = '{basic_data[1]}', first_name = '{basic_data[2]}', \
                        last_name = '{basic_data[3]}', birth_date = '{basic_data[4]}', home_address = '{basic_data[5]}', \
                        home_city = '{basic_data[6]}', mobile_number = '{basic_data[7]}' WHERE user_id = {account_id};")
        cursor.execute(f"UPDATE user_health_data SET age = '{age}' WHERE user_id = {account_id};")
        mysql.connection.commit()
        cursor.close()
    else:
        cursor.execute(f"UPDATE doctor_basic_data SET profile_picture = '{basic_data[1]}', first_name = '{basic_data[2]}', \
                last_name = '{basic_data[3]}', birth_date = '{basic_data[4]}', home_address = '{basic_data[5]}', \
                home_city = '{basic_data[6]}', work_address = '{basic_data[7]}', work_city = '{basic_data[8]}', \
                specialist = '{basic_data[9]}', mobile_number = '{basic_data[10]}' WHERE doctor_id = {account_id};")
        cursor.execute(f"UPDATE doctor_health_data SET age = '{age}' WHERE doctor_id = {account_id};")
        mysql.connection.commit()
        cursor.close()

    return True


# Update Profile: Update Health Data
def update_health_data(account_id, account_type, health_data):
    cursor = mysql.connection.cursor()

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
        health_data[3] = 'Not available'
        health_data[4] = 'Not available'
        health_data[5] = 'Not available'
        obesity = 'Not available'

    cursor.execute(f"UPDATE {account}_health_data SET gender = '{health_data[1]}', blood_group = '{health_data[3]}', \
                    weight = '{health_data[4]}', height = '{health_data[5]}', obesity = '{obesity}', disability = '{health_data[7]}', \
                    fitzpatrick = '{health_data[8]}', allergies = '{health_data[9]}', diabetes = '{health_data[10]}', \
                    thyroid = '{health_data[11]}', cancer = '{health_data[12]}', covid = '{health_data[13]}', asthma = '{health_data[14]}', \
                    hiv_aids = '{health_data[15]}', addiction = '{health_data[16]}' WHERE {account}_id = {account_id};")

    mysql.connection.commit()
    cursor.close()

    return True


# Update Profile: Update Login Data
def update_login_data(account_id, account_type, email, password):
    cursor = mysql.connection.cursor()

    if account_type == 'Normal':
        cursor.execute(f"UPDATE user_basic_data SET email_address = '{email}', password = '{password}' WHERE user_id = {account_id};")
        mysql.connection.commit()
        cursor.close()
    else:
        cursor.execute(f"UPDATE doctor_basic_data SET email_address = '{email}', password = '{password}' WHERE doctor_id = {account_id};")
        mysql.connection.commit()
        cursor.close()

    return True


# Update Profile: Update Stats
def update_stats(account_id, account_type, stats):
    cursor = mysql.connection.cursor()

    if account_type == 'Normal':
        cursor.execute(f"UPDATE user_stats SET number_of_appointments = {stats[2]}, number_of_virtual_appointments = {stats[3]}, \
                        number_of_documents_uploaded = {stats[4]}, number_of_members_added = {stats[5]} WHERE user_id = {account_id};")
        mysql.connection.commit()
        cursor.close()
    else:
        cursor.execute(f"UPDATE doctor_stats SET number_of_appointments = {stats[2]}, number_of_virtual_appointments = {stats[3]}, \
                        number_of_appointments_diagnosed = {stats[4]}, number_of_virtual_appointments_diagnosed = {stats[5]}, \
                        number_of_documents_uploaded = {stats[6]}, number_of_members_added = {stats[7]} WHERE doctor_id = {account_id};")
        mysql.connection.commit()
        cursor.close()

    return True


# Send Email
def send_mail(recipient, subject, body):
    msg = Message(subject, sender = 'contact.aarogyacentre@gmail.com', recipients = [recipient])
    msg.body = body
    mail.send(msg)

    return True