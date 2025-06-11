# Driver Drowsiness Alert System

A real-time system for detecting driver drowsiness and alerting emergency services using AWS IoT Core. The system is optimized for AWS Free Tier usage and includes comprehensive monitoring and cost optimization features.

## Project Overview

This system monitors driver drowsiness in real-time and automatically alerts emergency services when necessary. It uses a Raspberry Pi for data collection and AWS services for processing and storage.

### Key Features

- Real-time drowsiness detection and alerting
- Driver profile management
- Emergency service integration
- AWS IoT Core integration
- DynamoDB for data storage
- Free Tier optimization
- Usage monitoring and alerts

## System Architecture

### Components

1. **Data Collection (Raspberry Pi)**
   - Drowsiness detection model
   - Camera module
   - MQTT client for data transmission

2. **AWS Services**
   - IoT Core: Message broker and device management
   - Lambda: Serverless functions for data processing
   - DynamoDB: NoSQL database for data storage
   - CloudWatch: Monitoring and logging

3. **Database Structure**
   - `drivers-dev` Table:
     - Primary Key: `id` (String)
     - Columns: name, gender, date_of_birth, weight, height, emergency_contact, blood_type, chronic_diseases, allergies, last_updated, ttl
   
   - `drowsiness_alerts-dev` Table:
     - Primary Key: `alert_id` (String)
     - Secondary Index: `driver_id-timestamp-index`
     - Columns: driver_id, timestamp, drowsiness_level, confidence, location, speed, processed, ttl

## Data Flow

1. **Driver Profile Flow**
   ```
   Raspberry Pi → MQTT → IoT Core → Lambda → DynamoDB
   ```
   - Driver profile is sent via MQTT
   - IoT Core receives the message
   - Lambda function processes and validates data
   - Data is stored in DynamoDB

2. **Drowsiness Alert Flow**
   ```
   Raspberry Pi → MQTT → IoT Core → Lambda → DynamoDB → Emergency Services
   ```
   - Drowsiness detection triggers alert
   - Alert is sent via MQTT
   - IoT Core receives the alert
   - Lambda function:
     - Retrieves driver information
     - Processes alert data
     - Stores in DynamoDB
     - Notifies emergency services

3. **Emergency Response Flow**
   ```
   DynamoDB → Lambda → IoT Core → Emergency Dashboard
   ```
   - Emergency services receive alert
   - Access driver information
   - View real-time location
   - Coordinate response

## Project Structure

```
FProject/
├── README.md
├── requirements.txt
├── cloudformation.yaml
├── main.py
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration and environment variables
│   ├── lambda_functions.py    # AWS Lambda functions
│   └── client/
│       ├── __init__.py
│       └── mqtt_client.py     # MQTT client for IoT Core
├── tests/
│   ├── test_driver_profile.py    # Driver profile flow tests
│   ├── test_mqtt_messages.py     # MQTT message tests
│   ├── test_data_flow.py         # Data flow tests
│   └── test_database.py          # DynamoDB tests
├── certificates/              # AWS IoT Core certificates
│   ├── device.pem.crt
│   ├── private.pem.key
│   ├── public.pem.key
│   └── AmazonRootCA1.pem
└── scripts/
    └── create_certificates.sh  # Certificate creation script
```

## Components

1. **Core Application**
   - `main.py`: Main application entry point
   - `src/config.py`: Configuration management
   - `src/lambda_functions.py`: AWS Lambda functions
   - `src/client/mqtt_client.py`: MQTT client for IoT Core

2. **Testing**
   - Test suite for driver profiles
   - Test suite for MQTT messages
   - Test suite for data flow
   - Test suite for database operations

3. **Infrastructure**
   - `cloudformation.yaml`: AWS infrastructure definition
   - `certificates/`: AWS IoT Core certificates
   - `scripts/`: Utility scripts

## Prerequisites

- Python 3.8+
- AWS Account with appropriate permissions
- AWS IoT Core certificates
- AWS CLI configured
- Raspberry Pi with camera module

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd driver-drowsiness-alert-system
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure AWS credentials:
```bash
aws configure
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Deployment

1. Deploy AWS resources using CloudFormation:
```bash
aws cloudformation deploy \
    --template-file cloudformation.yaml \
    --stack-name drowsiness-alert-system \
    --capabilities CAPABILITY_IAM
```

2. Update the IoT endpoint in `src/config.py`

3. Place your AWS IoT Core certificates in the specified paths

## Usage

### Sending Driver Profile

```python
from src.client.mqtt_client import DrowsinessAlertClient

client = DrowsinessAlertClient(
    client_id="your-client-id",
    endpoint="your-iot-endpoint",
    cert_path="path/to/device.pem.crt",
    key_path="path/to/private.pem.key",
    ca_path="path/to/AmazonRootCA1.pem"
)

client.connect()

profile = {
    "id": "DRIVER123",
    "name": "John Doe",
    "gender": "male",
    "date_of_birth": "1990-01-01",
    "weight": 75.5,
    "height": 180.0,
    "emergency_contact": "+1234567890",
    "blood_type": "A+",
    "chronic_diseases": ["Hypertension"],
    "allergies": ["Penicillin"]
}

client.client.publish(
    topic="vehicle/driver/profile",
    payload=json.dumps(profile),
    qos=1
)
```

### Sending Drowsiness Alert

```python
from src.client.mqtt_client import DrowsinessAlertClient

client = DrowsinessAlertClient()
client.connect()

alert = {
    "driver_id": "DRIVER123",
    "drowsiness_level": 0.85,
    "confidence": 0.92,
    "location": {
        "latitude": 37.7749,
        "longitude": -122.4194
    },
    "speed": 65.5
}

client.send_drowsiness_alert(alert)
```

## Monitoring

### Usage Tracking
```bash
# Check current usage
aws cloudwatch get-metric-statistics \
    --namespace AWS/IoT \
    --metric-name MessageCount \
    --dimensions Name=ClientId,Value=raspberry-pi-client \
    --start-time $(date -u +"%Y-%m-%dT%H:%M:%SZ" -d "-30 days") \
    --end-time $(date -u +"%Y-%m-%dT%H:%M:%SZ") \
    --period 86400 \
    --statistics Sum
```

### CloudWatch Alarms
- IoT message count
- DynamoDB capacity units
- Lambda invocations

## Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Development

1. Format code:
```bash
black src/ tests/
```

2. Lint code:
```bash
flake8 src/ tests/
```

3. Type checking:
```bash
mypy src/ tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

