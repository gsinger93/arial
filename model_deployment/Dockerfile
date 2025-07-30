# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the prediction script into the container
COPY prediction.py .

# Expose port 8080 to the outside world
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "prediction:app", "--host", "0.0.0.0", "--port", "8080"]