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

# Use app.state to hold the model, the recommended FastAPI practice
@app.on_event("startup")
def load_model():
    """Load the model at application startup."""
    # This is the crucial change: We get the directory from Vertex AI...
    model_dir = os.getenv("AIP_STORAGE_URI")
    
    if model_dir is None:
        print("FATAL: AIP_STORAGE_URI environment variable not set. Cannot find model.")
        app.state.model = None
        return

    # ...and then we join it with our specific model filename.
    model_path = os.path.join(model_dir, "baseline_xgboost_model.joblib")
    
    try:
        app.state.model = joblib.load(model_path)
        print(f"Model loaded successfully from {model_path}")
    except Exception as e:
        print(f"FATAL: Error loading model from {model_path}: {e}")
        app.state.model = None

@app.get("/health", status_code=200)
def health_check():
    """Endpoint for Vertex AI health checks."""
    if app.state.model is not None:
        return {"status": "healthy"}
    else:
        # If the model failed to load, the service is unhealthy.
        return {"status": "unhealthy"}, 500

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