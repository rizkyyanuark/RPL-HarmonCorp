import streamlit as st
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from firebase_admin import auth, firestore
from datetime import datetime
from utils.firebase_config import db, credentials_dict

# FIREBASE_API_KEY diambil langsung dari credentials_dict
FIREBASE_API_KEY = credentials_dict['firebase_api']

# Konfigurasi SMTP
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = credentials_dict['smtp_username']
SMTP_PASSWORD = credentials_dict['smtp_password']


def save_login_logout(username, event_type):
    """Simpan data login atau logout ke Firestore dengan memisahkan tanggal dan waktu."""
    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%H:%M:%S")
    doc_ref = db.collection("Absensi Karyawan").document(username)

    try:
        if event_type == "login":
            doc_ref.update({
                "Login_Date": firestore.ArrayUnion([date]),
                "Login_Time": firestore.ArrayUnion([time])
            })
        elif event_type == "logout":
            doc_ref.update({
                "Logout_Date": firestore.ArrayUnion([date]),
                "Logout_Time": firestore.ArrayUnion([time])
            })
    except Exception as e:
        if event_type == "login":
            doc_ref.set({
                "Login_Date": [date],
                "Login_Time": [time],
                "Logout_Date": [],
                "Logout_Time": []
            })
        elif event_type == "logout":
            doc_ref.set({
                "Login_Date": [],
                "Login_Time": [],
                "Logout_Date": [date],
                "Logout_Time": [time]
            })


def verify_password(email, password):
    api_key = FIREBASE_API_KEY
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def login(email, password):
    user_data = verify_password(email, password)
    if user_data:
        try:
            user = auth.get_user_by_email(email)
            if not user.email_verified:
                st.warning("Email not verified. Please check your inbox.")
                return
            user_doc = db.collection('users').document(user.uid).get()

            if user_doc.exists:
                user_data = user_doc.to_dict()
                st.session_state.username = user.uid
                st.session_state.useremail = user.email
                st.session_state.role = user_data['role']
                st.session_state.signout = True
                save_login_logout(user.uid, "login")  # Simpan data login
                st.success(f"Login successful as {user_data['role']}!")
            else:
                st.warning("User data not found.")
        except Exception as e:
            st.warning(f"Login Failed: {e}")
    else:
        st.warning("Invalid email or password")


def logout():
    save_login_logout(st.session_state.username, "logout")
    st.session_state.signout = False
    st.session_state.username = ''
    st.session_state.useremail = ''
    st.session_state.role = ''


def send_verification_email(email):
    try:
        user = auth.get_user_by_email(email)
        link = auth.generate_email_verification_link(email)

        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = 'Verify your email address'

        body = f"""
        Hi {user.display_name or user.email},
        
        Please verify your email address by clicking the link below:
        
        {link}
        
        If you did not create an account, please ignore this email.
        
        Thanks,
        Your Company Name
        """

        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, email, text)
        server.quit()

        print(f"Verification email sent to {email}")
    except Exception as e:
        print(f"Error sending verification email: {e}")
