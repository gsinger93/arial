import os
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Define the input data model for robust validation
class PredictionInput(BaseModel):
    instances: List[List[float]]

# Initialize the FastAPI app
app = FastAPI()

# Use app.state to hold the model, which is the recommended FastAPI practice
@app.on_event("startup")
def load_model():
    """Load the model at application startup."""
    # This is the crucial change: Use the environment variable provided by Vertex AI
    model_path = os.getenv("AIP_STORAGE_URI")
    
    if model_path is None:
        print("Error: AIP_STORAGE_URI environment variable not set. Using default path.")
        # Fallback for local testing, though it won't work on Vertex AI without the env var
        model_path = "/app/baseline_xgboost_model.joblib"

    try:
        app.state.model = joblib.load(model_path)
        print(f"Model loaded successfully from {model_path}")
    except FileNotFoundError:
        print(f"FATAL: Model file not found at {model_path}. The application cannot serve predictions.")
        app.state.model = None
    except Exception as e:
        print(f"An unexpected error occurred while loading the model: {e}")
        app.state.model = None

@app.get("/health", status_code=200)
def health_check():
    """Endpoint for Vertex AI health checks."""
    # A robust health check confirms the model is actually loaded
    if app.state.model is not None:
        return {"status": "healthy"}
    else:
        # Return an unhealthy status if the model failed to load
        return {"status": "unhealthy"}, 503

@app.post("/predict")
def predict(input_data: PredictionInput):
    """Prediction endpoint."""
    if app.state.model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded or failed to load on startup.")

    try:
        prediction_input = np.array(input_data.instances)
        predictions = app.state.model.predict(prediction_input)
        return {"predictions": predictions.tolist()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error during prediction: {str(e)}")