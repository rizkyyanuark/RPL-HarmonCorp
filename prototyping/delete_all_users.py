import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK
cred = credentials.Certificate("RPL_CREDENTIALS.json")
firebase_admin.initialize_app(cred)


def delete_all_users():
    # List all users
    page = auth.list_users()
    while page:
        for user in page.users:
            print(f"Deleting user: {user.uid}")
            auth.delete_user(user.uid)
        # Get next batch of users
        page = page.get_next_page()

    print("All users have been deleted.")


if __name__ == "__main__":
    delete_all_users()
