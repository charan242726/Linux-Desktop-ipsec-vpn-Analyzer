# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the required code directories
COPY backend/ /app/backend/
COPY ml/ /app/ml/
COPY analyzer/ /app/analyzer/
COPY rules/ /app/rules/

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
