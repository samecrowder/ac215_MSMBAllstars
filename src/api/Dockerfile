# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy requirements files first for better caching
COPY Pipfile .
COPY Pipfile.lock .

# Install dependencies
RUN pipenv install

# Copy the current directory contents into the container at /app
COPY . .

RUN mkdir -p /gcs_cache && chmod 777 /gcs_cache

# Add the app directory to PYTHONPATH
ENV PYTHONPATH="/app"

# Run the application
CMD ["pipenv", "run", "fastapi", "run", "app.py", "--port", "$PORT"]
