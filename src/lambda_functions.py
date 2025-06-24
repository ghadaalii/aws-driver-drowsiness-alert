"""
Consolidated Lambda functions for the Driver Drowsiness Alert System
Optimized for AWS Free Tier usage with comprehensive error handling and monitoring
"""

import json
import boto3
import uuid
from datetime import datetime, timedelta
import os
import logging
import csv
import io
import decimal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
iot_client = boto3.client('iot-data')

# Get table names from environment variables
DRIVERS_TABLE = os.environ.get('DRIVERS_TABLE', 'drivers-free-tier')
ALERTS_TABLE = os.environ.get('ALERTS_TABLE', 'drowsiness_alerts-free-tier')

# Free Tier limits for monitoring
FREE_TIER_LIMITS = {
    'iot_messages_per_month': 250000,
    'dynamodb_wcu': 25,
    'dynamodb_rcu': 25,
    'lambda_invocations': 1000000,
    'lambda_compute_seconds': 400000
}

def map_json_to_database(json_data):
    """
    Map JSON data to match database columns
    
    Args:
        json_data (dict): The JSON data to map
        
    Returns:
        dict: Mapped data ready for database insertion
    """
    try:
        # Extract and map the data
        mapped_data = {
            'id': json_data.get('id'),
            'name': json_data.get('name'),
            'gender': json_data.get('gender'),
            'date_of_birth': json_data.get('date_of_birth'),
            'weight': float(json_data.get('weight', 0)),
            'height': float(json_data.get('height', 0)),
            'emergency_contact': json_data.get('emergency_contact'),
            'blood_type': json_data.get('blood_type'),
            'chronic_diseases': json_data.get('chronic_diseases', []),
            'allergies': json_data.get('allergies', []),
            'last_updated': datetime.utcnow().isoformat(),
            'ttl': int((datetime.utcnow() + timedelta(days=365)).timestamp())
        }
        
        # Validate required fields
        required_fields = ['id', 'name', 'gender', 'date_of_birth', 'weight', 'height', 'emergency_contact', 'blood_type']
        missing_fields = [field for field in required_fields if not mapped_data.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        return mapped_data
        
    except Exception as e:
        logger.error(f"Error mapping JSON data: {str(e)}")
        raise

def process_json_file(json_file_content):
    """
    Process JSON file content and store in database
    
    Args:
        json_file_content (str): The content of the JSON file
        
    Returns:
        dict: Processing results
    """
    try:
        # Parse JSON content
        data = json.loads(json_file_content)
        
        # Map data to database format
        mapped_data = map_json_to_database(data)
        
        # Store in DynamoDB
        drivers_table = dynamodb.Table(DRIVERS_TABLE)
        drivers_table.put_item(Item=mapped_data)
        
        # Publish to IoT Core
        iot_client.publish(
            topic='vehicle/driver/profile',
            qos=1,
            payload=json.dumps(mapped_data)
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data processed successfully',
                'id': mapped_data['id']
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid JSON format'
            })
        }
    except ValueError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': str(e)
            })
        }
    except Exception as e:
        logger.error(f"Error processing JSON file: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error processing file: {str(e)}'
            })
        }

def http_update_profile_handler(event, context):
    """
    Lambda function to handle HTTP requests for driver profile updates.
    This function:
    1. Receives HTTP POST requests from the infotainment system
    2. Validates the incoming data
    3. Updates the driver profile in DynamoDB
    4. Publishes to IoT Core for real-time updates
    
    Args:
        event (dict): The event data from API Gateway
        context (LambdaContext): The Lambda context object
    
    Returns:
        dict: Response containing status code and message
    """
    logger.info(f"Received HTTP request: {json.dumps(event)}")
    
    try:
        # Parse request body
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Request body is missing'
                })
            }
        
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Invalid JSON in request body'
                })
            }
        
        # Process the JSON data
        return process_json_file(json.dumps(body))
        
    except Exception as e:
        logger.error(f"Error processing HTTP request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Error updating profile: {str(e)}'
            })
        }

