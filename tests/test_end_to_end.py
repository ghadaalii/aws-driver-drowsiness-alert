import time
import json
import uuid
import threading
import boto3
import paho.mqtt.client as mqtt

# AWS IoT Core settings
ENDPOINT = "a33zskt3eonsh8-ats.iot.us-east-1.amazonaws.com"
PORT = 8883
CA_PATH = "certificates/AmazonRootCA1.pem"
CERT_PATH = "certificates/device.pem.crt"
KEY_PATH = "certificates/private.pem.key"
CLIENT_ID = f"test-client-{uuid.uuid4()}"
ALERT_TOPIC = "vehicle/alerts/drowsiness"
ACK_TOPIC = "vehicle/alerts/ack"
DYNAMODB_TABLE = "drowsiness_alerts-dev"

# Generate a unique alert
alert_id = str(uuid.uuid4())
alert_payload = {
    "alert_id": alert_id,
    "driver_id": "test-driver-id",
    "location": {
        "description": "Cairo, Egypt",
        "latitude": 30.0444,
        "longitude": 31.2357
    },
    "message": "Driver fell asleep",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
}

# Flag to indicate ack received
ack_received = threading.Event()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(ACK_TOPIC, qos=1)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received message on {msg.topic}: {payload}")
    try:
        data = json.loads(payload)
        if data.get("alert_id") == alert_id:
            print("✅ Ack received for our alert!")
            ack_received.set()
    except Exception as e:
        print("Error parsing ack:", e)

def publish_alert():
    client = mqtt.Client(client_id=CLIENT_ID)
    client.tls_set(ca_certs=CA_PATH, certfile=CERT_PATH, keyfile=KEY_PATH)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(ENDPOINT, PORT, 60)
    client.loop_start()
    print(f"Publishing alert to {ALERT_TOPIC}: {json.dumps(alert_payload)}")
    client.publish(ALERT_TOPIC, json.dumps(alert_payload), qos=1)
    # Wait for ack or timeout
    if ack_received.wait(timeout=20):
        print("Ack received within 20 seconds.")
    else:
        print("❌ No ack received within 20 seconds.")
    client.loop_stop()
    client.disconnect()

def check_dynamodb():
    dynamodb = boto3.client("dynamodb")
    print(f"Checking DynamoDB table {DYNAMODB_TABLE} for alert_id {alert_id}...")
    response = dynamodb.get_item(
        TableName=DYNAMODB_TABLE,
        Key={"alert_id": {"S": alert_id}}
    )
    if "Item" in response:
        print("✅ Alert found in DynamoDB:", response["Item"])
    else:
        print("❌ Alert not found in DynamoDB.")

if __name__ == "__main__":
    publish_alert()
    # Wait a few seconds for Lambda/DynamoDB propagation
    time.sleep(5)
    check_dynamodb() 