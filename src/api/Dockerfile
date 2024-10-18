# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install pipenv
RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

# Install dependencies
RUN pipenv install

# Copy the current directory contents into the container at /app
COPY . .

# Set the PYTHONPATH to include the virtual environment site-packages
ENV PYTHONPATH /root/.local/share/virtualenvs/app-*/lib/python3.9/site-packages

# Run preprocess.py when the container launches
CMD ["pipenv", "run", "fastapi", "run", "app.py"]
