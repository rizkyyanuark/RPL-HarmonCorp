import firebase_admin
from firebase_admin import credentials, firestore, initialize_app, storage
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource
def get_firebase_app():
    def get_secret():
        # Load credentials from Streamlit secrets
        credentials_info = {
            "type": st.secrets["firebase"]["type"],
            "project_id": st.secrets["firebase"]["project_id"],
            "private_key_id": st.secrets["firebase"]["private_key_id"],
            "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
            "client_email": st.secrets["firebase"]["client_email"],
            "client_id": st.secrets["firebase"]["client_id"],
            "auth_uri": st.secrets["firebase"]["auth_uri"],
            "token_uri": st.secrets["firebase"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
            "universe_domain": st.secrets["firebase"]["universe_domain"],
            "firebase_api": st.secrets["firebase"]["firebase_api"],
            "bucket_firestore": st.secrets["firebase"]["bucket_firestore"]
        }
        return credentials_info

    if not firebase_admin._apps:
        cred = credentials.Certificate(get_secret())
        return initialize_app(cred, {
            'storageBucket': st.secrets["firebase"]["bucket_firestore"]
        })
    else:
        return firebase_admin.get_app()


firebase_app = get_firebase_app()

# Firestore client
db = firestore.client()

# Storage client
bucket = storage.bucket(st.secrets["firebase"]["bucket_firestore"])
