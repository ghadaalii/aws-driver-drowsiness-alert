"""
Configuration settings for the Driver Drowsiness Alert System
Optimized for AWS Free Tier usage
"""

import os
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_env_var(name: str, default: Any = None) -> str:
    """Get environment variable with validation"""
    value = os.environ.get(name, default)
    if value is None:
        raise ValueError(f"Environment variable {name} is not set")
    return value

# AWS IoT Core Configuration (Free Tier: 250,000 messages/month)
IOT_ENDPOINT = "a33zskt3eonsh8-ats.iot.us-east-1.amazonaws.com"
IOT_PORT = 8883
IOT_CLIENT_ID = get_env_var('IOT_CLIENT_ID', 'raspberry-pi-client')

# Certificate paths
CERT_PATH = "certificates/device.pem.crt"
KEY_PATH = "certificates/private.pem.key"
ROOT_CA_PATH = "certificates/AmazonRootCA1.pem"

# MQTT Topics
TOPIC_DROWSINESS = "vehicle/alerts/drowsiness"
TOPIC_DRIVER_PROFILE = "vehicle/driver/profile"
TOPIC_AMBULANCE = "ambulance/alerts/drowsiness"

# DynamoDB Tables (Free Tier: 25 WCU and 25 RCU)
DRIVERS_TABLE = "drivers-free-tier"
ALERTS_TABLE = "drowsiness_alerts-free-tier"

# S3 Bucket (Free Tier: 5GB storage)
CSV_IMPORT_BUCKET = "drowsiness-alert-csv-imports-free-tier"

# Environment
ENVIRONMENT = get_env_var('ENVIRONMENT', 'dev')  # Options: dev, staging, prod

# Free Tier Limits
FREE_TIER_LIMITS: Dict[str, int] = {
    'iot_messages_per_month': 250000,
    'dynamodb_wcu': 25,
    'dynamodb_rcu': 25,
    's3_storage_gb': 5,
    'lambda_invocations': 1000000,
    'lambda_compute_seconds': 400000
}

# Example JSON payload for driver profile (optimized for free tier)
DRIVER_PROFILE_EXAMPLE = {
    "driver_id": "DRIVER123456",
    "timestamp": "2025-05-05T08:30:00Z",
    "name": "John Doe",
    "age": 35,
    "phone": "+1234567890",
    "emergency_contact": "+0987654321",
    "medical_info": {
        "blood_type": "O+",
        "allergies": ["penicillin"],
        "conditions": ["hypertension"],
        "medications": ["lisinopril"]
    },
    "car_info": {
        "license_plate": "ABC123",
        "make": "Toyota",
        "model": "Camry",
        "color": "Blue",
        "year": 2023
    }
}

# Example JSON payload for drowsiness alert (optimized for free tier)
DROWSINESS_ALERT_EXAMPLE = {
    "alert_id": "ALERT123456",
    "driver_id": "DRIVER123456",
    "timestamp": "2025-05-05T08:45:23Z",
    "drowsiness_level": 0.85,  # 0-1 scale with 1 being most severe
    "confidence": 0.92,        # Model confidence 
    "location": {
        "latitude": 37.7749,
        "longitude": -122.4194
    },
    "speed": 65.5             # Speed in km/h
}

def validate_config() -> None:
    """Validate the configuration settings"""
    try:
        # Check required environment variables
        get_env_var('IOT_CLIENT_ID')
        
        # Validate environment
        if ENVIRONMENT not in ['dev', 'staging', 'prod']:
            raise ValueError(f"Invalid environment: {ENVIRONMENT}")
        
        logger.info("Configuration validated successfully")
    except Exception as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise

# Validate configuration on import
validate_config() 