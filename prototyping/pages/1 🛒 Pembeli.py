import os
import streamlit as st
import pandas as pd
from PIL import Image
from utils.firebase_config import db
from utils.pdf_generator import generate_receipt
from datetime import datetime

st.sidebar.markdown(
    """
    ##### **Visit our repository [here](https://github.com/rizkyyanuark/RPL-HarmonCorp)!**
    """
)
# Check if user is logged in
if st.session_state.role == 'Pembeli' and 'signout' in st.session_state and st.session_state.signout:
    logo_path = os.path.join("image", "logo.jpg")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
    else:
        logo = None

    st.set_page_config(
        page_title="Pembeli",
        page_icon=logo if logo else None,
    )

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
    st.title("Product dari Platform Harmon Corp 👟")

    # Load products from Firestore
    products = load_products()

    if products:
        df = pd.DataFrame(products)
        st.subheader("Daftar Barang")
        st.dataframe(df)

        # Input untuk membeli produk
        st.subheader("Beli Produk")
        product_name = st.selectbox("Pilih Produk", df['name'])
        quantity = st.number_input("Jumlah", min_value=1, step=1)
        payment_method = st.selectbox(
            "Metode Pembayaran", ["Credit Card", "Debit Card", "PayPal", "Cash"])

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
                st.success("Pembelian berhasil!")
                pdf_stream = generate_receipt(order_data)

                st.download_button(label="Download Receipt", data=pdf_stream,
                                   file_name="receipt.pdf", mime='application/pdf')
            else:
                st.error("Stok tidak mencukupi.")
    else:
        st.text("Tidak ada produk yang tersedia.")
else:
    st.error("Please log in as Pembeli to access this page.")
