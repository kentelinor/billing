# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app into the container
COPY app.py /app/

# Expose the Flask app port
EXPOSE 6000

# Define the command to run the app
CMD ["python", "app.py"]
