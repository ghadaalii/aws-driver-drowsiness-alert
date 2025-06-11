#!/bin/bash

# Create certificates directory
mkdir -p certificates

# Get IoT endpoint
echo "Getting IoT endpoint..."
IOT_ENDPOINT=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text)

# Create certificate
echo "Creating certificate..."
CERTIFICATE_ARN=$(aws iot create-keys-and-certificate \
    --set-as-active \
    --certificate-pem-outfile certificates/device.pem.crt \
    --public-key-outfile certificates/public.pem.key \
    --private-key-outfile certificates/private.pem.key \
    --query certificateArn \
    --output text)

# Download Amazon Root CA
echo "Downloading Amazon Root CA..."
curl -o certificates/AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem

# Create a zip file with certificates
echo "Creating zip file..."
zip -r certificates.zip certificates/

# Create a README file with instructions
cat > certificates/README.txt << EOL
AWS IoT Core Certificates

These certificates are required to connect to AWS IoT Core.

Files included:
1. device.pem.crt - Device certificate
2. private.pem.key - Private key
3. AmazonRootCA1.pem - Amazon Root CA certificate

IoT Endpoint: ${IOT_ENDPOINT}

IMPORTANT:
- Keep these files secure and never share them publicly
- Store them in a safe location
- Use them only for connecting to AWS IoT Core
- Do not commit them to version control

To use these certificates:
1. Extract the certificates.zip file
2. Place the certificates in your project's certificates directory
3. Update your code to use these certificate paths
4. Use the IoT endpoint provided above

Example usage in Python:
\`\`\`python
client = DrowsinessAlertClient(
    client_id="your-client-id",
    endpoint="${IOT_ENDPOINT}",
    cert_path="certificates/device.pem.crt",
    key_path="certificates/private.pem.key",
    ca_path="certificates/AmazonRootCA1.pem"
)
\`\`\`
EOL

echo "Certificates have been created and packaged in certificates.zip"
echo "Please share this file securely with your friend"
echo "The certificates are also available in the certificates/ directory" 