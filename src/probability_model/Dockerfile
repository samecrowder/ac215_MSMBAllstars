# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Force CPU mode
ENV CUDA_VISIBLE_DEVICES=""
ENV TORCH_DEVICE="cpu"

# Install pipenv
RUN pip install pipenv

# Install dependencies directly with pip, starting with torch CPU version
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir fastapi[standard] \
    pydantic \
    python-dotenv \
    google-cloud-storage \
    numpy \
    pandas \
    scikit-learn \
    && rm -rf /root/.cache/pip

# Copy your application code
COPY . .

RUN mkdir -p /gcs_cache && chmod 777 /gcs_cache

# Run the FastAPI app
CMD ["pipenv", "run", "fastapi", "run", "app.py", "--port", "$PORT"]
