# Use an ultra-slim Python base image
FROM python:3.12-alpine

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies and Python dependencies
RUN apk update && apk add --no-cache \
    libffi-dev \
    gcc \
    musl-dev \
    python3-dev \
    py3-pip \
    && pip install --no-cache-dir --upgrade pip

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ .

# Set environment variables for BACnet communication if needed
ENV BACNET_IP=0.0.0.0

# Expose BACnet UDP port
EXPOSE 47808/udp

# Run the app
CMD ["python", "main.py", "--name", "BacnetWeatherStation", "--instance", "3456789", "--debug"]