def update_profile_handler(event, context):
    """
    Lambda function to handle driver profile updates.
    When a driver updates their profile via the infotainment system,
    this function updates the record in DynamoDB.
    
    Args:
        event (dict): The event data containing profile updates
        context (LambdaContext): The Lambda context object
    
    Returns:
        dict: Response containing status code and message
    """
    logger.info(f"Received driver profile update: {json.dumps(event)}")
    
    drivers_table = dynamodb.Table(DRIVERS_TABLE)
    
    try:
        driver_id = event.get('driver_id')
        if not driver_id:
            raise ValueError("Update missing driver_id")
        
        ttl = int((datetime.utcnow() + timedelta(days=365)).timestamp())
        
        update_data = {
            'driver_id': driver_id,
            'name': event.get('name'),
            'age': event.get('age'),
            'medical_info': event.get('medical_info', {}),
            'car_info': event.get('car_info', {}),
            'last_updated': datetime.utcnow().isoformat(),
            'ttl': ttl
        }
        
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        drivers_table.put_item(Item=update_data)
        
        logger.info(f"Successfully updated driver profile for {driver_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Driver profile updated successfully',
                'driver_id': driver_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error updating driver profile: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error updating profile: {str(e)}'
            })
        }

def process_alert_handler(event, context):
    """
    Lambda function triggered by AWS IoT Core when a drowsiness alert is received.
    This function:
    1. Receives the alert from the vehicle
    2. Retrieves the driver's information from DynamoDB
    3. Combines the data
    4. Stores the alert in DynamoDB
    5. Publishes the combined data to the ambulance dashboard
    6. Sends acknowledgment back to the vehicle
    
    Args:
        event (dict): The event data from IoT Core
        context (LambdaContext): The Lambda context object
    
    Returns:
        dict: Response containing status code and message
    """
    logger.info(f"Received drowsiness alert: {json.dumps(event)}")
    
    drivers_table = dynamodb.Table(DRIVERS_TABLE)
    alerts_table = dynamodb.Table(ALERTS_TABLE)
    
    try:
        # Extract alert data from event
        alert_id = event.get('alert_id', str(uuid.uuid4()))
        driver_id = event.get('driver_id')
        timestamp = event.get('timestamp', datetime.utcnow().isoformat())
        location = event.get('location', {})
        message = event.get('message', 'Driver drowsiness detected')
        
        if not driver_id:
            raise ValueError("Alert missing driver_id")
        
        ttl = int((datetime.utcnow() + timedelta(days=30)).timestamp())
        
        # Get driver information from database
        driver_response = drivers_table.get_item(
            Key={'id': driver_id}  # Note: using 'id' as primary key for drivers table
        )
        
        if 'Item' not in driver_response:
            logger.warning(f"Driver with ID {driver_id} not found in database")
            driver_info = {
                'id': driver_id,
                'name': 'Unknown Driver',
                'emergency_contact': 'Unknown',
                'blood_type': 'Unknown'
            }
        else:
            driver_info = driver_response['Item']
        
        # Create alert record matching CloudFormation table structure
        alert_record = {
            'alert_id': alert_id,
            'driver_id': driver_id,
            'timestamp': timestamp,
            'location': location,
            'message': message,
            'processed': True,
            'ttl': ttl
        }
        
        # Store alert in DynamoDB
        alerts_table.put_item(Item=alert_record)
        logger.info(f"Alert stored in database: {alert_id}")
        
        # Create complete alert for ambulance dashboard
        complete_alert = {
            'alert': alert_record,
            'driver_info': driver_info
        }
        
        # Helper for Decimal serialization
        def decimal_default(obj):
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            raise TypeError
        
        # Publish to ambulance dashboard
        iot_client.publish(
            topic='ambulance/alerts/drowsiness',
            qos=1,
            payload=json.dumps(complete_alert, default=decimal_default)
        )
        logger.info(f"Published alert to ambulance dashboard: {alert_id}")
        
        # Send acknowledgment back to vehicle
        acknowledgment = {
            'alert_id': alert_id,
            'status': 'processed',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Alert received and processed successfully'
        }
        
        iot_client.publish(
            topic='vehicle/alerts/ack',
            qos=1,
            payload=json.dumps(acknowledgment)
        )
        logger.info(f"Sent acknowledgment to vehicle: {alert_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Alert processed successfully',
                'alert_id': alert_id,
                'driver_found': 'Item' in driver_response
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing drowsiness alert: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error processing alert: {str(e)}'
            })
        } 