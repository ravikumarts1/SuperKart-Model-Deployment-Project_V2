import os
import numpy as np
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize the Flask application
superkart_model_api = Flask("SuperKart Model Deployment_V1")

# Get absolute path to the directory where app.py resides
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "superkart_model_v1.joblib")

# Load the trained machine learning model
model = joblib.load(MODEL_PATH)

# Home / Health check endpoint
@superkart_model_api.get('/')
def home():
    """Returns a simple welcome message."""
    return "Welcome to the SuperKart Model Deployment V1 API!"

# Single Prediction Endpoint
@superkart_model_api.post('/v1/predict')
def predict_single():
    """
    Handles POST requests for a single product sales prediction.
    Extracts explicit product features from the incoming JSON payload.
    """
    data = request.get_json()

    # Safely extract incoming parameters with fallback defaults
    sample = {
        'Product_Weight': data.get('Product_Weight'),
        'Product_Sugar_Content': data.get('Product_Sugar_Content'),
        'Product_Allocated_Area': data.get('Product_Allocated_Area'),
        'Product_MRP': data.get('Product_MRP'),
        'Store_Size': data.get('Store_Size'),
        'Store_Location_City_Type': data.get('Store_Location_City_Type'),
        'Store_Type': data.get('Store_Type'),
        'Product_Id_Char': data.get('Product_Id_Char'),
        'Store_Age_Years': data.get('Store_Age_Years'),
        'Product_Type_Category': data.get('Product_Type_Category')
    }

    # Convert dictionary into DataFrame expected by the model
    input_data = pd.DataFrame([sample])

    # Generate prediction on raw sales scale
    prediction = model.predict(input_data)[0]
    predicted_sales = round(float(prediction), 2)

    return jsonify({'Predicted_Store_Sales': predicted_sales})

# Batch Prediction Endpoint
@superkart_model_api.post('/v1/predict_batch')
def predict_batch():
    """
    Handles POST requests containing a CSV file for batch predictions.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    input_data = pd.read_csv(file)

    # Generate predictions for all rows
    raw_predictions = model.predict(input_data).tolist()
    predicted_sales = [round(float(val), 2) for val in raw_predictions]

    # Map output to Product_Id if present, otherwise use row index
    if 'Product_Id' in input_data.columns:
        item_ids = input_data['Product_Id'].tolist()
        output_dict = dict(zip(item_ids, predicted_sales))
    else:
        output_dict = {f"Item_{i}": sales for i, sales in enumerate(predicted_sales)}

    return jsonify(output_dict)

if __name__ == '__main__':
    # Force Flask to run on port 8000 and bind externally
    superkart_model_api.run(host='0.0.0.0', port=8000, debug=True)
