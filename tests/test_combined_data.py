#!/usr/bin/env python3
"""
Test script to show the combined data structure sent to ambulance dashboard
This simulates what the Lambda function sends to the API Gateway endpoint
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal

def create_combined_alert_data():
    """
    Create example combined alert data that gets sent to ambulance dashboard
    This is the exact structure that the Lambda function sends
    """
    
    # Example alert data (what gets stored in DynamoDB)
    alert_record = {
        'alert_id': 'cacae107-7aaf-83bd-1b2a-e01e5b4bbd7d',
        'driver_id': 'fac15154-8712-af70-5b23-f3fd61e3db89',
        'timestamp': '2025-06-23T22:31:12Z',
        'location': {
            'latitude': Decimal('30.0444'),
            'longitude': Decimal('31.2357'),
            'description': 'Cairo, Egypt'
        },
        'message': 'Driver fell asleep',
        'processed': True,
        'ttl': int((datetime.utcnow() + timedelta(days=30)).timestamp())
    }
    
    # Example driver info (retrieved from DynamoDB)
    driver_info = {
        'id': 'fac15154-8712-af70-5b23-f3fd61e3db89',
        'name': 'Anna',
        'gender': 'Female',
        'date_of_birth': '30-01-2000',
        'weight': Decimal('52'),
        'height': Decimal('157'),
        'blood_type': 'AB+',
        'emergency_contact': '01233445577',
        'chronic_diseases': ['Asthma'],
        'allergies': ['no'],
        'last_updated': '2025-06-23T22:31:10.056404',
        'ttl': int((datetime.utcnow() + timedelta(days=365)).timestamp())
    }
    
    # Combined data structure (what gets sent to ambulance dashboard)
    complete_alert = {
        'alert': alert_record,
        'driver_info': driver_info,
        'processed_at': datetime.utcnow().isoformat()
    }
    
    return complete_alert

def decimal_default(obj):
    """Helper function to handle Decimal serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def show_combined_data():
    """Display the combined data structure"""
    
    print("=" * 80)
    print("🚨 COMBINED DATA SENT TO AMBULANCE DASHBOARD")
    print("=" * 80)
    
    # Create the combined data
    combined_data = create_combined_alert_data()
    
    # Convert to JSON (handling Decimal objects)
    json_data = json.dumps(combined_data, default=decimal_default, indent=2)
    
    print("\n📋 JSON Structure:")
    print("-" * 40)
    print(json_data)
    
    print("\n" + "=" * 80)
    print("📊 DATA BREAKDOWN")
    print("=" * 80)
    
    # Show alert section
    print("\n🚨 ALERT INFORMATION:")
    print("-" * 30)
    alert = combined_data['alert']
    print(f"Alert ID: {alert['alert_id']}")
    print(f"Driver ID: {alert['driver_id']}")
    print(f"Timestamp: {alert['timestamp']}")
    print(f"Location: {alert['location']['latitude']}, {alert['location']['longitude']}")
    print(f"Description: {alert['location']['description']}")
    print(f"Message: {alert['message']}")
    print(f"Processed: {alert['processed']}")
    
    # Show driver section
    print("\n👤 DRIVER INFORMATION:")
    print("-" * 30)
    driver = combined_data['driver_info']
    print(f"Name: {driver['name']}")
    print(f"Gender: {driver['gender']}")
    print(f"Date of Birth: {driver['date_of_birth']}")
    print(f"Weight: {driver['weight']} kg")
    print(f"Height: {driver['height']} cm")
    print(f"Blood Type: {driver['blood_type']}")
    print(f"Emergency Contact: {driver['emergency_contact']}")
    print(f"Chronic Diseases: {', '.join(driver['chronic_diseases'])}")
    print(f"Allergies: {', '.join(driver['allergies'])}")
    
    print("\n⏰ PROCESSING INFO:")
    print("-" * 30)
    print(f"Processed At: {combined_data['processed_at']}")
    
    print("\n" + "=" * 80)
    print("🌐 HTTP REQUEST DETAILS")
    print("=" * 80)
    
    print(f"\nURL: https://jnptb8kop7.execute-api.us-east-1.amazonaws.com/dev/ambulance-alert")
    print(f"Method: POST")
    print(f"Content-Type: application/json")
    print(f"Data Size: {len(json_data)} characters")
    
    print("\n" + "=" * 80)
    print("✅ READY TO SEND TO AMBULANCE DASHBOARD")
    print("=" * 80)

def test_http_request():
    """Simulate the HTTP request that would be sent"""
    
    print("\n🔧 SIMULATING HTTP REQUEST")
    print("-" * 40)
    
    import urllib.request
    import urllib.error
    
    combined_data = create_combined_alert_data()
    json_data = json.dumps(combined_data, default=decimal_default).encode('utf-8')
    
    url = "https://jnptb8kop7.execute-api.us-east-1.amazonaws.com/dev/ambulance-alert"
    
    try:
        req = urllib.request.Request(
            url,
            data=json_data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'DrowsinessAlertSystem/1.0'
            }
        )
        
        print(f"✅ Request prepared successfully")
        print(f"📤 Data size: {len(json_data)} bytes")
        print(f"🌐 URL: {url}")
        print(f"📋 Headers: {dict(req.headers)}")
        
        # Uncomment the next lines to actually send the request
        # with urllib.request.urlopen(req, timeout=10) as response:
        #     response_data = response.read().decode('utf-8')
        #     print(f"📥 Response Status: {response.getcode()}")
        #     print(f"📥 Response: {response_data}")
        
    except Exception as e:
        print(f"❌ Error preparing request: {str(e)}")

if __name__ == "__main__":
    show_combined_data()
    test_http_request() 