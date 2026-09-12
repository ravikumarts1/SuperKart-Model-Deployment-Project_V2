import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="SuperKart Sales Predictor",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 SuperKart Total Store Sales Prediction")

# Backend endpoints running on port 8000
BACKEND_URL_SINGLE = "https://glorious-halibut-g4q6qwqgww75c9q6g-8000.app.github.dev/v1/predict"
BACKEND_URL_BATCH = "https://glorious-halibut-g4q6qwqgww75c9q6g-8000.app.github.dev/v1/predict_batch"

tab1, tab2 = st.tabs(["Single Item Prediction", "Batch Prediction"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        product_id_char = st.selectbox("Product Category Code (Product_Id_Char)", ["FD", "DR", "NC"])
        product_weight = st.number_input("Product Weight", value=12.5, step=0.1)
        product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        product_allocated_area = st.number_input("Product Allocated Area", value=0.025, format="%.4f")
        product_type_category = st.selectbox("Product Type Category", [
            'Food', 'Drink', 'Non-Consumable', 'Others'
        ])
        product_mrp = st.number_input("Product MRP ($)", value=117.0, step=1.0)

    with col2:
        #store_id = st.selectbox("Store ID", ["OUT001", "OUT002", "OUT003", "OUT004"])
        store_age_years = st.number_input("Store Age (Years)", value=15, step=1)
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_location_city_type = st.selectbox("City Type", ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", [
            "Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"
        ])

    if st.button("Predict Sales"):
        # Payload aligned with engineered model features and numeric types
        payload = {
            "Product_Weight": float(product_weight),
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": float(product_allocated_area),
            "Product_MRP": float(product_mrp),
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_Char": product_id_char,
            "Store_Age_Years": int(store_age_years),
            "Product_Type_Category": product_type_category
        }

        try:
            response = requests.post(BACKEND_URL_SINGLE, json=payload)
            if response.status_code == 200:
                result = response.json()
                st.success(f"Predicted Sales: ${result.get('Predicted_Store_Sales', 0):,.2f}")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Could not connect to backend server: {e}")

with tab2:
    st.header("Batch Sales Prediction")
    uploaded_file = st.file_uploader("Upload CSV file for predictions", type=["csv"])

    if uploaded_file is not None:
        df_batch = pd.read_csv(uploaded_file)
        st.write("Uploaded Data Preview:", df_batch.head())

        if st.button("Predict Batch"):
            try:
                # Wrap batch records under the "inputs" key to match FastAPI Batch model
                # The backend expects the file directly, not wrapped in 'inputs'
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
                response = requests.post(BACKEND_URL_BATCH, files=files)

                if response.status_code == 200:
                    predictions_dict = response.json()
                    # Convert dictionary to DataFrame for display
                    predictions_df = pd.DataFrame(predictions_dict.items(), columns=['Product_Id', 'Predicted_Sales'])
                    st.write("Prediction Results:", predictions_df)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
