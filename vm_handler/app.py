from flask import Flask, jsonify
import pika
import json
import threading
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()

# RabbitMQ setup
RABBITMQ_HOST = "rabbitmq"  # Hostname of the RabbitMQ server
QUEUE_NAME = "vm_handler_queue"  # The queue to consume messages from

def callback(ch, method, properties, body):
    """Callback function to process messages from RabbitMQ"""
    message = json.loads(body)
    logger.info(f"Received message: {message}")

    # Process the message (for example, print it)
    # You can add any other processing logic here

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    logger.info("Message acknowledged.")

def consume_messages():
    """Consume messages from RabbitMQ in a separate thread"""
    try:
        # Establish a connection to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        # Declare the queue (ensure it exists)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        # Set up the consumer
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

        logger.info(f"Waiting for messages in {QUEUE_NAME}. To exit press CTRL+C")
        channel.start_consuming()
    except Exception as e:
        logger.error(f"Error consuming messages: {e}")

# Health check route
@app.route('/health', methods=['GET'])
def health():
    """Health check route"""
    return jsonify({"status": "healthy", "message": "The app is running successfully!"}), 200

@app.route('/')
def home():
    return jsonify({"message": "Hello, World!"})

if __name__ == '__main__':
    # Start the RabbitMQ message consumer in a separate thread before running the Flask app
    consumer_thread = threading.Thread(target=consume_messages, daemon=True)
    consumer_thread.start()

    # Run the Flask app on port 6000
    app.run(host="0.0.0.0", port=6000)
