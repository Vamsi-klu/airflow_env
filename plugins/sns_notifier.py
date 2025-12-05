"""
SNS Notifier Module

Sends email notifications via AWS SNS when new jobs are found.
Enhanced to show breakdown by source and job role.
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
    SNS_TOPIC_ARN,
    JOB_TITLES,
    JOB_LOCATION,
    EXPERIENCE_MIN_YEARS,
    EXPERIENCE_MAX_YEARS
)


def get_sns_client():
    """Initialize and return an SNS client."""
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        return boto3.client(
            "sns",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    else:
        return boto3.client("sns", region_name=AWS_REGION)


def send_notification(job_count: int, csv_filepath: str, role_counts: dict = None) -> bool:
    """
    Send an SNS notification about new job listings.
    
    Args:
        job_count: Number of jobs found
        csv_filepath: Path to the generated CSV file
        role_counts: Optional dict with breakdown by role
        
    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    if not SNS_TOPIC_ARN:
        print("Warning: SNS_TOPIC_ARN not configured. Skipping notification.")
        return False
    
    client = get_sns_client()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S PST")
    
    # Build role breakdown string
    role_breakdown = ""
    if role_counts:
        role_breakdown = "\n".join([f"   • {role}: {count}" for role, count in role_counts.items()])
    else:
        role_breakdown = "   (breakdown not available)"
    
    subject = f"🔔 Job Alert - {job_count} New Data/Analytics Positions Found"
    
    message = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Multi-Source Job Scraper Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕐 Scan Time: {timestamp}
📍 Location: {JOB_LOCATION}
📋 Experience: {EXPERIENCE_MIN_YEARS}-{EXPERIENCE_MAX_YEARS} years

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Job Titles Searched
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join([f'   • {title}' for title in JOB_TITLES])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Results Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Total Jobs Found: {job_count}

📊 By Role:
{role_breakdown}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 Data Sources Used
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • JSearch (LinkedIn, Indeed, Glassdoor, ZipRecruiter)
   • Adzuna (Monster, CareerBuilder, SimplyHired)
   • RemoteOK (Remote-focused positions)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 CSV File Location
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{csv_filepath}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Schedule: Every 6 hours (6AM, 12PM, 6PM, 12AM PST)
📧 This is an automated message from your Job Scraper.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
                    "StringValue": "MultiSource"
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
    """Create an SNS topic if it doesn't exist."""
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
    """Subscribe an email address to an SNS topic."""
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
    # Test notification with role breakdown
    print("Testing SNS notification...")
    result = send_notification(
        job_count=75,
        csv_filepath="/path/to/test/job_listings_20240115.csv",
        role_counts={
            "Data Engineer": 35,
            "Analytics Engineer": 20,
            "Data Scientist": 15,
            "Other": 5
        }
    )
    print(f"Notification test result: {'Success' if result else 'Failed'}")
