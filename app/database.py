from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager


db = SQLAlchemy()


def init_db(app):
    """Initialize the database with the Flask app."""
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.logger.info(f"Database initialization successful!")


@contextmanager
def get_db_connection():
    """Provide a database session for use with queries."""
    connection = None
    try:
        connection = db.engine.connect()
        yield connection
    finally:
        if connection:
            connection.close()


# # Add member to a profile
# def add_user(first_name, last_name, birth_date, city, email, mobile, relation, basic_data, account_type):
#     birthdate = birth_date.split("-")

#     today = date.today()
#     age = today.year - int(birthdate[0]) - ((today.month, today.day) < (int(birthdate[1]), int(birthdate[2])))

#     if relation in ['Mother', 'Wife', 'Daughter', 'Sister']:
#         gender = 'Female'
#     else:
#         gender = 'Male'

#     with closing(mysql.connection.cursor()) as cursor:
#         cursor.execute(GET_BASIC_DATA_FROM_EMAIL, (email,))
#         user_account = cursor.fetchone()

#         cursor = mysql.connection.cursor()
#         cursor.execute("SELECT * FROM doctor_basic_data WHERE email_address = %s;", (email,))
#         doctor_account = cursor.fetchone()

#         if user_account or doctor_account:
#             mysql.connection.commit()

#             return False
#         else:
#             cursor.execute("INSERT INTO user_basic_data VALUES (NULL, NULL, %s, %s, %s, NULL, %s, %s, %s, \
#                            NULL, NULL, %s);", (first_name, last_name, birth_date, city, mobile, email, False))
#             cursor.execute("INSERT INTO user_health_data VALUES (NULL, %s, %s, NULL, NULL, NULL, NULL, NULL, \
#                            NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);", (gender, age,))
#             cursor.execute("INSERT INTO user_stats VALUES (NULL, %s, 0, 0, 0, 0);", (today,))

#             cursor.execute(GET_BASIC_DATA_FROM_EMAIL, (email,))
#             member_account = cursor.fetchone()

#             member_ids = basic_data[10]

#             if member_ids:
#                 member_ids += f' {member_account[0]} {relation}'
#             else:
#                 member_ids = f' {member_account[0]} {relation}'

#             if account_type == 'Normal':
#                 cursor.execute("UPDATE user_basic_data SET member_ids = %s WHERE user_id = %s;", 
#                                (member_ids, basic_data[0],))
#             else:
#                 cursor.execute("UPDATE doctor_basic_data SET member_ids = '[%s, %s]' WHERE doctor_id = %s;", 
#                                (member_account[0], relation, basic_data[0],))

#             mysql.connection.commit()
#             return True


# # Upload documents of a user
# def upload_documents(account_type, account_id, document_name, document_path):
#     with closing(mysql.connection.cursor()) as cursor:

#         if account_type == 'Normal':
#             account = 'user'
#         else:
#             account = 'doctor'

#         cursor.execute("INSERT INTO %s_documents VALUES (%s, %s, %s);", 
#                        (account, account_id, document_name, document_path))
#         mysql.connection.commit()

#     return True


# # Update login data of the user
# def update_login_data(account_id, account_type, email, password):
#     with closing(mysql.connection.cursor()) as cursor:

#         if account_type == 'Normal':
#             cursor.execute("UPDATE user_basic_data SET email_address = %s, password = %s WHERE user_id = %s;", 
#                            (email, password, account_id,))
#             mysql.connection.commit()
#         else:
#             cursor.execute("UPDATE doctor_basic_data SET email_address = %s, password = %s WHERE doctor_id = %s;", 
#                            (email, password, account_id,))
#             mysql.connection.commit()

#     return True


# # Send Email
# def send_mail(recipient, subject, body):
    # msg = Message(subject, sender = 'contact.aarogyacentre@gmail.com', recipients = [recipient])
    # msg.body = body
    # mail.send(msg)

    # return True