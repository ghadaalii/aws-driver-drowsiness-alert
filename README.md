# Driver Drowsiness Alert System

A real-time system for detecting driver drowsiness and alerting emergency services using AWS IoT Core. The system is optimized for AWS Free Tier usage and includes comprehensive monitoring and cost optimization features.

## Project Overview

This system monitors driver drowsiness in real-time and automatically alerts emergency services when necessary. It uses a Raspberry Pi for data collection and AWS services for processing and storage.

# System Status (June 2025)
- **End-to-end flow is fully operational:**
  - MQTT → IoT Core → Lambda → DynamoDB → MQTT Ack
  - All Lambda code is managed inline in CloudFormation (see `cloudformation.yaml`).
  - CloudFormation template includes robust error handling, logging, and correct resource naming (e.g., `driver-profile` for API Gateway).
  - Alerts are stored in DynamoDB, acknowledgments are sent to the vehicle, and driver data is joined and sent to the ambulance dashboard.

### Key Features

- Real-time drowsiness detection and alerting
- Driver profile management with medical information
- Emergency service integration with ambulance dashboard
- AWS IoT Core integration with MQTT communication
- DynamoDB for data storage with automatic TTL
- Free Tier optimization with usage monitoring
- Comprehensive testing suite
- Lambda function processing with driver-alert data joining

## System Architecture

### Components

1. **Data Collection (Raspberry Pi)**
   - Drowsiness detection model
   - Camera module
   - MQTT client for data transmission
   - GPS module for location tracking

2. **AWS Services**
   - IoT Core: Message broker and device management
   - Lambda: Serverless functions for data processing
   - DynamoDB: NoSQL database for data storage
   - CloudWatch: Monitoring and logging
   - API Gateway: HTTP endpoints for profile updates and ambulance dashboard alerts

3. **Database Structure**
   - `drivers-dev` Table:
     - Primary Key: `id` (String)
     - Columns: name, gender, date_of_birth, weight, height, emergency_contact, blood_type, chronic_diseases, allergies, last_updated, ttl
   
   - `drowsiness_alerts-dev` Table:
     - Primary Key: `alert_id` (String)
     - Secondary Index: `driver_id-timestamp-index`
     - Columns:
       - alert_id (String, Primary Key) - Unique identifier for the alert
       - driver_id (String) - Reference to driver in drivers table
       - timestamp (String, ISO8601) - When the alert was created
       - location (Map: latitude, longitude, description) - GPS coordinates and location description
       - message (String) - Alert message/description
       - processed (Boolean) - Whether the alert has been processed
       - ttl (Number) - Time to live for automatic deletion

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
                                                      ↓
                                                 Acknowledgment → Vehicle
   ```
   - Drowsiness detection triggers alert
   - Alert is sent via MQTT to `vehicle/alerts/drowsiness`
   - IoT Core receives the alert
   - Lambda function:
     - Retrieves driver information from driver table
     - Processes alert data
     - Stores simplified alert in DynamoDB
     - Publishes combined data to ambulance dashboard **via HTTP POST to API Gateway**
     - Sends acknowledgment back to vehicle via `vehicle/alerts/ack`

3. **Emergency Response Flow**
   ```
   DynamoDB → Lambda → IoT Core → Emergency Dashboard
   ```
   - Emergency services receive alert via HTTP POST endpoint
   - Access complete driver information
   - View real-time location and medical data
   - Coordinate response with driver details

## Project Structure

```
FProject/
├── README.md
├── requirements.txt
├── cloudformation.yaml
├── main.py
├── subscribe_and_publish.py
├── test_lambda_alert_processing.py
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
   - `main.py`: Main application entry point with usage monitoring
   - `src/config.py`: Configuration management and Free Tier limits
   - `src/lambda_functions.py`: AWS Lambda functions for data processing
   - `src/client/mqtt_client.py`: MQTT client for IoT Core communication

2. **Testing**
   - `test_lambda_alert_processing.py`: Comprehensive Lambda function testing
   - `subscribe_and_publish.py`: MQTT communication testing
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

