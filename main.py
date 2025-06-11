"""
Main entry point for the Driver Drowsiness Alert System
Optimized for AWS Free Tier usage
This script coordinates all components:
1. MQTT client for sending data
2. AWS Lambda functions for processing data
3. DynamoDB for storage
4. Integration with the drowsiness detection model
"""

import os
import time
import csv
import json
from datetime import datetime, timedelta
from src.client.mqtt_client import DrowsinessAlertClient
from src.config import (
    IOT_ENDPOINT,
    IOT_CLIENT_ID,
    CERT_PATH,
    KEY_PATH,
    ROOT_CA_PATH,
    TOPIC_DROWSINESS,
    TOPIC_DRIVER_PROFILE,
    FREE_TIER_LIMITS
)

class DrowsinessSystem:
    def __init__(self):
        """Initialize the Drowsiness Alert System"""
        # Set up environment variables for AWS IoT Core
        os.environ['IOT_ENDPOINT'] = IOT_ENDPOINT
        os.environ['IOT_CLIENT_ID'] = IOT_CLIENT_ID
        os.environ['CERT_PATH'] = CERT_PATH
        os.environ['KEY_PATH'] = KEY_PATH
        os.environ['ROOT_CA_PATH'] = ROOT_CA_PATH

        # Initialize MQTT client
        self.client = DrowsinessAlertClient()
        
        # File paths for CSV data
        self.drivers_csv = "data/drivers.csv"
        self.alerts_csv = "data/drowsiness_alerts.csv"
        
        # Usage tracking for free tier limits
        self.usage_stats = {
            'iot_messages': 0,
            'start_time': datetime.utcnow(),
            'last_reset': datetime.utcnow()
        }
        
        # Create usage tracking file
        self.usage_file = "data/usage_stats.json"
        self.load_usage_stats()

    def load_usage_stats(self):
        """Load usage statistics from file"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    self.usage_stats = json.load(f)
                    # Convert string dates back to datetime objects
                    self.usage_stats['start_time'] = datetime.fromisoformat(self.usage_stats['start_time'])
                    self.usage_stats['last_reset'] = datetime.fromisoformat(self.usage_stats['last_reset'])
            except Exception as e:
                print(f"Error loading usage stats: {e}")
                self.reset_usage_stats()

    def save_usage_stats(self):
        """Save usage statistics to file"""
        try:
            os.makedirs(os.path.dirname(self.usage_file), exist_ok=True)
            stats_to_save = self.usage_stats.copy()
            # Convert datetime objects to strings
            stats_to_save['start_time'] = stats_to_save['start_time'].isoformat()
            stats_to_save['last_reset'] = stats_to_save['last_reset'].isoformat()
            with open(self.usage_file, 'w') as f:
                json.dump(stats_to_save, f)
        except Exception as e:
            print(f"Error saving usage stats: {e}")

    def reset_usage_stats(self):
        """Reset usage statistics"""
        self.usage_stats = {
            'iot_messages': 0,
            'start_time': datetime.utcnow(),
            'last_reset': datetime.utcnow()
        }
        self.save_usage_stats()

    def check_free_tier_limits(self):
        """Check if we're within free tier limits"""
        current_time = datetime.utcnow()
        
        # Check if we need to reset monthly counters
        if (current_time - self.usage_stats['last_reset']).days >= 30:
            self.reset_usage_stats()
        
        # Check IoT message limit
        if self.usage_stats['iot_messages'] >= FREE_TIER_LIMITS['iot_messages_per_month']:
            print("WARNING: Approaching AWS IoT Core free tier message limit!")
            return False
        
        return True

    def update_usage_stats(self, message_count=1):
        """Update usage statistics"""
        self.usage_stats['iot_messages'] += message_count
        self.save_usage_stats()

    def start(self):
        """Start the Drowsiness Alert System"""
        try:
            print("Starting Drowsiness Alert System...")
            print("Free Tier Limits:")
            print(f"- IoT Messages per month: {FREE_TIER_LIMITS['iot_messages_per_month']}")
            print(f"- DynamoDB WCU: {FREE_TIER_LIMITS['dynamodb_wcu']}")
            print(f"- DynamoDB RCU: {FREE_TIER_LIMITS['dynamodb_rcu']}")
            print(f"- S3 Storage: {FREE_TIER_LIMITS['s3_storage_gb']}GB")
            
            # Connect to AWS IoT Core
            self.client.connect()
            print("Connected to AWS IoT Core")

            # Main loop
            while True:
                if not self.check_free_tier_limits():
                    print("Free tier limits reached. Waiting for next month...")
                    time.sleep(3600)  # Check every hour
                    continue

                # Process driver profiles
                if os.path.exists(self.drivers_csv):
                    print("\nProcessing driver profiles...")
                    success_count = self.client.send_drivers_from_csv(self.drivers_csv)
                    self.update_usage_stats(success_count)
                
                # Process drowsiness alerts
                if os.path.exists(self.alerts_csv):
                    print("\nProcessing drowsiness alerts...")
                    success_count = self.client.send_alerts_from_csv(self.alerts_csv)
                    self.update_usage_stats(success_count)
                
                # Print usage statistics
                print(f"\nCurrent Usage (This Month):")
                print(f"- IoT Messages: {self.usage_stats['iot_messages']}/{FREE_TIER_LIMITS['iot_messages_per_month']}")
                
                # Wait before next iteration
                print("\nWaiting for new data...")
                time.sleep(60)  # Check for new data every minute

        except KeyboardInterrupt:
            print("\nShutting down Drowsiness Alert System...")
        except Exception as e:
            print(f"Error in Drowsiness Alert System: {str(e)}")
        finally:
            self.client.disconnect()
            self.save_usage_stats()
            print("System shutdown complete")

    def create_sample_csv_files(self):
        """Create sample CSV files for testing"""
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Sample driver profile data (optimized for free tier)
        driver_data = [
            {
                'driver_id': 'DRIVER001',
                'name': 'John Doe',
                'age': '35',
                'blood_type': 'O+',
                'medical_conditions': 'hypertension',
                'emergency_contact': '+1234567890',
                'vehicle_info': 'Toyota Camry 2023'
            }
        ]

        # Sample drowsiness alert data (optimized for free tier)
        alert_data = [
            {
                'driver_id': 'DRIVER001',
                'drowsiness_level': '0.85',
                'confidence': '0.92',
                'gps_coordinates': '37.7749,-122.4194',
                'vehicle_speed': '65.5',
                'timestamp': datetime.utcnow().isoformat()
            }
        ]

        # Write driver profiles to CSV
        with open(self.drivers_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=driver_data[0].keys())
            writer.writeheader()
            writer.writerows(driver_data)

        # Write drowsiness alerts to CSV
        with open(self.alerts_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=alert_data[0].keys())
            writer.writeheader()
            writer.writerows(alert_data)

        print(f"Created sample CSV files in {os.path.abspath('data')}")

if __name__ == "__main__":
    # Create and start the system
    system = DrowsinessSystem()
    
    # Create sample data if needed
    if not os.path.exists("data"):
        system.create_sample_csv_files()
    
    # Start the system
    system.start() 