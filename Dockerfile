# Stage 1: Builder
# Use a specific, lightweight Python version for reproducibility.
FROM python:3.11-slim as builder

# Set the working directory.
WORKDIR /app

# Install system dependencies required for OpenCV.
# Using --no-install-recommends to keep the image slim.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker's layer caching.
COPY requirements.txt .

# Install python dependencies into a virtual environment.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2: Final application image
FROM python:3.11-slim

# Set the working directory.
WORKDIR /app

# Create a non-root user to run the application for security.
RUN useradd --create-home appuser
USER appuser

# Copy the virtual environment from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Copy the application source code.
COPY --chown=appuser:appuser . .

# Set the PATH to include the venv.
ENV PATH="/opt/venv/bin:$PATH"

# --- Model Caching Note ---
# The EasyOCR and YOLO models are downloaded on the first run. For production,
# it's better to download these during the build process to avoid slow startup
# and to ensure they are available without an internet connection.
# Example (uncomment and adapt if needed):
# RUN python -c "from ultralytics import YOLO; from config import MODEL_PATH; YOLO(MODEL_PATH)"
# RUN python -c "import easyocr; easyocr.Reader(['en', 'pt'])"

# Expose the port the Flask app will run on.
EXPOSE 5001

# Set the command to run the Flask application.
CMD ["python", "app.py"]
