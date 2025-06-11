"""
Test suite for DynamoDB database operations and functionality
"""

import unittest
import boto3
from moto import mock_dynamodb2
from datetime import datetime, timedelta
import json
import uuid
import os

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.mock_dynamodb = mock_dynamodb2()
        self.mock_dynamodb.start()
        
        # Initialize DynamoDB client
        self.dynamodb = boto3.resource('dynamodb')
        
        # Get environment
        self.environment = os.environ.get('ENVIRONMENT', 'dev')
        
        # Create test tables
        self.create_test_tables()
        
        # Initialize test data
        self.test_driver = {
            'id': 'DRIVER123',
            'name': 'John Doe',
            'gender': 'male',
            'date_of_birth': '1990-01-01',
            'weight': 75.5,
            'height': 180.0,
            'emergency_contact': '+1234567890',
            'blood_type': 'A+',
            'chronic_diseases': ['Hypertension'],
            'allergies': ['Penicillin'],
            'last_updated': datetime.utcnow().isoformat(),
            'ttl': int((datetime.utcnow() + timedelta(days=365)).timestamp())
        }
        
        self.test_alert = {
            'alert_id': str(uuid.uuid4()),
            'driver_id': 'DRIVER123',
            'timestamp': datetime.utcnow().isoformat(),
            'drowsiness_level': 0.85,
            'confidence': 0.92,
            'location': {
                'latitude': 37.7749,
                'longitude': -122.4194
            },
            'speed': 65.5,
            'processed': False,
            'ttl': int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }

    def tearDown(self):
        """Clean up test environment"""
        self.mock_dynamodb.stop()

    def create_test_tables(self):
        """Create test DynamoDB tables"""
        # Create Drivers table
        self.drivers_table = self.dynamodb.create_table(
            TableName=f'drivers-{self.environment}',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST',
            SSESpecification={
                'SSEEnabled': True
            },
            PointInTimeRecoverySpecification={
                'PointInTimeRecoveryEnabled': True
            },
            TimeToLiveSpecification={
                'AttributeName': 'ttl',
                'Enabled': True
            }
        )
        
        # Create Alerts table
        self.alerts_table = self.dynamodb.create_table(
            TableName=f'drowsiness_alerts-{self.environment}',
            KeySchema=[
                {'AttributeName': 'alert_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'alert_id', 'AttributeType': 'S'},
                {'AttributeName': 'driver_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'driver_id-timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'driver_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            SSESpecification={
                'SSEEnabled': True
            },
            PointInTimeRecoverySpecification={
                'PointInTimeRecoveryEnabled': True
            },
            TimeToLiveSpecification={
                'AttributeName': 'ttl',
                'Enabled': True
            }
        )

    def test_create_driver_profile(self):
        """Test creating a driver profile"""
        # Put item in DynamoDB
        self.drivers_table.put_item(Item=self.test_driver)
        
        # Get item from DynamoDB
        response = self.drivers_table.get_item(
            Key={'id': self.test_driver['id']}
        )
        
        # Verify the item
        self.assertIn('Item', response)
        item = response['Item']
        self.assertEqual(item['id'], self.test_driver['id'])
        self.assertEqual(item['name'], self.test_driver['name'])
        self.assertEqual(item['blood_type'], self.test_driver['blood_type'])
        self.assertEqual(item['chronic_diseases'], self.test_driver['chronic_diseases'])

    def test_update_driver_profile(self):
        """Test updating a driver profile"""
        # First create the profile
        self.drivers_table.put_item(Item=self.test_driver)
        
        # Update the profile
        updated_data = {
            'id': self.test_driver['id'],
            'weight': 80.0,
            'height': 182.0,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        self.drivers_table.update_item(
            Key={'id': self.test_driver['id']},
            UpdateExpression='SET weight = :w, height = :h, last_updated = :t',
            ExpressionAttributeValues={
                ':w': updated_data['weight'],
                ':h': updated_data['height'],
                ':t': updated_data['last_updated']
            }
        )
        
        # Get updated item
        response = self.drivers_table.get_item(
            Key={'id': self.test_driver['id']}
        )
        
        # Verify updates
        self.assertEqual(response['Item']['weight'], updated_data['weight'])
        self.assertEqual(response['Item']['height'], updated_data['height'])
        self.assertEqual(response['Item']['last_updated'], updated_data['last_updated'])

    def test_create_drowsiness_alert(self):
        """Test creating a drowsiness alert"""
        # Put item in DynamoDB
        self.alerts_table.put_item(Item=self.test_alert)
        
        # Get item from DynamoDB
        response = self.alerts_table.get_item(
            Key={'alert_id': self.test_alert['alert_id']}
        )
        
        # Verify the item
        self.assertIn('Item', response)
        item = response['Item']
        self.assertEqual(item['alert_id'], self.test_alert['alert_id'])
        self.assertEqual(item['driver_id'], self.test_alert['driver_id'])
        self.assertEqual(item['drowsiness_level'], self.test_alert['drowsiness_level'])
        self.assertEqual(item['confidence'], self.test_alert['confidence'])

    def test_query_alerts_by_driver(self):
        """Test querying alerts by driver ID"""
        # Create multiple alerts for the same driver
        alerts = []
        for i in range(3):
            alert = self.test_alert.copy()
            alert['alert_id'] = str(uuid.uuid4())
            alert['timestamp'] = (datetime.utcnow() + timedelta(minutes=i)).isoformat()
            self.alerts_table.put_item(Item=alert)
            alerts.append(alert)
        
        # Query alerts by driver ID
        response = self.alerts_table.query(
            IndexName='driver_id-timestamp-index',
            KeyConditionExpression='driver_id = :did',
            ExpressionAttributeValues={
                ':did': self.test_alert['driver_id']
            }
        )
        
        # Verify results
        self.assertEqual(len(response['Items']), 3)
        for item in response['Items']:
            self.assertEqual(item['driver_id'], self.test_alert['driver_id'])

    def test_ttl_functionality(self):
        """Test TTL functionality"""
        # Create an alert with short TTL
        alert = self.test_alert.copy()
        alert['alert_id'] = str(uuid.uuid4())
        alert['ttl'] = int((datetime.utcnow() + timedelta(seconds=1)).timestamp())
        self.alerts_table.put_item(Item=alert)
        
        # Wait for TTL to expire
        import time
        time.sleep(2)
        
        # Try to get the item
        response = self.alerts_table.get_item(
            Key={'alert_id': alert['alert_id']}
        )
        
        # Verify item is deleted
        self.assertNotIn('Item', response)

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Test invalid driver ID
        with self.assertRaises(Exception):
            self.drivers_table.get_item(
                Key={'id': 'NONEXISTENT'}
            )
        
        # Test invalid alert ID
        with self.assertRaises(Exception):
            self.alerts_table.get_item(
                Key={'alert_id': 'NONEXISTENT'}
            )
        
        # Test invalid query
        with self.assertRaises(Exception):
            self.alerts_table.query(
                IndexName='driver_id-timestamp-index',
                KeyConditionExpression='invalid_field = :val',
                ExpressionAttributeValues={
                    ':val': 'test'
                }
            )

if __name__ == '__main__':
    unittest.main() 