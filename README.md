# Driver Drowsiness Alert System

A real-time system for detecting driver drowsiness and alerting emergency services using AWS IoT Core with WebSocket support for real-time dashboard communication. The system is optimized for AWS Free Tier usage and includes comprehensive monitoring and cost optimization features.

## Project Overview

This system monitors driver drowsiness in real-time and automatically alerts emergency services when necessary. It uses a Raspberry Pi for data collection, AWS services for processing and storage, and WebSocket connections for real-time ambulance dashboard communication.

# System Status (January 2025)
- **End-to-end flow is fully operational:**
  - MQTT → IoT Core → Lambda → DynamoDB → WebSocket → Ambulance Dashboard
  - All Lambda code is managed inline in CloudFormation (see `cloudformation.yaml`).
  - CloudFormation template includes robust error handling, logging, and correct resource naming.
  - Alerts are stored in DynamoDB, acknowledgments are sent to the vehicle, and driver data is joined and sent to the ambulance dashboard via WebSocket connections.
  - **WebSocket API Gateway provides real-time communication for ambulance dashboard**

### Key Features

- Real-time drowsiness detection and alerting
- Driver profile management with medical information
- Emergency service integration with real-time WebSocket dashboard
- AWS IoT Core integration with MQTT communication
- DynamoDB for data storage with automatic TTL
- WebSocket API Gateway for real-time ambulance dashboard communication
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
   - API Gateway: WebSocket endpoints for real-time ambulance dashboard communication
   - WebSocket API Gateway: Real-time bidirectional communication

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

   - `websocket-connections-dev` Table:
     - Primary Key: `connection_id` (String)
     - Columns:
       - connection_id (String, Primary Key) - WebSocket connection identifier
       - user_id (String) - User identifier for the connection
       - timestamp (String, ISO8601) - When the connection was established
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
   Raspberry Pi → MQTT → IoT Core → Lambda → DynamoDB → WebSocket → Ambulance Dashboard
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
     - **Sends combined data to ambulance dashboard via WebSocket connections**
     - Sends acknowledgment back to vehicle via `vehicle/alerts/ack`

3. **Emergency Response Flow**
   ```
   DynamoDB → Lambda → WebSocket API Gateway → Ambulance Dashboard (Real-time)
   ```
   - Emergency services receive real-time alerts via WebSocket connections
   - Access complete driver information
   - View real-time location and medical data
   - Coordinate response with driver details

## Project Structure

```
FProject/
├── README.md
├── requirements.txt
├── cloudformation.yaml          # AWS infrastructure with WebSocket support
├── main.py                      # Main application entry point
├── presentation_story.md        # Project presentation
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuration and environment variables
│   ├── lambda_functions.py      # AWS Lambda functions with WebSocket support
│   └── client/
│       ├── __init__.py
│       └── mqtt_client.py       # MQTT client for IoT Core
├── tests/
│   ├── test_dashboard_data.py       # WebSocket dashboard data testing
│   ├── test_combined_data.py        # Combined alert and driver data tests
│   ├── test_end_to_end.py           # End-to-end system tests
│   ├── test_alert.json              # Sample alert data
│   ├── subscribe_and_publish.py     # MQTT communication testing
│   ├── test_driver_profile.py       # Driver profile flow tests
│   ├── test_mqtt_messages.py        # MQTT message tests
│   ├── test_data_flow.py            # Data flow tests
│   └── test_database.py             # DynamoDB tests
├── certificates/                # AWS IoT Core certificates
│   ├── device.pem.crt
│   ├── private.pem.key
│   ├── public.pem.key
│   └── AmazonRootCA1.pem
└── scripts/
    └── create_certificates.sh   # Certificate creation script
```

## Components

1. **Core Application**
   - `main.py`: Main application entry point with usage monitoring
   - `src/config.py`: Configuration management and Free Tier limits
   - `src/lambda_functions.py`: AWS Lambda functions for data processing with WebSocket support
   - `src/client/mqtt_client.py`: MQTT client for IoT Core communication

2. **Testing**
   - `test_dashboard_data.py`: WebSocket dashboard communication testing
   - `test_combined_data.py`: Combined alert and driver data testing
   - `test_end_to_end.py`: Complete system flow testing
   - `subscribe_and_publish.py`: MQTT communication testing
   - Comprehensive test suite for all components

3. **Infrastructure**
   - `cloudformation.yaml`: AWS infrastructure definition with WebSocket API Gateway
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
python tests/subscribe_and_publish.py
```

### Testing WebSocket Dashboard Communication

```bash
# Test WebSocket dashboard data flow
python tests/test_dashboard_data.py
```

### Testing End-to-End Flow

```bash
# Test complete system flow
python tests/test_end_to_end.py
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

