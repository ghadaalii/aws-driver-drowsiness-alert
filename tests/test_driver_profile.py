"""
Test script to verify driver profile flow through IoT Core
"""

import json
import time
import unittest
from src.client.mqtt_client import DrowsinessAlertClient
import boto3
from datetime import datetime
import os

class TestDriverProfile(unittest.TestCase):
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

    def test_driver_profile_flow(self):
        """Test sending and verifying driver profile"""
        try:
            # 1. Connect to AWS IoT Core
            print("Connecting to AWS IoT Core...")
            self.client.connect()
            time.sleep(2)  # Wait for connection

            # 2. Create test driver profile
            print("\nPreparing test driver profile...")
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
            
            # 3. Send driver profile
            print("Sending driver profile to IoT Core...")
            self.client.client.publish(
                topic="vehicle/driver/profile",
                payload=json.dumps(driver_profile),
                qos=1
            )
            print("Driver profile sent!")

            # 4. Wait for Lambda to process
            print("\nWaiting for profile processing...")
            time.sleep(5)

            # 5. Verify driver profile in DynamoDB
            print("Verifying driver profile in DynamoDB...")
            response = self.drivers_table.get_item(
                Key={'id': 'TEST123'}
            )
            
            # Check if profile exists
            self.assertIn('Item', response, "Driver profile not found in DynamoDB")
            item = response['Item']
            
            # Verify all fields
            print("\nVerifying profile fields...")
            self.assertEqual(item['id'], driver_profile['id'], "ID mismatch")
            self.assertEqual(item['name'], driver_profile['name'], "Name mismatch")
            self.assertEqual(item['gender'], driver_profile['gender'], "Gender mismatch")
            self.assertEqual(item['date_of_birth'], driver_profile['date_of_birth'], "DOB mismatch")
            self.assertEqual(item['weight'], driver_profile['weight'], "Weight mismatch")
            self.assertEqual(item['height'], driver_profile['height'], "Height mismatch")
            self.assertEqual(item['emergency_contact'], driver_profile['emergency_contact'], "Emergency contact mismatch")
            self.assertEqual(item['blood_type'], driver_profile['blood_type'], "Blood type mismatch")
            self.assertEqual(item['chronic_diseases'], driver_profile['chronic_diseases'], "Chronic diseases mismatch")
            self.assertEqual(item['allergies'], driver_profile['allergies'], "Allergies mismatch")
            
            print("\nAll profile fields verified successfully!")

        except Exception as e:
            self.fail(f"Error during driver profile test: {str(e)}")
        
        finally:
            # Clean up
            print("\nCleaning up...")
            try:
                # Delete test data from DynamoDB
                self.drivers_table.delete_item(
                    Key={'id': 'TEST123'}
                )
                print("Test data cleaned up!")
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")
            
            # Disconnect from AWS IoT Core
            print("\nDisconnecting from AWS IoT Core...")
            self.client.disconnect()

if __name__ == "__main__":
    unittest.main() 