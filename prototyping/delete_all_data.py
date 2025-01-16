import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Firebase Admin SDK
cred = credentials.Certificate("RPL_CREDENTIALS.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


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


def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(f"Deleting doc {doc.id} => {doc.to_dict()}")
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


def delete_all_collections():
    collections = db.collections()
    for collection in collections:
        print(f"Deleting collection: {collection.id}")
        delete_collection(collection, 10)

    print("All collections have been deleted.")


if __name__ == "__main__":
    delete_all_users()
    delete_all_collections()
