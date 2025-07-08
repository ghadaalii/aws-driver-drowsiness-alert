#!/usr/bin/env python3
"""
Simple Test: Send Data to Dashboard
This script sends alerts to trigger Lambda function
Lambda will combine alert + driver data and send to dashboard
"""

import boto3
import json
import uuid
from datetime import datetime

# AWS Configuration
iot_client = boto3.client('iot-data', region_name='us-east-1')

def send_alert_to_dashboard(driver_id, driver_name):
    """Send alert that will trigger Lambda to send combined data to dashboard"""
    
    alert_id = f"TEST-{str(uuid.uuid4())[:8]}"
    
    alert_data = {
        "alert_id": alert_id,
        "driver_id": driver_id,
        "timestamp": datetime.utcnow().isoformat(),
        "location": {
            "latitude": 30.0444,
            "longitude": 31.2357,
            "description": f"Test location for {driver_name}"
        },
        "message": f"Test drowsiness alert for {driver_name}"
    }
    
    print(f"📤 Sending alert for {driver_name}...")
    print(f"   Alert ID: {alert_id}")
    print(f"   Driver ID: {driver_id}")
    
    # Send via MQTT to trigger Lambda
    iot_client.publish(
        topic='vehicle/alerts/drowsiness',
        qos=1,
        payload=json.dumps(alert_data)
    )
    
    print(f"✅ Alert sent! Lambda will:")
    print(f"   1. Search driver {driver_id} in database")
    print(f"   2. Combine alert + driver data")
    print(f"   3. Send to dashboard via WebSocket")
    
    return alert_id

def main():
    print("🚑 Send Data to Dashboard")
    print("=" * 40)
    
    # Real driver IDs from your database
    drivers = [
        {"id": "32471704-8347-e071-d067-3233ed6cf3cc", "name": "Mariam"},
        {"id": "3b7c6d2d-3b99-4e3f-0b83-bd7d9c1e7cab", "name": "sasa"},
        {"id": "8d0e7b9a-d139-6fa0-b503-653f32eff968", "name": "Max"},
        {"id": "DRIVER123", "name": "John Doe"},
        {"id": "fac15154-8712-af70-5b23-f3fd61e3db89", "name": "Anna"}
    ]
    
    print("Available drivers:")
    for i, driver in enumerate(drivers, 1):
        print(f"   {i}. {driver['name']} (ID: {driver['id']})")
    
    try:
        choice = int(input("\nEnter driver number (1-5): ")) - 1
        if 0 <= choice < len(drivers):
            driver = drivers[choice]
            alert_id = send_alert_to_dashboard(driver['id'], driver['name'])
            
            if alert_id:
                print(f"\n✅ SUCCESS!")
                print(f"📋 Alert ID: {alert_id}")
                print(f"👤 Driver: {driver['name']}")
                print(f"🔗 Dashboard should receive combined data via WebSocket")
                print(f"💡 Check dashboard for real-time update!")
        else:
            print("❌ Invalid choice")
    except:
        print("❌ Invalid input")

if __name__ == "__main__":
    main() 