Dependencies needed to be installed before running the application
	-	MySQL (Server, Workbench, Shell) [Install using MySQL Installer]
	-	Python (virtualenv, Flask, flask_mysql, pytz, flask_mail, numpy, pandas, sklearn)
Configurations
    -   You will need to configure the database configuration and email configuration that is present in database.py

Site Map:

	-> Home Page	-> Create a Account
                     -> Log In	        -> Appointment Booking Module
                                        -> Healthcare Chatbot Module
                                        -> Communicate with Doctor (Link to Communicate Module)	
                                        -> Upcoming In-Person Appointments
                                        -> Upcoming Virtual Appointments
                                        -> Mini Profile (Link to Profile Module)    -> Appointment History
                                                                                    -> Uploaded Documents Details		-> Upload Documents
                                                                                    -> User Basic Details			    -> Update User Basic Deatils
                                                                                    -> User Health Details 			    -> Update User Health Details

Color Palette Codes: 

-> #22577A
-> #38A3A5
-> #57CC99
-> #80ED99

Database Fields:

->  Basic Data		->  Health Data	            ->  User Stats		                        ->  Doctor Stats
1. 	ID			        1.	ID		            1.	User ID		                            1.  Doctor ID
2.	Profile Picture	    2. 	Gender		        2.	Account Created On		                2.  Account Created On
3.	First Name		    3.	Age		            3.	Number of Appointments Booked           3.  Number of Appointments Diagnosed
4. 	Last Name		    4.	Blood Group	        4.	Number of Virtual Appointments Booked   4.  Number of Virtual Appointments Diagnosed
5. 	Date of Birth	    5. 	Weight		        5.	Number of Documents Uploaded            
6.	Address	            6.	Height		        6.	Number of Members Added	
7. 	City, State	        7.	Obesity			
8. 	Mobile Number	    8.	Disability			
9. 	Email Address	    9.	Fitzpatrick			
10.	Password		    10.	Allergies		
11. Speciality          11.	Diabetes			
12.	Logged In		    12.	Thyroid			
                        13.	Cancer			
                        14. Covid			
                        15. Asthma									
                        16.	HIV/AIDS								
                        17. Addiction					

-> Appointment Data
1.	Appointment ID
2. 	Mode of Appointment
3. 	User ID
4. 	User Name
5.	Doctor ID
6.	Doctor Name
7.	Specialist
8.	Appointment Date
9.	Appointment Time
10.	Appointment Address
11. Appointment City