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
        driver_id = event.get('driver_id')
        if not driver_id:
            raise ValueError("Alert missing driver_id")
        
        alert_id = str(uuid.uuid4())
        timestamp = event.get('timestamp', datetime.utcnow().isoformat())
        ttl = int((datetime.utcnow() + timedelta(days=30)).timestamp())
        
        driver_response = drivers_table.get_item(
            Key={'driver_id': driver_id}
        )
        
        if 'Item' not in driver_response:
            logger.warning(f"Driver with ID {driver_id} not found in database")
            driver_info = {
                'driver_id': driver_id,
                'name': 'Unknown Driver',
                'car_info': {'vehicle': 'Unknown Vehicle'}
            }
        else:
            driver_info = driver_response['Item']
        
        alert_record = {
            'alert_id': alert_id,
            'driver_id': driver_id,
            'timestamp': timestamp,
            'drowsiness_level': event.get('drowsiness_level', 'unknown'),
            'confidence': event.get('confidence', 0),
            'location': event.get('location', {}),
            'speed': event.get('speed', 0),
            'processed': True,
            'ttl': ttl
        }
        
        alerts_table.put_item(Item=alert_record)
        
        complete_alert = {
            'alert': alert_record,
            'driver_info': driver_info
        }
        
        iot_client.publish(
            topic='ambulance/alerts/drowsiness',
            qos=1,
            payload=json.dumps(complete_alert)
        )
        
        logger.info(f"Published alert to ambulance dashboard: {json.dumps(complete_alert)}")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Alert processed successfully',
                'alert_id': alert_id
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