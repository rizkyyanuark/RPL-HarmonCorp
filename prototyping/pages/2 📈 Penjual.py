import os
import streamlit as st
import pandas as pd
from PIL import Image
from utils.firebase_config import db

st.sidebar.markdown(
    """
    ##### **Visit our repository [here](https://github.com/rizkyyanuark/RPL-HarmonCorp)!**
    """
)
# Check if user is logged in
if st.session_state.role == 'Penjual' and 'signout' in st.session_state and st.session_state.signout:
    logo_path = os.path.join("image", "logo.jpg")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
    else:
        logo = None

    st.set_page_config(
        page_title="Penjual",
        page_icon=logo if logo else None,
    )

    st.title('Penjual Page')
    st.text(f'Hello, {st.session_state.username}!')

    # Form to add a new product
    st.subheader("Add New Product")
    product_name = st.text_input("Product Name")
    product_price = st.number_input("Product Price", min_value=0.0, step=0.01)
    product_stock = st.number_input("Product Stock", min_value=0, step=1)
    product_store = st.text_input("Store Name")

    if st.button("Add Product"):
        product_data = {
            "name": product_name,
            "price": product_price,
            "stock": int(product_stock),
            "store": product_store,
            "seller": st.session_state.username
        }
        db.collection('products').add(product_data)
        st.success("Product added successfully!")

    # Display all products added by the seller
    st.subheader("Your Products")
    products_ref = db.collection('products').where(
        'seller', '==', st.session_state.username)
    products = products_ref.stream()

    product_list = []
    for product in products:
        product_data = product.to_dict()
        product_data['id'] = product.id
        product_list.append(product_data)

    if product_list:
        products_df = pd.DataFrame(product_list)
        st.dataframe(products_df)
    else:
        st.text("No products found.")

    # Display orders for confirmation
    st.subheader("Confirm Orders")
    product_store = st.text_input("Store Name for Orders", value=product_store)
    orders_ref = db.collection('orders').where(
        'store', '==', product_store).where('confirmed', '==', False)
    orders = orders_ref.stream()

    order_list = []
    for order in orders:
        order_data = order.to_dict()
        order_data['id'] = order.id
        order_list.append(order_data)

    if order_list:
        orders_df = pd.DataFrame(order_list)
        st.dataframe(orders_df)

        order_id = st.selectbox("Select Order to Confirm", orders_df['id'])

        # Get list of couriers
        couriers_ref = db.collection('users').where('role', '==', 'Kurir')
        couriers = couriers_ref.stream()
        courier_list = [courier.to_dict()['name'] for courier in couriers]

        courier_email = st.selectbox("Select Courier", courier_list)
        if st.button("Confirm Order"):
            db.collection('orders').document(order_id).update({
                'confirmed': True,
                'courier': courier_email
            })
            st.success("Order confirmed and courier assigned!")
    else:
        st.text("No orders to confirm.")
else:
    st.error("Please log in as Penjual to access this page.")
