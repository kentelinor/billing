from flask import Flask, jsonify
import pika
from pika.exceptions import AMQPConnectionError
import json
import threading
import logging
import psycopg2
from datetime import datetime
import os
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()

# RabbitMQ setup
RABBITMQ_HOST = "rabbitmq"  # Hostname of the RabbitMQ server
QUEUE_NAME = "vm_handler_queue"  # The queue to consume messages from

db_config = {
    "host": "vm-events.cbgysoossqru.eu-north-1.rds.amazonaws.com",
    "port": 5432,
    "dbname": "vm-events",
    "user": "postgres",
    "password": os.getenv("VMEVENTS_DB_PASSWORD")
}

def write_to_db(message):
    # Process the message (for example, print it)
    try:
    # Connect to the database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        message["timestamp"] = datetime.strptime(message["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")

        # SQL query to insert data
        insert_query = """
        INSERT INTO vm_events (vm_name, event, created_at)
        VALUES (%s, %s, %s);
        """
        # Execute the query
        cursor.execute(insert_query, (message["vm"], message["status"], message["timestamp"]))

        # Commit the transaction
        conn.commit()
        print("Data inserted successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def callback(ch, method, properties, body):
    """Callback function to process messages from RabbitMQ"""
    message = json.loads(body)
    logger.info(f"Received message: {message}")

    # You can add any other processing logic here
    write_to_db(message)
    

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    logger.info("Message acknowledged.")

def consume_messages():
    """Consume messages from RabbitMQ in a separate thread with retry logic"""
    while True:
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
            break  # Exit the loop if connection is successful
        except AMQPConnectionError as e:
            logger.error(f"Connection to RabbitMQ failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
            break  # Stop the loop if other errors occur
def get_all_events():
    """Retrieve all events from the database"""
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # SQL query to fetch all events
        select_query = "SELECT vm_name, event, created_at FROM vm_events;"
        cursor.execute(select_query)

        # Fetch all rows from the result
        rows = cursor.fetchall()

        # Convert the result into a list of dictionaries
        events = []
        for row in rows:
            events.append({
                "vm_name": row[0],
                "event": row[1],
                "created_at": row[2].isoformat()  # Convert datetime to ISO format
            })

        return events

    except Exception as e:
        logger.error(f"Error retrieving events: {e}")
        return []

    finally:
        # Close the connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Route to get all events
@app.route('/events', methods=['GET'])
def get_events():
    """Fetch and return all events from the database in JSON format"""
    events = get_all_events()
    return jsonify(events), 200

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
    app.run(host="0.0.0.0", port=8000)
