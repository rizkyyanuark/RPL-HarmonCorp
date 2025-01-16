import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

from utils.firebase_config import db
from utils.cookies import cookies, load_cookie_to_session

# Set page configuration
logo_url = "https://raw.githubusercontent.com/rizkyyanuark/RPL-HarmonCorp/main/prototyping/image/logo.jpg"
response = requests.get(logo_url)
logo = Image.open(BytesIO(response.content))
st.set_page_config(
    page_title="Penjual",
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

# Check if the user is logged in and has the role "Penjual"
if (
    "role" in st.session_state and
    st.session_state.role == "Penjual" and
    "signout" in st.session_state and
    not st.session_state.signout
):
    st.title("Seller Page")
    st.text(f"Hello, {st.session_state.username}!")

    # Form to add a new product
    st.subheader("Add New Product")
    product_name = st.text_input("Product Name")
    product_price = st.number_input("Product Price", min_value=0.0, step=0.01)
    product_stock = st.number_input("Product Stock", min_value=0, step=1)

    if st.button("Add Product"):
        product_data = {
            "name": product_name,
            "price": product_price,
            "stock": int(product_stock),
            "store": st.session_state.store_name,
            "seller": st.session_state.username
        }
        db.collection("products").add(product_data)
        st.success("Product added successfully!")

    # Display all products added by the seller
    st.subheader("Your Products")
    products_ref = db.collection("products").where(
        "seller", "==", st.session_state.username
    )
    products = products_ref.stream()

    product_list = []
    for product in products:
        product_data = product.to_dict()
        product_data["id"] = product.id
        product_list.append(product_data)

    if product_list:
        products_df = pd.DataFrame(product_list)
        st.dataframe(products_df)
    else:
        st.text("No products found.")

    # Display orders for confirmation
    st.subheader("Confirm Orders")
    orders_ref_confirmed = db.collection("orders").where(
        "store", "==", st.session_state.store_name
    ).where("confirmed", "==", False)
    orders_ref_delivered = db.collection("orders").where(
        "store", "==", st.session_state.store_name
    ).where("delivered", "==", False)

    orders_confirmed = orders_ref_confirmed.stream()
    orders_delivered = orders_ref_delivered.stream()

    order_list = []
    order_ids = set()

    for order in orders_confirmed:
        order_data = order.to_dict()
        order_data["id"] = order.id
        if order.id not in order_ids:
            order_list.append(order_data)
            order_ids.add(order.id)

    for order in orders_delivered:
        order_data = order.to_dict()
        order_data["id"] = order.id
        if order.id not in order_ids:
            order_list.append(order_data)
            order_ids.add(order.id)

    if order_list:
        orders_df = pd.DataFrame(order_list)
        st.dataframe(orders_df)

        # Filter orders_df to only include orders where confirmed is False
        unconfirmed_orders_df = orders_df[orders_df['confirmed'] == False]

        selected_order = st.selectbox(
            "Select Order to Confirm", unconfirmed_orders_df['id'].unique())

        # Get list of couriers
        couriers_ref = db.collection("users").where("role", "==", "Kurir")
        couriers = couriers_ref.stream()
        courier_list = [courier.to_dict()["name"] for courier in couriers]

        courier_email = st.selectbox("Select Courier", courier_list)
        if st.button("Confirm Order"):
            db.collection("orders").document(selected_order).update({
                "confirmed": True,
                "courier": courier_email
            })
            st.success("Order confirmed and courier assigned!")
            st.experimental_set_query_params(rerun=True)
    else:
        st.text("No orders to confirm.")
else:
    st.error("Please log in as Seller to access this page.")
