import streamlit as st
import pandas as pd
from PIL import Image
import os
from utils.firebase_config import db

# Check if user is logged in
if st.session_state.role == 'Kurir' and 'signout' in st.session_state and st.session_state.signout:
    logo_path = os.path.join("images", "logo.jpg")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
    else:
        logo = None

    st.set_page_config(
        page_title="Kurir",
        page_icon=logo if logo else None,
    )

    st.title('Kurir Page')
    st.text(f'Hello, {st.session_state.username}!')

    # Display orders assigned to the courier
    st.subheader("Assigned Orders")
    assigned_orders_ref = db.collection('orders').where(
        'courier', '==', st.session_state.username).where('confirmed', '==', True)
    assigned_orders = assigned_orders_ref.stream()

    assigned_orders_list = []
    for order in assigned_orders:
        order_data = order.to_dict()
        order_data['id'] = order.id
        assigned_orders_list.append(order_data)

    if assigned_orders_list:
        orders_df = pd.DataFrame(assigned_orders_list)
        st.dataframe(orders_df)

        selected_order = st.selectbox(
            "Select Order to Mark as Delivered", orders_df['id'].unique())

        if st.button("Mark as Delivered"):
            db.collection('orders').document(selected_order).update({
                'delivered': True
            })
            st.success("Order marked as delivered!")
    else:
        st.write("No assigned orders found.")
else:
    st.error("Please log in as Kurir to access this page.")
