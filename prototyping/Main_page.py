from datetime import datetime
from utils.firebase_config import db
from utils.account import login, logout, send_verification_email
from dotenv import load_dotenv
from firebase_admin import auth
import os
import base64
from io import BytesIO
from PIL import Image
import streamlit as st


# Set page configuration
logo_path = os.path.join("image", "logo.jpg")
logo = Image.open(logo_path)
logo_home = os.path.join("image", "logo_home.jpg")
logo_home = Image.open(logo_home)
st.set_page_config(
    page_title="Welcome to Harmon Corp!",
    page_icon=logo,
)


load_dotenv()
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")


def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


# Sidebar success message
st.sidebar.success("Select a demo above.")

logo_base64 = image_to_base64(logo_home)
st.markdown(
    f"""
        <div style="text-align: center; margin: 0; padding: 0;">
            <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="width: 50%; max-width: 300px;">
        </div>
        """,
    unsafe_allow_html=True,
)

# Welcome text
st.write(
    "<h1 style='text-align: center;'>Welcome!</h1>",
    unsafe_allow_html=True,
)

# Link to repository
st.markdown(
    """
    ##### **Visit our repository [here](https://github.com/NV-Bite)!**
    """
)

# Initialize session state for user data
if 'username' not in st.session_state:
    st.session_state.username = ''

if 'useremail' not in st.session_state:
    st.session_state.useremail = ''

if 'signout' not in st.session_state:
    st.session_state.signout = False

if 'role' not in st.session_state:
    st.session_state.role = ''

if not st.session_state.signout:
    # If not logged in
    choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])
    if choice == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                user = auth.get_user_by_email(email)
                if not user.email_verified:
                    st.error("Email not verified. Please check your inbox.")
                else:
                    login(email, password)
            except Exception as e:
                st.error(f"Error logging in: {e}")
    else:
        username = st.text_input("Username")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox('Select Role', ['Pembeli', 'Penjual', 'Kurir'])

        if st.button("Create my account"):
            if password != confirm_password:
                st.error("Passwords do not match. Please try again.")
            else:
                try:
                    user = auth.create_user(
                        email=email, password=password, uid=username)
                    db.collection('users').document(user.uid).set({
                        'name': username,
                        'email': email,
                        'role': role
                    })
                    # Send email verification
                    send_verification_email(email)
                    st.success(
                        "Account created successfully! Please verify your email.")
                    st.markdown(
                        "Please check your email for the verification link.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error creating account: {e}")
else:
    # If logged in
    st.text('Name: ' + st.session_state.username)
    st.text('Email: ' + st.session_state.useremail)
    st.text('Role: ' + st.session_state.role)
    st.button('Sign Out', on_click=logout)
