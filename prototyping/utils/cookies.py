from streamlit_cookies_manager import EncryptedCookieManager

# Inisialisasi cookie manager
cookies = EncryptedCookieManager(
    prefix="harmon_corp", password="super_secret_key")

# Fungsi untuk menyimpan data pengguna ke dalam cookie


def save_user_to_cookie(username, email, role, store_name=""):
    cookies["username"] = username
    cookies["email"] = email
    cookies["role"] = role
    if role == "Penjual":
        cookies["store_name"] = store_name
    cookies["signout"] = "False"
    cookies.save()

# Fungsi untuk menghapus data pengguna dari cookie


def clear_user_cookie():
    cookies["username"] = ""
    cookies["email"] = ""
    cookies["role"] = ""
    cookies["store_name"] = ""
    cookies["signout"] = "True"
    cookies.save()

# Fungsi untuk memuat data dari cookie ke session state


def load_cookie_to_session(session_state):
    session_state.username = cookies.get("username", "")
    session_state.useremail = cookies.get("email", "")
    session_state.role = cookies.get("role", "")
    session_state.store_name = cookies.get("store_name", "")
    session_state.signout = cookies.get("signout", "True") == "True"


# Pastikan cookies siap digunakan
if not cookies.ready():
    raise RuntimeError("Cookies manager is not ready.")
