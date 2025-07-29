import numpy as np
import xgboost as xgb
import joblib
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# Define the input data model for FastAPI
class PredictionInput(BaseModel):
    instances: List[List[float]] # Expects a list of prediction requests, e.g., [[150.5]]

# Initialize FastAPI app
app = FastAPI()

# Global variable to store the loaded model
model = None

@app.on_event("startup")
async def load_model():
    """Load the model when the FastAPI application starts up."""
    global model
    
    # Get the model filename from an environment variable (set in Dockerfile)
    model_filename = os.getenv("MODEL_FILENAME", "baseline_xgboost_model.joblib")
    # Construct the full path to the model file inside the container
    model_path = os.path.join("/app", model_filename) 

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    model = joblib.load(model_path)
    print(f"Model loaded successfully from {model_path}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return Response(response="OK", status=200)

@app.post("/predict")
async def predict(input_data: PredictionInput):
    """Prediction endpoint for the XGBoost model."""
    if model is None:
        raise RuntimeError("Model not loaded. Ensure startup event was successful.")

    try:
        # Convert the incoming instances (e.g., [[150.5]]) to a NumPy array
        np_instances = np.array(input_data.instances)

        # --- THIS IS THE CRUCIAL FIX FOR DMatrix ---
        # Convert the NumPy array into an xgboost.DMatrix.
        dmatrix_instances = xgb.DMatrix(np_instances)

        # Make predictions using the DMatrix
        predictions = model.predict(dmatrix_instances)

        # Return predictions as a standard Python list
        return {"predictions": predictions.tolist()}
    except Exception as e:
        print(f"Error during prediction: {e}")
        # It's good practice to re-raise or return a structured error response
        raise e

@app.get("/health")
async def health_check():
    """Health check endpoint for Vertex AI."""
    return {"status": "healthy"}