### Testing MQTT Communication

```bash
# Test basic MQTT publish and subscribe
python subscribe_and_publish.py
```

### Testing Lambda Function Processing

```bash
# Test complete Lambda function flow
python test_lambda_alert_processing.py
```

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
    "alert_id": "ALERT123456",
    "driver_id": "DRIVER123",
    "timestamp": "2025-01-18T10:30:00Z",
    "location": {
        "latitude": 30.0444,
        "longitude": 31.2357,
        "description": "Cairo Ring Road, near Gate 3"
    },
    "message": "Driver fell asleep",
    "processed": False
}

client.client.publish(
    topic="vehicle/alerts/drowsiness",
    payload=json.dumps(alert),
    qos=1
)
```

### Monitoring Ambulance Dashboard

The ambulance dashboard now receives combined alert and driver data via an HTTP POST endpoint:

**Endpoint URL:**

```
https://<api-id>.execute-api.<region>.amazonaws.com/<env>/ambulance-alert
```

**Example POST request (Python):**

```python
import requests
import json

combined_alert = {
    "alert": {
        "alert_id": "ALERT123456",
        "driver_id": "DRIVER001",
        "timestamp": "2025-05-05T08:45:23Z",
        "location": {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "description": "Test location"
        },
        "message": "Driver fell asleep",
        "processed": True,
        "ttl": 1781826822
    },
    "driver_info": {
        "id": "DRIVER001",
        "name": "John Doe",
        "gender": "male",
        "date_of_birth": "1990-01-01",
        "weight": 75.5,
        "height": 180.0,
        "emergency_contact": "+1234567890",
        "blood_type": "A+",
        "chronic_diseases": ["Hypertension"],
        "allergies": ["Penicillin"],
        "last_updated": "2025-05-05T08:00:00Z",
        "ttl": 1781826822
    }
}

endpoint = "https://<api-id>.execute-api.<region>.amazonaws.com/<env>/ambulance-alert"
response = requests.post(endpoint, json=combined_alert)
print(response.status_code, response.text)
```

**Note:** Replace `<api-id>`, `<region>`, and `<env>` with your actual API Gateway values. The endpoint is also output by CloudFormation as `AmbulanceAlertApiEndpoint`.

### Monitoring Vehicle Acknowledgments

```python
# Subscribe to acknowledgment messages
client.client.subscribe("vehicle/alerts/ack")

def on_message(client, userdata, msg):
    if msg.topic == "vehicle/alerts/ack":
        ack_data = json.loads(msg.payload.decode())
        print(f"Alert Acknowledgment: {ack_data}")

client.client.on_message = on_message
```

## Testing

### Run All Tests
```bash
# Run comprehensive Lambda function test
python test_lambda_alert_processing.py

# Run MQTT communication test
python subscribe_and_publish.py

# Run individual test suites
pytest tests/
```

### Test Coverage
```bash
pytest --cov=src tests/
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

### Free Tier Monitoring
The system includes built-in Free Tier monitoring:
- Tracks IoT message usage
- Monitors DynamoDB read/write units
- Alerts when approaching limits
- Automatic usage statistics

## DynamoDB Schema & Example Data

### drivers-dev Table
- **Primary Key:** `id` (String)
- **Columns:** name, gender, date_of_birth, weight, height, emergency_contact, blood_type, chronic_diseases, allergies, last_updated, ttl

| id                                   | name     | gender | date_of_birth | weight | height | blood_type | emergency_contact | chronic_diseases | allergies   | last_updated                |
|--------------------------------------|----------|--------|---------------|--------|--------|------------|------------------|------------------|-------------|-----------------------------|
| DRIVER123                            | John Doe | male   | 1990-01-01    | 75.5   | 180    | A+         | +1234567890      | Hypertension     | Penicillin  | 2025-06-18T01:38:43.193645  |
| fac15154-8712-af70-5b23-f3fd61e3db89 | Anna     | Female | 30-01-2000    | 52     | 157    | AB+        | 01233445577      | Asthma           | no          | 2025-06-23T22:31:10.056404  |
| ...                                  | ...      | ...    | ...           | ...    | ...    | ...        | ...              | ...              | ...         | ...                         |

