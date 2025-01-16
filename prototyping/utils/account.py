import streamlit as st
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from firebase_admin import auth, firestore, storage
from datetime import datetime
from io import BytesIO
from utils.firebase_config import db, bucket
from utils.pdf_generator import generate_receipt

# configuration Firebase
FIREBASE_API_KEY = st.secrets["firebase"]["firebase_api"]

# configuration SMTP
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = st.secrets["smtp"]["username"]
SMTP_PASSWORD = st.secrets["smtp"]["password"]


def save_login_logout(username, event_type):
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
                if st.session_state.role == 'Penjual':
                    st.session_state.store_name = user_data['store_name']
                st.session_state.signout = True
                save_login_logout(user.uid, "login")  # Simpan data login
                st.success(f"Login successful as {user_data['role']}!")
            else:
                st.warning("User data not found.")
        except Exception as e:
            st.warning(f"Login Failed: {e}")


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
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .email-container {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                }}
                .email-header {{
                    text-align: center;
                    padding-bottom: 20px;
                }}
                .email-header img {{
                    max-width: 100px;
                }}
                .email-body {{
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 10px;
                }}
                .email-footer {{
                    text-align: center;
                    padding-top: 20px;
                    font-size: 12px;
                    color: #777;
                }}
                .verify-button {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 20px 0;
                    font-size: 16px;
                    color: #fff;
                    background-color: #b9c4c6;
                    text-decoration: none;
                    border-radius: 5px;
                }}
                .verify-button:hover {{
                    background-color: #a0b0b2;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    <img src="https://raw.githubusercontent.com/rizkyyanuark/RPL-HarmonCorp/main/prototyping/image/logo.jpg" alt="Harmon Corp Logo">
                </div>
                <div class="email-body">
                    <p>Hi {user.display_name or user.email},</p>
                    <p>Please verify your email address by clicking the button below:</p>
                    <p style="text-align: center;">
                        <a href="{link}" class="verify-button">Verify Email</a>
                    </p>
                    <p>If you did not create an account, please ignore this email.</p>
                    <p>Thanks,<br>Harmon Corp Team</p>
                </div>
                <div class="email-footer">
                    <p>&copy; {datetime.now().year} Harmon Corp. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        # Send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, email, text)
        server.quit()
    except Exception as e:
        print(f"Error sending verification email: {e}")


def send_purchase_confirmation_email(email, order_data):
    try:
        user = auth.get_user_by_email(email)
        receipt_link = generate_receipt_link(order_data)

        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = 'Your Purchase Confirmation'

        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .email-container {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                }}
                .email-header {{
                    text-align: center;
                    padding-bottom: 20px;
                }}
                .email-header img {{
                    max-width: 100px;
                }}
                .email-body {{
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 10px;
                }}
                .email-footer {{
                    text-align: center;
                    padding-top: 20px;
                    font-size: 12px;
                    color: #777;
                }}
                .download-button {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 20px 0;
                    font-size: 16px;
                    color: #fff;
                    background-color: #b9c4c6;
                    text-decoration: none;
                    border-radius: 5px;
                }}
                .download-button:hover {{
                    background-color: #a0b0b2;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    <img src="https://raw.githubusercontent.com/rizkyyanuark/RPL-HarmonCorp/main/prototyping/image/logo.jpg" alt="Harmon Corp Logo">
                </div>
                <div class="email-body">
                    <p>Hi {user.display_name or user.email},</p>
                    <p>Thank you for your purchase! Here are the details of your order:</p>
                    <ul>
                        <li><strong>Product:</strong> {order_data['product_name']}</li>
                        <li><strong>Quantity:</strong> {order_data['quantity']}</li>
                        <li><strong>Price per Item:</strong> {order_data['price']}</li>
                        <li><strong>Total Price:</strong> {order_data['quantity'] * order_data['price']}</li>
                        <li><strong>Payment Method:</strong> {order_data['payment_method']}</li>
                    </ul>
                    <p>You can download your receipt by clicking the button below:</p>
                    <p style="text-align: center;">
                        <a href="{receipt_link}" class="download-button">Download Receipt</a>
                    </p>
                    <p>If you have any questions, please contact our support team.</p>
                    <p>Thanks,<br>Harmon Corp Team</p>
                </div>
                <div class="email-footer">
                    <p>&copy; {datetime.now().year} Harmon Corp. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        # Send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, email, text)
        server.quit()
        st.success("Purchase confirmation email sent successfully!")
    except Exception as e:
        print(f"Error sending purchase confirmation email: {e}")


def generate_receipt_link(order_data):
    # Generate the receipt PDF
    pdf_stream = generate_receipt(order_data)
    receipt_filename = f"receipt_{order_data['product_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    # Upload the PDF to Firebase Storage
    blob = bucket.blob(f"receipts/{receipt_filename}")
    blob.upload_from_file(BytesIO(pdf_stream.getvalue()),
                          content_type='application/pdf')

    # Make the file publicly accessible
    blob.make_public()

    # Return the public URL
    return blob.public_url
