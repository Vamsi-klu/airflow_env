"""
SNS Notifier Module

Sends email notifications via AWS SNS when new jobs are found.
"""
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import (
    AWS_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    SNS_TOPIC_ARN
)


def get_sns_client():
    """
    Initialize and return an SNS client.
    
    Returns:
        boto3.client: SNS client instance
    """
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        # Use explicit credentials
        return boto3.client(
            "sns",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    else:
        # Use default credentials (IAM role, ~/.aws/credentials, etc.)
        return boto3.client("sns", region_name=AWS_REGION)


def send_notification(job_count: int, csv_filepath: str) -> bool:
    """
    Send an SNS notification about new job listings.
    
    Args:
        job_count: Number of jobs found
        csv_filepath: Path to the generated CSV file
        
    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    if not SNS_TOPIC_ARN:
        print("Warning: SNS_TOPIC_ARN not configured. Skipping notification.")
        return False
    
    client = get_sns_client()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    subject = f"🔔 Data Engineer Jobs Alert - {job_count} New Listings Found"
    
    message = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 LinkedIn Job Scraper Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕐 Scan Time: {timestamp}
🔍 Search Query: Data Engineer in United States
📋 Experience Filter: 3-7 years

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Results Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Total Jobs Found: {job_count}
📁 CSV File: {csv_filepath}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next scan scheduled in 6 hours.

This is an automated message from your LinkedIn Job Scraper.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    try:
        response = client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message,
            MessageAttributes={
                "JobCount": {
                    "DataType": "Number",
                    "StringValue": str(job_count)
                },
                "ScanType": {
                    "DataType": "String",
                    "StringValue": "Scheduled"
                }
            }
        )
        
        message_id = response.get("MessageId")
        print(f"Notification sent successfully. MessageId: {message_id}")
        return True
        
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(f"Failed to send notification: {error_code} - {error_message}")
        return False
    except Exception as e:
        print(f"Unexpected error sending notification: {e}")
        return False


def create_sns_topic(topic_name: str = "job-alerts") -> str:
    """
    Create an SNS topic if it doesn't exist.
    
    Args:
        topic_name: Name for the SNS topic
        
    Returns:
        str: Topic ARN
    """
    client = get_sns_client()
    
    try:
        response = client.create_topic(Name=topic_name)
        topic_arn = response["TopicArn"]
        print(f"SNS topic created/found: {topic_arn}")
        return topic_arn
    except ClientError as e:
        print(f"Error creating SNS topic: {e}")
        return None


def subscribe_email(topic_arn: str, email: str) -> bool:
    """
    Subscribe an email address to an SNS topic.
    
    Args:
        topic_arn: ARN of the SNS topic
        email: Email address to subscribe
        
    Returns:
        bool: True if subscription created successfully
    """
    client = get_sns_client()
    
    try:
        response = client.subscribe(
            TopicArn=topic_arn,
            Protocol="email",
            Endpoint=email
        )
        print(f"Subscription created. Check {email} for confirmation link.")
        return True
    except ClientError as e:
        print(f"Error subscribing email: {e}")
        return False


if __name__ == "__main__":
    # Test notification (will fail without proper AWS config)
    print("Testing SNS notification...")
    result = send_notification(
        job_count=25,
        csv_filepath="/path/to/test/jobs.csv"
    )
    print(f"Notification test result: {'Success' if result else 'Failed'}")
