# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the client files
COPY client.py /app/

# Install dependencies
RUN pip install --no-cache-dir requests

# Run the client script
CMD ["python", "client.py"]