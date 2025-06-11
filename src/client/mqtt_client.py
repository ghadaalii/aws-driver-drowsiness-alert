"""
MQTT Client for the Driver Drowsiness Alert System
"""

import paho.mqtt.client as mqtt
import json
import time
import os
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

class DrowsinessAlertClient:
    def __init__(self, client_id, endpoint, port=8883, cert_path=None, key_path=None, ca_path=None):
        """
        Initialize MQTT client for AWS IoT Core
        
        Args:
            client_id (str): Unique client identifier
            endpoint (str): AWS IoT Core endpoint
            port (int): Port number (default: 8883 for TLS)
            cert_path (str): Path to client certificate
            key_path (str): Path to private key
            ca_path (str): Path to root CA certificate
        """
        self.client_id = client_id
        self.endpoint = endpoint
        self.port = port
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=client_id)
        
        # Set up TLS
        if all([cert_path, key_path, ca_path]):
            self.client.tls_set(
                ca_certs=ca_path,
                certfile=cert_path,
                keyfile=key_path,
                cert_reqs=mqtt.ssl.CERT_REQUIRED,
                tls_version=mqtt.ssl.PROTOCOL_TLSv1_2,
                ciphers=None
            )
        
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Initialize AWS IoT Core client
        self.iot_client = boto3.client('iot')
        
    def connect(self):
        """Connect to AWS IoT Core"""
        try:
            self.client.connect(self.endpoint, self.port, keepalive=60)
            self.client.loop_start()
            print(f"Connected to AWS IoT Core at {self.endpoint}")
        except Exception as e:
            print(f"Failed to connect to AWS IoT Core: {str(e)}")
            raise
    
    def disconnect(self):
        """Disconnect from AWS IoT Core"""
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from AWS IoT Core")
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to AWS IoT Core"""
        if rc == 0:
            print("Connected to AWS IoT Core successfully")
            # Subscribe to relevant topics
            self.client.subscribe("vehicle/alerts/drowsiness")
        else:
            print(f"Failed to connect to AWS IoT Core with code: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            payload = json.loads(msg.payload.decode())
            print(f"Received message on topic {msg.topic}: {payload}")
            # Process message as needed
        except Exception as e:
            print(f"Error processing message: {str(e)}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected"""
        if rc != 0:
            print(f"Unexpected disconnection from AWS IoT Core with code: {rc}")
    
    def publish_alert(self, driver_id, drowsiness_level):
        """
        Publish drowsiness alert to AWS IoT Core
        
        Args:
            driver_id (str): ID of the driver
            drowsiness_level (float): Level of drowsiness detected
        """
        try:
            payload = {
                'driver_id': driver_id,
                'drowsiness_level': drowsiness_level,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Publish to AWS IoT Core
            self.client.publish(
                topic="vehicle/alerts/drowsiness",
                payload=json.dumps(payload),
                qos=1
            )
            print(f"Published alert for driver {driver_id}")
            
        except Exception as e:
            print(f"Failed to publish alert: {str(e)}")
            raise
    
    def get_thing_shadow(self, thing_name):
        """
        Get the current state of an IoT thing
        
        Args:
            thing_name (str): Name of the IoT thing
        """
        try:
            response = self.iot_client.get_thing_shadow(thingName=thing_name)
            return json.loads(response['payload'].read())
        except ClientError as e:
            print(f"Error getting thing shadow: {str(e)}")
            raise
    
    def update_thing_shadow(self, thing_name, state):
        """
        Update the state of an IoT thing
        
        Args:
            thing_name (str): Name of the IoT thing
            state (dict): New state to update
        """
        try:
            payload = {
                'state': {
                    'reported': state
                }
            }
            self.iot_client.update_thing_shadow(
                thingName=thing_name,
                payload=json.dumps(payload)
            )
            print(f"Updated shadow for thing {thing_name}")
        except ClientError as e:
            print(f"Error updating thing shadow: {str(e)}")
            raise 