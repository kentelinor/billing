import os
import json
import logging
import threading
import pika
import boto3
import requests
from flask import Flask, jsonify
from botocore.exceptions import NoCredentialsError

# Flask App Setup
app = Flask(__name__)

# AWS S3 setup
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

# RabbitMQ setup
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = os.getenv("QUEUE_NAME", "s3_queue")

# Port for the Flask server
SERVER_PORT = 4000

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()

# Setup S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)

def upload_to_s3(message):
    """Uploads the message content to an S3 bucket."""
    logger.info(f"Original message: {message} (type: {type(message)})")
    try:
        if not isinstance(message, dict):
            raise TypeError(f"Expected message to be a dictionary, got {type(message)}")

        file_name = f"message_{message['timestamp']}.json"
        message_str = json.dumps(message)
        body = message_str.encode("utf-8")

        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_name,
            Body=body,
            ContentType="application/json",
        )
        logger.info(f"Successfully uploaded message to S3: {file_name}")
    except NoCredentialsError:
        logger.error("No valid AWS credentials found")
    except KeyError as e:
        logger.error(f"Missing expected key in message: {e}")
    except Exception as e:
        logger.error(f"Error uploading to S3: {e}")

def callback(ch, method, properties, body):
    """Callback function to process the message from RabbitMQ"""
    message = json.loads(body)
    logger.info(f"Received message: {message}")

    # Upload message to S3
    upload_to_s3(message)

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_messages():
    """Consume messages from RabbitMQ in a separate thread."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

        logger.info(f"Waiting for messages in {QUEUE_NAME}. To exit press CTRL+C")
        channel.start_consuming()
    except Exception as e:
        logger.error(f"Error in consumer thread: {e}")

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """Endpoint to check if the service is running."""
    return jsonify({"status": "healthy", "message": "Consumer service is running"}), 200

# Start message consumer in a background thread
@app.before_first_request
def start_consumer_thread():
    """Start the RabbitMQ consumer thread before the first request."""
    consumer_thread = threading.Thread(target=consume_messages, daemon=True)
    consumer_thread.start()

if __name__ == "__main__":
    # Run the Flask app on port 4000
    app.run(host="0.0.0.0", port=SERVER_PORT)
