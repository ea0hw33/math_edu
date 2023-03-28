from edu_lite import db, app
from edu_lite.models import Students
from passlib.hash import sha256_crypt

login = ""
name = input("Enter admin name:")
second_name= input("Enter admin second_name:")
surname = input("Enter admin surname:")
raw_password = ""

validate_name = False
while validate_name == False:
	login = input("Enter admin login:")
	if login == '':
		print("Name can't be blank!")
	elif ' ' in login:
		print("Name can't contain spaces!")
	elif len(login) < 3:
		print("Name is too short!")
	else:
		validate_name = True

validate_password = False
while validate_password == False:
	raw_password = input("Enter password:")
	if raw_password == '':
		print("Password can't be blank!")
	if ' ' in raw_password:
		print("Password can't contain spaces!")
	if len(raw_password) < 4:
		print("Password is too short!")
	else:
		validate_password = True
with app.app_context():
	crypt_password = sha256_crypt.hash(raw_password)
	new_user = Students(name, second_name, surname, login, crypt_password, 1)
	db.session.add(new_user)
	db.session.commit()