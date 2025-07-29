# Use a lightweight Python 3.9 base image
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies first (good for Docker caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your trained model file and the prediction script into the container
COPY baseline_xgboost_model.joblib .
COPY prediction.py .

# Define an environment variable for the model filename
# This makes it easy to change the model filename if needed without rebuilding the image
ENV MODEL_FILENAME=baseline_xgboost_model.joblib

# Expose the port that your FastAPI application will listen on (Vertex AI default is 8080)
EXPOSE 8080

# Command to run the prediction server using Uvicorn
# 'prediction:app' means look for the 'app' FastAPI object in 'prediction.py'
# '--host 0.0.0.0' makes it accessible from outside the container
# '--port 8080' sets the listening port
CMD ["uvicorn", "prediction:app", "--host", "0.0.0.0", "--port", "8080"]