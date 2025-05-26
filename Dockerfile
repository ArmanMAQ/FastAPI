# Start with an official Python runtime as a parent image
FROM python:3.11
# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces image size
# --default-timeout=100 can help with slower connections
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --default-timeout=100

# Copy the content of the local src directory to the working directory
COPY . .

# Make port 8000 available to the world outside this container
# App Service will automatically map an external port to this.
# It also sets the PORT environment variable (e.g., to 80 or 8000 or other).
# Your application should listen on the port specified by the PORT env var.
# Gunicorn/Uvicorn can be configured to listen on $PORT.
# EXPOSE 8000 # This is more for documentation; App Service uses WEBSITES_PORT or PORT env var.

# Define environment variable (optional, can be overridden)
# ENV MODULE_NAME="main"
# ENV VARIABLE_NAME="app"

# Command to run the application using Gunicorn with Uvicorn workers
# It's good practice to have an entrypoint script or run gunicorn directly.
# Gunicorn will listen on 0.0.0.0 and the port specified by the PORT env var.
# If PORT env var is not set, Gunicorn defaults to 8000.
# Azure App Service will set the PORT environment variable (typically 8000 or 80).
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:$PORT"]