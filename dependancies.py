import streamlit as st
import streamlit_authenticator as stauth
import datetime
import re
from deta import Deta
import smtplib
import random
import string
import bcrypt


# Database authentication cedentials

auth_key = 'd0wdrf4hnoy_6AZ6t78HKWW8geoy2kBKWfffbC95ZNVE'
deta = Deta(auth_key)
db = deta.Base('project')

# Patient Database
db2 = deta.Base('patient')


def validate_mobile_number(number):

    pattern = r'^[789]\d{9}$'
    
    if re.match(pattern, number):
        return True
    else:
        return False
    

def validate_password(password):
    # Check if the password is at least 8 characters long
    if len(password) < 8:
        return False
    
    # Check if the password contains at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check if the password contains at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # Check if the password contains at least one digit
    if not re.search(r'[0-9]', password):
        return False
    
    # Check if the password contains at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>~]', password):
        return False
    
    return True

def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def validate_email(email):
   
    pattern = "^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$"

    if re.match(pattern, email):
        return True
    return False


def validate_username(username):
    if re.search(r'[A-Z]', username):
        return False
    
    
    if not re.search(r'[a-z]', username):
        return False
    
    
    if not re.search(r'[0-9]', username):
        return False
    
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>~]', username):
        return False
    
    return True
    
def validate_age(age):
    try:
        age = int(age)
        if age > 0 and age < 120:
            return True
        else:
            return False
    except:
        pass


def insert_user(email, username,mob, password):

    date_joined = str(datetime.datetime.now())
    
    return db.put({'key': email, 'username': username, 'password': password,"mobile":mob ,'date_joined': date_joined})
    

def fetch_users():

    users = db.fetch()
    return users.items


def get_user_emails():

    users = db.fetch()
    emails = []
    for user in users.items:
        emails.append(user['key'])
    return emails


def get_usernames():
    
    users = db.fetch()
    usernames = []
    for user in users.items:
        usernames.append(user['username'])
    print(usernames)
    return usernames


def get_password(email):
    p = None
    users = db.fetch()
    for user in users.items:
        if user['key'] == email:
            p = user['password']
            break
    return p
    


def sign_up():
    with st.form(key='signup', clear_on_submit=True):
        st.subheader(':green[Sign Up]')
        email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
        username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
        password1 = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')
        password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Your Password', type='password')
        mobile = st.text_input(':blue[Mobile]', placeholder='Your Mobile Number')
        

        if email:
            if validate_email(email):
                if email not in get_user_emails():
                    if validate_username(username):
                        if username not in get_usernames():
                            if len(username) >= 2:
                                if validate_password(password1):
                                    if password1 == password2:
                                        if validate_mobile_number(mobile):
                                            
                                            hashed =  stauth.Hasher([password1]).generate()
                                            insert_user(email, username, mobile,hashed[0])         # Add User to DB
                                            st.success('Account created successfully!!')
                                            st.balloons()
                                        else:
                                            st.warning("Mobile number is not valid")
                                    else:
                                        st.warning('Passwords Do Not Match')
                                else:
                                    st.warning('Password is not valid. Should be like "Xyz@123"')
                            else:
                                st.warning('Username Too short')
                        else:
                            st.warning('Username Already Exists')
                    else:
                        st.warning('Invalid Username!Should only Contain smallcase and numbers.')
                else:
                    st.warning('Email Already exists!!')
            else:
                st.warning('Invalid Email')

        btn1, bt2, btn3, btn4, btn5 = st.columns(5)
        
        with btn3:
            st.form_submit_button('Sign Up')


def patient_info(name,age,mob):

    if validate_age(age):

        if validate_mobile_number(mob):
        
            date_joined = str(datetime.datetime.now())
            db2.put({"name":name,"age":age,"mobile":mob,"Date_joined":date_joined})
            st.balloons()

        else:
            st.warning("Mobile number is not valid")
    else:
        
        st.warning("Age is not valid")


def patient_form():

   with st.form(key="patient_info",clear_on_submit=True):
      st.subheader(':green[Patient Details]')
      name = st.text_input("Enter patient's name")
      age = st.text_input("Enter patient's age")
      mob = st.text_input("Enter patient's Mobile")
      if st.form_submit_button(":green[Submit]"):
          patient_info(name,age,mob)


def change_pass(new_pass):
    st.success("Password has been updated")


def send_pass(email,new_pass):

    try:
        HOST = "smtp.googlemail.com"
        PORT = 587

        FROM_EMAIL = "pandey.sp.shiva625@gmail.com"

        TO_EMAIL = email
        PASSWORD = "jmauqsioloeueqjb"


        smtp = smtplib.SMTP(HOST, PORT)

        status_code, response = smtp.ehlo()
        print(f"[*] Echoing the server: {status_code} {response}")

        status_code, response = smtp.starttls()
        print(f"[*] Starting TLS connection: {status_code} {response}")

        status_code, response = smtp.login(FROM_EMAIL, PASSWORD)
        print(f"[*] Logging in: {status_code} {response}")

        

        MESSAGE = """Subject: Pneumonia Detection Website \n\n
    your password is '{}' """.format(new_pass)

        smtp.sendmail(FROM_EMAIL, TO_EMAIL, MESSAGE)

        smtp.quit()
        return True
    except:
        pass

def set_pass(email,new_pass = generate_random_password()):
    try:
        users = db.fetch()
        for user in users.items:
            if user['key'] == email:
                hashed = stauth.Hasher([new_pass]).generate()
                db.update(key=email,updates={'password':hashed[0]})
                return new_pass
    except:
        st.success("Refresh and try again....")    
    
def reset_pass():
    with st.form(key="Reset Password",clear_on_submit=True):
            st.subheader(':blue[Change Your Password]')
            email = st.text_input("Enter your email",placeholder="Enter Your Current Email")
            curr_pass = st.text_input("Enter your current passowrd",placeholder="Enter Your Current Passowrd")
            new_passs = st.text_input("Enter your New Password",placeholder="Enter Your New Passowrd")
            confirm_new_passs = st.text_input("Confirm Your Password",placeholder="Confirm Your New Password")
            
            if st.form_submit_button("Change"):

                if validate_email(email):
                    if email in get_user_emails():
                        if validate_password(new_passs):
                            if new_passs == confirm_new_passs:
                                if bcrypt.checkpw(curr_pass.encode(), get_password(email).encode()):
                                    
                                    
                                    new_pass = set_pass(email,new_passs) 
                                    if send_pass(email,new_pass):
                                        
                                        
                                        st.success("Passowrd Changed Succesfully. Login Please..",icon="✅")

                                        
                                    else:
                                        st.warning("OTP sent to your email")
                                else:
                                    st.warning("Wrong Password !!!")
                            else:
                                st.warning("Password not matching !!!")
                        else:
                            st.warning('New password is not valid. Should in format "Xyz@123"')
                    else:
                        st.error("Email not found !!!")
                else:
                    st.warning('Wrong email !!!')

def forgot_pass():
        
        with st.form(key="Forgot Password",clear_on_submit=True):
            st.subheader(':red[Get your password]')
            email = st.text_input("Enter your email",placeholder="Password will be send to provided email")
            
            if st.form_submit_button("Send"):

                if validate_email(email):
                    if email in get_user_emails():
                        new_pass = set_pass(email)
                        
                        if send_pass(email,new_pass):
                            
                            
                            st.success("Passowrd sent to your email. Login or Change it.",icon="✅")

                            
                        else:
                            st.warning("OTP sent to your email")
                    else:
                        st.error("Email not found !!!")
                else:
                    st.warning('Wrong email !!!')
        
                


                    


