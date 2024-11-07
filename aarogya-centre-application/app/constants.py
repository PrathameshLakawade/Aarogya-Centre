TABLE_NAMES = [
    'user_basic_data',
    'user_health_data',
    'user_stats',
    'user_documents',
    'doctor_basic_data',
    'doctor_health_data',
    'doctor_stats',
    'doctor_documents',
    'appointment_data'
]
GET_BASIC_DATA_FROM_EMAIL = "SELECT * FROM user_basic_data WHERE email_address = %s;"