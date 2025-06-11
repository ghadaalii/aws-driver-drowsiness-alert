"""
Test script to verify data flow from MQTT to DynamoDB
"""

import json
import time
import unittest
from src.client.mqtt_client import DrowsinessAlertClient
import boto3
from datetime import datetime
import os

class TestDataFlow(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.environment = os.environ.get('ENVIRONMENT', 'dev')
        
        # Initialize MQTT client
        self.client = DrowsinessAlertClient(
            client_id="test-client-1",
            endpoint="a33zskt3eonsh8-ats.iot.us-east-1.amazonaws.com",
            cert_path="certificates/device.pem.crt",
            key_path="certificates/private.pem.key",
            ca_path="certificates/AmazonRootCA1.pem"
        )

        # Initialize DynamoDB client
        self.dynamodb = boto3.resource('dynamodb')
        self.drivers_table = self.dynamodb.Table(f'drivers-{self.environment}')
        self.alerts_table = self.dynamodb.Table(f'drowsiness_alerts-{self.environment}')

    def test_driver_profile_flow(self):
        """Test the flow of driver profile data from MQTT to DynamoDB"""
        try:
            # Connect to AWS IoT Core
            print("Connecting to AWS IoT Core...")
            self.client.connect()
            time.sleep(2)  # Wait for connection

            # Test 1: Send driver profile
            print("\nSending driver profile...")
            driver_profile = {
                "id": "TEST123",
                "name": "Test Driver",
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
            print("Driver profile sent!")

            # Wait for Lambda to process
            time.sleep(5)

            # Verify driver profile in DynamoDB
            response = self.drivers_table.get_item(
                Key={'id': 'TEST123'}
            )
            self.assertIn('Item', response)
            item = response['Item']
            self.assertEqual(item['id'], driver_profile['id'])
            self.assertEqual(item['name'], driver_profile['name'])
            self.assertEqual(item['blood_type'], driver_profile['blood_type'])

        except Exception as e:
            self.fail(f"Error during driver profile flow test: {str(e)}")
        
        finally:
            # Disconnect from AWS IoT Core
            print("\nDisconnecting from AWS IoT Core...")
            self.client.disconnect()

    def test_drowsiness_alert_flow(self):
        """Test the flow of drowsiness alert data from MQTT to DynamoDB"""
        try:
            # Connect to AWS IoT Core
            print("Connecting to AWS IoT Core...")
            self.client.connect()
            time.sleep(2)  # Wait for connection

            # Test 2: Send drowsiness alert
            print("\nSending drowsiness alert...")
            alert = {
                "driver_id": "TEST123",
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
            print("Drowsiness alert sent!")

            # Wait for Lambda to process
            time.sleep(5)

            # Verify alert in DynamoDB
            response = self.alerts_table.scan(
                FilterExpression='driver_id = :driver_id',
                ExpressionAttributeValues={
                    ':driver_id': 'TEST123'
                }
            )
            self.assertTrue(response['Items'])
            item = response['Items'][0]
            self.assertEqual(item['driver_id'], alert['driver_id'])
            self.assertEqual(item['drowsiness_level'], alert['drowsiness_level'])
            self.assertEqual(item['confidence'], alert['confidence'])

        except Exception as e:
            self.fail(f"Error during drowsiness alert flow test: {str(e)}")
        
        finally:
            # Disconnect from AWS IoT Core
            print("\nDisconnecting from AWS IoT Core...")
            self.client.disconnect()

if __name__ == "__main__":
    unittest.main() 