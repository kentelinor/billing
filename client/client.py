import requests
import logging
import time
import os
from flask import Flask

# Flask server URL
app = Flask(__name__)

server_url = os.getenv("FLASK_SERVER_URL", "http://server:5000")

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s [%(levelname)s] %(message)s",  # Include timestamp, level, and message
)

# JSON message to send
from datetime import datetime
json_message = {
    "key": "value",
    "message": "Hello from the client!",
    "timestamp": datetime.now().isoformat()
}


# Get current timestamp

MAX_RETRIES = 5  # Number of retry attempts
RETRY_DELAY = 5  # Delay in seconds between retries

@app.route('/send-json', methods=['POST'])
def send_json_to_server():
    for attempt in range(1, MAX_RETRIES + 1):
        logging.info(f"Attempt {attempt} to send message...")
        try:
            response = requests.post(f"{server_url}/publish", json=json_message)

            if response.status_code == 202:
                logging.info("Message successfully sent to the server!")
                return
            else:
                logging.error(f"Failed to send message. Status code: {response.status_code}")
                logging.error(f"Response: {response.text}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Error while sending message: {e}")

        if attempt < MAX_RETRIES:
            logging.info(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
    
    logging.error("Max retries exceeded. Failed to send message.")

if __name__ == "__main__":
    app.run(debug=True)