### drowsiness_alerts-dev Table
- **Primary Key:** `alert_id` (String)
- **Secondary Index:** `driver_id-timestamp-index`
- **Columns:** alert_id, driver_id, timestamp, location (latitude, longitude, description), message, processed, ttl

| alert_id                              | driver_id                             | timestamp              | location (lat,lon,desc)         | message              | processed | ttl         |
|---------------------------------------|---------------------------------------|------------------------|-------------------------------|----------------------|-----------|-------------|
| b5712103-efbd-47e9-83a9-21783229df51  | test-driver-id                        | 2025-06-23T22:15:58Z   | 30.0444,31.2357,Cairo, Egypt  | Driver fell asleep   | true      | ...         |
| cacae107-7aaf-83bd-1b2a-e01e5b4bbd7d  | fac15154-8712-af70-5b23-f3fd61e3db89  | 2025-06-23T22:31:12Z   | 30.0444,31.2357,Cairo, Egypt  | Driver fell asleep   | true      | ...         |

## Querying DynamoDB for Data

**Get all drivers:**
```bash
aws dynamodb scan --table-name drivers-dev --select ALL_ATTRIBUTES
```
**Get all alerts:**
```bash
aws dynamodb scan --table-name drowsiness_alerts-dev --select ALL_ATTRIBUTES
```
**Get a specific driver by ID:**
```bash
aws dynamodb get-item --table-name drivers-dev --key '{"id": {"S": "fac15154-8712-af70-5b23-f3fd61e3db89"}}' --region us-east-1
```
**Get a specific alert by ID:**
```bash
aws dynamodb get-item --table-name drowsiness_alerts-dev --key '{"alert_id": {"S": "cacae107-7aaf-83bd-1b2a-e01e5b4bbd7d"}}' --region us-east-1
```

## Troubleshooting

- **No acknowledgment or DynamoDB write:**
  - Check CloudWatch logs for Lambda errors (e.g., import errors, permission issues)
  - Ensure CloudFormation stack update completed successfully
  - Make sure the IoT Rule is enabled and points to the correct Lambda
- **Lambda code not updating:**
  - CloudFormation must be updated and the stack must finish updating for inline Lambda code changes to take effect
- **API Gateway resource conflicts:**
  - Use unique path parts (e.g., `driver-profile` instead of `driver`) to avoid naming conflicts
- **Data not joined:**
  - Ensure the driver ID in the alert matches an existing driver profile in DynamoDB

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

## Lambda Functions

### process_alert_handler
- **Trigger**: IoT Core topic rule on `vehicle/alerts/drowsiness`
- **Function**: 
  - Receives drowsiness alert from vehicle
  - Retrieves driver profile from DynamoDB using driver_id
  - Combines alert and driver data
  - Stores simplified alert in DynamoDB (alert_id, driver_id, timestamp, location, message, processed, ttl)
  - **Sends combined data to ambulance dashboard via HTTP POST to API Gateway endpoint**
  - Sends acknowledgment back to vehicle (`vehicle/alerts/ack`)

### update_profile_handler
- **Trigger**: IoT Core topic rule on `vehicle/driver/profile`
- **Function**:
  - Receives driver profile updates
  - Validates and processes data
  - Stores in DynamoDB with TTL

### http_update_profile_handler
- **Trigger**: API Gateway HTTP POST
- **Function**:
  - Receives HTTP requests for profile updates
  - Processes JSON data
  - Updates DynamoDB
  - Publishes to IoT Core

## Ambulance Dashboard HTTP Endpoint

The ambulance dashboard receives combined alert and driver data via an HTTP POST endpoint:

**CloudFormation Output:**

```
AmbulanceAlertApiEndpoint = https://<api-id>.execute-api.<region>.amazonaws.com/<env>/ambulance-alert
```

**How to use:**
- The backend/dashboard should listen for POST requests at this endpoint.
- Each POST contains a JSON body with the combined alert and driver info as shown above.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

 