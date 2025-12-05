"""
Configuration settings for Multi-Source Job Scraper
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
# Job Search APIs Configuration
# =============================================================================
# JSearch API (RapidAPI) - Primary source
# Get your key at https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
JSEARCH_HOST = "jsearch.p.rapidapi.com"

# Adzuna API - Secondary source (covers Indeed, Monster, etc.)
# Get your keys at https://developer.adzuna.com/
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")

# RemoteOK API - For remote jobs (no API key needed)
REMOTEOK_ENABLED = os.getenv("REMOTEOK_ENABLED", "true").lower() == "true"

# =============================================================================
# Job Search Parameters
# =============================================================================
# Multiple job titles to search for
JOB_TITLES = [
    "Data Engineer",
    "Analytics Engineer", 
    "Data Scientist ETL",
    "Data Scientist SQL",
    "Data Scientist Python",
]

# Location filter
JOB_LOCATION = "United States"
JOB_COUNTRY_CODE = "us"

# Experience filter
EXPERIENCE_MIN_YEARS = 3
EXPERIENCE_MAX_YEARS = 7

# Skills to look for in Data Scientist roles (ETL-focused)
ETL_SKILLS = [
    "etl", "data pipeline", "airflow", "spark", "sql", 
    "python", "data warehouse", "snowflake", "databricks",
    "dbt", "kafka", "data modeling", "bigquery", "redshift"
]

# Number of results to fetch per request
RESULTS_PER_PAGE = 20
MAX_PAGES_PER_SOURCE = 3  # Total max results per source: 60

# =============================================================================
# Output Configuration
# =============================================================================
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
CSV_FILENAME_PREFIX = "job_listings"

# =============================================================================
# Airflow Configuration
# =============================================================================
DAG_ID = "multi_source_job_scraper"

# Schedule: 6AM, 12PM, 6PM, 12AM PST (America/Los_Angeles)
# PST is UTC-8, so 6AM PST = 14:00 UTC
# Cron: minute hour day month day_of_week
SCHEDULE_INTERVAL = "0 6,12,18,0 * * *"  # Every 6 hours starting at 6AM
SCHEDULE_TIMEZONE = "America/Los_Angeles"  # PST/PDT

DAG_OWNER = "airflow"
DAG_RETRIES = 2
DAG_RETRY_DELAY_MINUTES = 5

# =============================================================================
# Job Sources Configuration
# =============================================================================
JOB_SOURCES = {
    "jsearch": {
        "name": "JSearch (LinkedIn, Indeed, etc.)",
        "enabled": True,
        "requires_api_key": True,
    },
    "adzuna": {
        "name": "Adzuna (Monster, CareerBuilder, etc.)",
        "enabled": True,
        "requires_api_key": True,
    },
    "remoteok": {
        "name": "RemoteOK (Remote Jobs)",
        "enabled": True,
        "requires_api_key": False,
    },
}