### Connecting to Ambulance Dashboard WebSocket

The ambulance dashboard receives real-time alerts via WebSocket connections:

**WebSocket Endpoint URL:**
```
wss://<api-id>.execute-api.<region>.amazonaws.com/<env>
```

**Example WebSocket Client (JavaScript):**
```javascript
const ws = new WebSocket('wss://<api-id>.execute-api.<region>.amazonaws.com/<env>');

ws.onopen = function() {
    console.log('Connected to ambulance dashboard WebSocket');
};

ws.onmessage = function(event) {
    const alertData = JSON.parse(event.data);
    console.log('Received alert:', alertData);
    
    // Process the combined alert and driver data
    const { alert, driver_info } = alertData;
    
    // Update dashboard UI with real-time data
    updateDashboard(alert, driver_info);
};

ws.onclose = function() {
    console.log('Disconnected from WebSocket');
};

function updateDashboard(alert, driverInfo) {
    // Update dashboard with real-time alert and driver information
    document.getElementById('alert-id').textContent = alert.alert_id;
    document.getElementById('driver-name').textContent = driverInfo.name;
    document.getElementById('location').textContent = alert.location.description;
    document.getElementById('blood-type').textContent = driverInfo.blood_type;
    // ... update other dashboard elements
}
```

**Example WebSocket Client (Python):**
```python
import websocket
import json

def on_message(ws, message):
    alert_data = json.loads(message)
    print(f"Received alert: {alert_data}")
    
    // Process the combined alert and driver data
    alert = alert_data['alert']
    driver_info = alert_data['driver_info']
    
    // Update dashboard with real-time data
    update_dashboard(alert, driver_info)

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    print("Connected to ambulance dashboard WebSocket")

def update_dashboard(alert, driver_info):
    print(f"Alert ID: {alert['alert_id']}")
    print(f"Driver: {driver_info['name']}")
    print(f"Location: {alert['location']['description']}")
    print(f"Blood Type: {driver_info['blood_type']}")

// Connect to WebSocket
websocket_url = "wss://<api-id>.execute-api.<region>.amazonaws.com/<env>"
ws = websocket.WebSocketApp(
    websocket_url,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()
```

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
# Test WebSocket dashboard communication
python tests/test_dashboard_data.py

# Test combined data flow
python tests/test_combined_data.py

# Test end-to-end system flow
python tests/test_end_to_end.py

# Test MQTT communication
python tests/subscribe_and_publish.py

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
- WebSocket API Gateway metrics

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

### websocket-connections-dev Table
- **Primary Key:** `connection_id` (String)
- **Columns:** connection_id, user_id, timestamp, ttl

| connection_id                         | user_id                               | timestamp              | ttl         |
|---------------------------------------|---------------------------------------|------------------------|-------------|
| abc123def456                          | ambulance-unit-001                    | 2025-01-18T10:30:00Z   | ...         |
| xyz789uvw012                          | emergency-center-002                  | 2025-01-18T10:35:00Z   | ...         |

## Querying DynamoDB for Data

**Get all drivers:**
```bash
aws dynamodb scan --table-name drivers-dev --select ALL_ATTRIBUTES
```
**Get all alerts:**
```bash
aws dynamodb scan --table-name drowsiness_alerts-dev --select ALL_ATTRIBUTES
```
**Get active WebSocket connections:**
```bash
aws dynamodb scan --table-name websocket-connections-dev --select ALL_ATTRIBUTES
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
- **WebSocket connection issues:**
  - Check WebSocket API Gateway logs in CloudWatch
  - Verify WebSocket Lambda functions have proper permissions
  - Ensure WebSocket connections table exists and is accessible
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
  - **Sends combined data to ambulance dashboard via WebSocket connections**
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

### WebSocket Lambda Functions
- **WebSocketAlertFunction**: Sends real-time alerts to ambulance dashboard via WebSocket

> **Note:** All ambulance alert delivery is performed in real-time via WebSocket connections. HTTP is not used for ambulance alert delivery in this system.

## WebSocket API Gateway

The ambulance dashboard receives real-time alerts via WebSocket connections:

**CloudFormation Outputs:**
```
WebSocketApiEndpoint = wss://<api-id>.execute-api.<region>.amazonaws.com/<env>
WebSocketConnectionsTableName = websocket-connections-dev
```

**WebSocket Routes:**
- `$connect`: Handle new WebSocket connections
- `$disconnect`: Handle WebSocket disconnections
- `$default`: Handle default WebSocket messages

**How to use:**
- The ambulance dashboard should establish WebSocket connections to the endpoint
- Real-time alerts will be pushed to all connected clients
- Each alert contains combined alert and driver information
- Connections are automatically managed and cleaned up

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

 