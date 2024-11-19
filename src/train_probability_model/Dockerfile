# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy only the Pipfile initially
COPY Pipfile .

# Install dependencies
RUN pipenv install

# Copy the package directory into the container
COPY package /app/package

# Install the local package in development mode
RUN pipenv run pip install -e /app/package

# Set the PYTHONPATH to include the virtual environment site-packages
ENV PYTHONPATH /root/.local/share/virtualenvs/app-*/lib/python3.9/site-packages

# Run train_model.py when the container launches
CMD ["pipenv", "run", "python", "package/trainer/train_model.py"]
