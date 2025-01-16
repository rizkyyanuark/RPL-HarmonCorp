import streamlit as st
import pandas as pd
from PIL import Image
from utils.firebase_config import db
from utils.pdf_generator import generate_receipt
from datetime import datetime
import requests
from io import BytesIO
from utils.cookies import cookies, load_cookie_to_session
from utils.account import send_purchase_confirmation_email

# Set page configuration
logo_url = "https://raw.githubusercontent.com/rizkyyanuark/RPL-HarmonCorp/main/prototyping/image/logo.jpg"
response = requests.get(logo_url)
logo = Image.open(BytesIO(response.content))
st.set_page_config(
    page_title="Pembeli",
    page_icon=logo,
)

st.sidebar.markdown(
    """
    ##### **Visit our repository [here](https://github.com/rizkyyanuark/RPL-HarmonCorp)!**
    """
)
# Load session state from cookies
try:
    load_cookie_to_session(st.session_state)
except RuntimeError:
    st.stop()

# Check if user is logged in
if (
    "role" in st.session_state and
    st.session_state.role == "Pembeli" and
    "signout" in st.session_state and
    not st.session_state.signout
):
    def load_products():
        products_ref = db.collection('products')
        products = products_ref.stream()
        product_list = []
        for product in products:
            product_data = product.to_dict()
            product_data['id'] = product.id
            product_list.append(product_data)
        return product_list

    st.title('Welcome Home!')
    st.text(f'Hello, {st.session_state.username}!')
    st.title("Products from Harmon Corp Platform 👟")

    # Load products from Firestore
    products = load_products()

    if products:
        df = pd.DataFrame(products)
        st.subheader("List Produk")
        st.dataframe(df)

        # Input untuk membeli produk
        st.subheader("Buy Product")
        product_name = st.selectbox("Choose Product", df['name'])
        quantity = st.number_input("Jumlah", min_value=1, step=1)
        payment_method = st.selectbox(
            "Payment Methods", ["Credit Card", "Debit Card", "PayPal", "Cash"])

        if st.button("Beli"):
            product = df[df['name'] == product_name].iloc[0]
            product_id = product['id']
            if int(product['stock']) >= quantity:
                db.collection('products').document(product_id).update({
                    'stock': int(product['stock']) - int(quantity)
                })
                order_data = {
                    "product_id": product_id,
                    "product_name": product['name'],
                    "quantity": int(quantity),
                    "buyer": st.session_state.username,
                    "store": product['store'],
                    "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                    "payment_method": payment_method,
                    "price": product['price'],
                    "confirmed": False,
                    "delivered": False,
                    "courier": None
                }
                db.collection('orders').add(order_data)
                st.success("successfully ordered and check email!")
                pdf_stream = generate_receipt(order_data)

                st.download_button(label="Download Receipt", data=pdf_stream,
                                   file_name="receipt.pdf", mime='application/pdf')
                send_purchase_confirmation_email(
                    st.session_state.useremail, order_data)
            else:
                st.error("Insufficient stock.")
    else:
        st.text("No products available.")
else:
    st.error("Please log in as Buyer to access this page.")
