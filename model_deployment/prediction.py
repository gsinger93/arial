import os
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

class PredictionInput(BaseModel):
    instances: List[List[float]]

app = FastAPI()

@app.on_event("startup")
def load_model():
    """Load the model at application startup using the path provided by Vertex AI."""
    # This is the standard path Vertex AI provides. There is no fallback.
    model_dir = os.getenv("AIP_STORAGE_URI")
    
    if not model_dir:
        # If this variable is not set, the deployment is fundamentally misconfigured.
        print("FATAL: AIP_STORAGE_URI environment variable not found. Model cannot be loaded.")
        app.state.model = None
        return

    # Construct the full path to the model file
    model_path = os.path.join(model_dir, "baseline_xgboost_model.joblib")
    print(f"Attempting to load model from: {model_path}")
    
    try:
        app.state.model = joblib.load(model_path)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"FATAL: Failed to load model. Error: {e}")
        app.state.model = None

@app.get("/health", status_code=200)
def health_check():
    """A robust health check that fails if the model is not loaded."""
    if hasattr(app.state, 'model') and app.state.model is not None:
        return {"status": "healthy"}
    else:
        # Return an error status code if the model isn't loaded.
        # This will cause the deployment to fail clearly if there's a problem.
        raise HTTPException(status_code=503, detail="Model not loaded")

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
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")