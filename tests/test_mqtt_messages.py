"""
Test script for sending JSON messages via MQTT to AWS IoT Core
"""

import json
import time
import unittest
from src.client.mqtt_client import DrowsinessAlertClient
from src.config import IOT_ENDPOINT, IOT_PORT, CERT_PATH, KEY_PATH, ROOT_CA_PATH
from datetime import datetime

class TestMQTTMessages(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Initialize the MQTT client
        self.client = DrowsinessAlertClient(
            client_id="test-client-1",
            endpoint=IOT_ENDPOINT,
            port=IOT_PORT,
            cert_path=CERT_PATH,
            key_path=KEY_PATH,
            ca_path=ROOT_CA_PATH
        )

    def test_send_driver_profile(self):
        """Test sending a driver profile message"""
        try:
            # Connect to AWS IoT Core
            print("Connecting to AWS IoT Core...")
            self.client.connect()
            time.sleep(2)  # Wait for connection to establish

            # Send a driver profile
            print("\nSending driver profile...")
            driver_profile = {
                "id": "DRIVER123456",
                "name": "John Doe",
                "gender": "male",
                "date_of_birth": "1990-01-01",
                "weight": 75.5,
                "height": 180.0,
                "emergency_contact": "+1234567890",
                "blood_type": "A+",
                "chronic_diseases": ["Hypertension"],
                "allergies": ["Penicillin"],
                "last_updated": datetime.utcnow().isoformat()
            }
            
            self.client.client.publish(
                topic="vehicle/driver/profile",
                payload=json.dumps(driver_profile),
                qos=1
            )
            print("Driver profile sent successfully!")
            time.sleep(1)  # Wait a bit between messages

        except Exception as e:
            self.fail(f"Error sending driver profile: {str(e)}")
        
        finally:
            # Disconnect from AWS IoT Core
            print("\nDisconnecting from AWS IoT Core...")
            self.client.disconnect()

    def test_send_drowsiness_alert(self):
        """Test sending a drowsiness alert message"""
        try:
            # Connect to AWS IoT Core
            print("Connecting to AWS IoT Core...")
            self.client.connect()
            time.sleep(2)  # Wait for connection to establish

            # Send a drowsiness alert
            print("\nSending drowsiness alert...")
            alert = {
                "driver_id": "DRIVER123456",
                "drowsiness_level": 0.85,
                "confidence": 0.92,
                "location": {
                    "latitude": 37.7749,
                    "longitude": -122.4194
                },
                "speed": 65.5,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.client.client.publish(
                topic="vehicle/alerts/drowsiness",
                payload=json.dumps(alert),
                qos=1
            )
            print("Drowsiness alert sent successfully!")

        except Exception as e:
            self.fail(f"Error sending drowsiness alert: {str(e)}")
        
        finally:
            # Disconnect from AWS IoT Core
            print("\nDisconnecting from AWS IoT Core...")
            self.client.disconnect()

    def test_message_qos(self):
        """Test message QoS levels"""
        try:
            # Connect to AWS IoT Core
            print("Connecting to AWS IoT Core...")
            self.client.connect()
            time.sleep(2)

            # Test different QoS levels
            test_message = {
                "test": "message",
                "timestamp": datetime.utcnow().isoformat()
            }

            # QoS 0 - At most once
            self.client.client.publish(
                topic="test/qos0",
                payload=json.dumps(test_message),
                qos=0
            )
            print("QoS 0 message sent")

            # QoS 1 - At least once
            self.client.client.publish(
                topic="test/qos1",
                payload=json.dumps(test_message),
                qos=1
            )
            print("QoS 1 message sent")

            # QoS 2 - Exactly once
            self.client.client.publish(
                topic="test/qos2",
                payload=json.dumps(test_message),
                qos=2
            )
            print("QoS 2 message sent")

        except Exception as e:
            self.fail(f"Error testing message QoS: {str(e)}")
        
        finally:
            # Disconnect from AWS IoT Core
            print("\nDisconnecting from AWS IoT Core...")
            self.client.disconnect()

if __name__ == "__main__":
    unittest.main() 