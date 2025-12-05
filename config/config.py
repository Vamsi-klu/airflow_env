"""
Configuration settings for LinkedIn Job Scraper
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# AWS SNS Configuration
# =============================================================================
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "")

# =============================================================================
# Job Search Configuration
# =============================================================================
# JSearch API (RapidAPI) - Get your key at https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "jsearch.p.rapidapi.com"

# Search parameters
JOB_SEARCH_QUERY = "Data Engineer"
JOB_LOCATION = "United States"
EXPERIENCE_MIN_YEARS = 3
EXPERIENCE_MAX_YEARS = 7

# Number of results to fetch per request (max 20 for free tier)
RESULTS_PER_PAGE = 20
MAX_PAGES = 5  # Total max results: 100

# =============================================================================
# Output Configuration
# =============================================================================
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
CSV_FILENAME_PREFIX = "data_engineer_jobs"

# =============================================================================
# Airflow Configuration
# =============================================================================
DAG_ID = "linkedin_job_scraper"
SCHEDULE_INTERVAL = "0 */6 * * *"  # Every 6 hours
DAG_OWNER = "airflow"
DAG_RETRIES = 2
DAG_RETRY_DELAY_MINUTES = 5
