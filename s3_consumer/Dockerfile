# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the consumer script into the container
COPY consumer.py /app/

# Install required Python libraries
RUN pip install --no-cache-dir pika boto3 requests flask

# Expose the new port for the Flask server
EXPOSE 4000

# Run the consumer script
CMD ["python", "consumer.py"]
