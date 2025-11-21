# Stage 1: Build and install dependencies
# Using a specific version of python for reproducibility
FROM python:3.10-slim as builder

# Set the working directory
WORKDIR /app

# Install system dependencies required for OpenCV and other libraries
# RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 --no-install-recommends

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
# This step is separated to leverage Docker's layer caching
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# Stage 2: Final application image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required for OpenCV at runtime
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copy the pre-built wheels from the builder stage
COPY --from=builder /app/wheels /wheels/

# Install the wheels
RUN pip install --no-cache /wheels/*

# Copy the application source code
COPY . .

# --- IMPORTANT NOTE ON MODELS ---
# The EasyOCR and YOLO models are downloaded on the first run inside the container.
# This means the first startup will be slow and require an internet connection.
# For a production setup, consider creating a script to download these models
# during the Docker build process itself.
# RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
# RUN python -c "import easyocr; easyocr.Reader(['en', 'pt'])"


# Expose the port Streamlit will run on
EXPOSE 8501

# Set the command to run the Streamlit application
# The --server.runOnSave=false flag is a good practice for production
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.runOnSave=false"]

