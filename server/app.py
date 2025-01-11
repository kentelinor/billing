from flask import Flask, request, jsonify
from flask_cors import CORS
import pika
import json
import os
import time
import logging


app = Flask(__name__)
CORS(app)

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')  # Default to 'rabbitmq'
S3_QUEUE_NAME = os.getenv('S3_QUEUE_NAME', 's3_queue')  # Default to 'my_queue'
S3_QUEUE_NAME = os.getenv('VM_HANDLER_QUEUE_NAME', 'vm_handler_queue')  # Default to 'my_queue'


logging.basicConfig(
                level=logging.INFO,  # Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
                format="%(asctime)s [%(levelname)s] %(message)s",  # Include timestamp, level, and message
            )
#When the server starts, RabbitMQ might not be ready yet. Add a retry mechanism to wait for RabbitMQ to be fully up before attempting a connection:
def connect_to_rabbitmq():
    for attempt in range(5):  # Retry 5 times
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            # Configure logging
            
            logging.info(f"server connected to rabbitmq")

            return connection
        except pika.exceptions.AMQPConnectionError as e:
            #app.logger.error(f"RabbitMQ not ready, retrying in 5 seconds... ({attempt + 1}/5)")
            app.logger.error(f"RabbitMQ not ready, retrying in 5 seconds... ({attempt + 1}/5). Error: {e}")

            time.sleep(5)
    raise Exception("Failed to connect to RabbitMQ after 5 attempts")

def publish_to_rabbitmq(message):
    try:
        # Establish connection to RabbitMQ
        connection = connect_to_rabbitmq()
        #connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        # Declare the queue (idempotent operation)
        channel.queue_declare(queue=S3_QUEUE_NAME, durable=True)

        # Publish the message to the queue
        channel.basic_publish(
            exchange='',
            routing_key=S3_QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )
         # Declare the queue (idempotent operation)
        channel.queue_declare(queue=S3_QUEUE_NAME, durable=True)

        # Publish the message to the queue
        channel.basic_publish(
            exchange='',
            routing_key=S3_QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )

        # Close the connection
        connection.close()

    except Exception as e:
        app.logger.error(f"Failed to publish message to RabbitMQ: {str(e)}")
        raise

@app.route('/publish', methods=['POST'])
def publish_message():
    try:
        # Parse JSON payload from the client
        print('here')
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        # Publish to RabbitMQ
        publish_to_rabbitmq(data)

        # Return 202 Accepted
        return '', 202

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    try:
       

        # Return 202 Accepted
        return '', 202

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)