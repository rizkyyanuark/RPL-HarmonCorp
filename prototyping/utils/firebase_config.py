import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
from dotenv import load_dotenv
from google.cloud import secretmanager
import json

load_dotenv()


def get_secret(secret_name, project_id=None):
    client = secretmanager.SecretManagerServiceClient()
    project_id = st.secrets['PROJECT_ID']
    if not project_id:
        raise ValueError("PROJECT_ID environment variable is not set.")
    secret_version = f'projects/{project_id}/secrets/{secret_name}/versions/latest'
    response = client.access_secret_version(name=secret_version)
    return response.payload.data.decode('UTF-8')


# Ambil konten JSON dari Secret Manager
credentials_json = get_secret("RPL_CREDENTIALS")

# Parse konten JSON menjadi dictionary
credentials_dict = json.loads(credentials_json)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(credentials_dict)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
