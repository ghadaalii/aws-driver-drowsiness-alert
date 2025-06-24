import json
import ssl
import time
from datetime import datetime
from src.client.mqtt_client import DrowsinessAlertClient
import uuid

# --- Configuration ---
CLIENT_ID = "test-client-001"
ENDPOINT = "a33zskt3eonsh8-ats.iot.us-east-1.amazonaws.com"
PORT = 8883
CERT_PATH = "certificates/device.pem.crt"
KEY_PATH = "certificates/private.pem.key"
CA_PATH = "certificates/AmazonRootCA1.pem"
TOPIC = "vehicle/alerts/drowsiness"

# --- Custom MQTT Client with subscribe and message print ---
class TestMQTTClient(DrowsinessAlertClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to AWS IoT Core successfully")
            # Subscribe to the topic
            self.client.subscribe(TOPIC)
            print(f"Subscribed to topic: {TOPIC}")
        else:
            print(f"Failed to connect with code: {rc}")

    def on_message(self, client, userdata, msg):
        print(f"\n[RECEIVED] Topic: {msg.topic}")
        print(f"Payload: {msg.payload.decode()}")

if __name__ == "__main__":
    # Initialize client
    client = TestMQTTClient(
        client_id=CLIENT_ID,
        endpoint=ENDPOINT,
        cert_path=CERT_PATH,
        key_path=KEY_PATH,
        ca_path=CA_PATH
    )

    # Connect and start loop
    client.connect()
    time.sleep(2)  # Wait for connection and subscription

    # Prepare alert data (updated to match new alert table structure)
    alert = {
        "alert_id": str(uuid.uuid4()),
        "driver_id": "DRIVER123",
        "timestamp": datetime.utcnow().isoformat(),
        "location": {
            "latitude": 30.0444,
            "longitude": 31.2357,
            "description": "Cairo Ring Road, near Gate 3"
        },
        "message": "Driver fell asleep",
        "processed": False
    }

    # Publish alert
    print("\nPublishing alert...")
    client.client.publish(
        topic=TOPIC,
        payload=json.dumps(alert),
        qos=1
    )

    # Wait to receive messages (10 seconds)
    print("\nWaiting for messages (10 seconds)...")
    time.sleep(10)

    # Disconnect
    client.disconnect()
    print("Disconnected.") 