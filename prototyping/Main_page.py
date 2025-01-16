from datetime import datetime
from utils.firebase_config import db
from utils.account import login, logout, send_verification_email
from dotenv import load_dotenv
from firebase_admin import auth
import base64
from io import BytesIO
from PIL import Image
import streamlit as st
import requests
from utils.cookies import cookies, save_user_to_cookie, clear_user_cookie, load_cookie_to_session


# Set page configuration
logo_url = "https://raw.githubusercontent.com/rizkyyanuark/RPL-HarmonCorp/main/prototyping/image/logo.jpg"
response = requests.get(logo_url)
logo = Image.open(BytesIO(response.content))
st.set_page_config(
    page_title="Welcome to Harmon Corp!",
    page_icon=logo,
)


load_dotenv()


def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


# Load images
logo_home_url = "https://raw.githubusercontent.com/rizkyyanuark/RPL-HarmonCorp/main/prototyping/image/logo_home.png"
response = requests.get(logo_home_url)
if response.status_code == 200:
    logo_home = Image.open(BytesIO(response.content))
else:
    logo_home = None

# Sidebar success message
st.sidebar.success("Select role above.")
st.sidebar.markdown(
    """
    ##### **Visit our repository [here](https://github.com/rizkyyanuark/RPL-HarmonCorp)!**
    """
)

# Convert logo to Base64 and display in the center
if logo_home:
    logo_base64 = image_to_base64(logo_home)
    st.markdown(
        f"""
        <div style="text-align: center; padding: 0px 0;">
            <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="width: 100%; max-width: 400px;">
        </div>
        """,
        unsafe_allow_html=True,
    )

# Welcome text
st.write(
    "<h1 style='text-align: center;'>Welcome!</h1>",
    unsafe_allow_html=True,
)

try:
    load_cookie_to_session(st.session_state)
except RuntimeError:
    st.stop()

if st.session_state.signout:
    choice = st.selectbox("Login/Signup", ["Login", "Sign up"])
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
                    user_data = db.collection("users").document(
                        user.uid).get().to_dict()
                    st.session_state.username = user_data["name"]
                    st.session_state.useremail = email
                    st.session_state.role = user_data["role"]
                    st.session_state.store_name = user_data.get(
                        "store_name", "")
                    st.session_state.signout = False

                    # Save to cookies
                    save_user_to_cookie(
                        st.session_state.username,
                        st.session_state.useremail,
                        st.session_state.role,
                        st.session_state.store_name,
                    )
                    st.success("Login successful!")
            except Exception as e:
                st.error(f"Error logging in: {e}")
    else:
        username = st.text_input("Username")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Select Role", ["Pembeli", "Penjual", "Kurir"])

        if role == "Penjual":
            store_name = st.text_input("Store Name")

        if st.button("Create my account"):
            if password != confirm_password:
                st.error("Passwords do not match. Please try again.")
            else:
                try:
                    user = auth.create_user(
                        email=email, password=password, uid=username)
                    user_data = {
                        "name": username,
                        "email": email,
                        "role": role,
                    }
                    if role == "Penjual":
                        user_data["store_name"] = store_name
                        st.session_state.store_name = store_name

                    db.collection("users").document(user.uid).set(user_data)
                    send_verification_email(email)
                    st.success(
                        "Account created successfully! Please verify your email.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error creating account: {e}")
else:
    st.markdown(
        f"<h2 style='text-align: left;'>Welcome back, {st.session_state.username}!</h2>", unsafe_allow_html=True)
    st.text(f"Email: {st.session_state.useremail}")
    st.text(f"Role: {st.session_state.role}")
    if st.session_state.role == "Penjual":
        st.text(f"Store Name: {st.session_state.store_name}")
    if st.button("Sign Out"):
        st.session_state.signout = True
        clear_user_cookie()
        st.success("Signed out successfully!")
