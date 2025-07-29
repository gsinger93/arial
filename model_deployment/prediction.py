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
    # Vertex AI automatically sets this env var to the model's path in GCS
    model_path = os.getenv("AIP_STORAGE_URI", "/app/baseline_xgboost_model.joblib")
    
    try:
        app.state.model = joblib.load(model_path)
        print(f"Model loaded successfully from {model_path}")
    except Exception as e:
        print(f"Error loading model: {e}")
        app.state.model = None

@app.get("/health", status_code=200)
def health_check():
    """Endpoint for Vertex AI health checks."""
    return {"status": "healthy"}

@app.post("/predict")
def predict(input_data: PredictionInput):
    """Prediction endpoint."""
    if app.state.model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")

    try:
        # Convert input directly to a NumPy array
        prediction_input = np.array(input_data.instances)
        
        # The scikit-learn wrapper handles the rest
        predictions = app.state.model.predict(prediction_input)
        
        return {"predictions": predictions.tolist()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")