import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_secret():
    # Load credentials from Streamlit secrets
    credentials_info = {
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"],
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
        "universe_domain": st.secrets["firebase"]["universe_domain"],
        "firebase_api": st.secrets["firebase"]["firebase_api"]
    }
    return credentials_info


# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(get_secret())
    initialize_app(cred)

# Firestore client
db = firestore.client()
