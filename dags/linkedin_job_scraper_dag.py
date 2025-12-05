"""
Multi-Source Job Scraper DAG

Automated pipeline that runs every 6 hours starting at 6AM PST to:
1. Scrape Data Engineer, Analytics Engineer, and Data Scientist jobs
2. Pull from multiple sources: JSearch, Adzuna, RemoteOK
3. Filter for positions requiring 3-7 years of experience with ETL skills
4. Export results to CSV
5. Send email notification via AWS SNS
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import sys
import os
import pendulum

# Add plugins directory to path
plugins_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
sys.path.insert(0, plugins_path)

# Add config directory to path
config_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, config_path)

from config.config import (
    DAG_ID,
    SCHEDULE_INTERVAL,
    SCHEDULE_TIMEZONE,
    DAG_OWNER,
    DAG_RETRIES,
    DAG_RETRY_DELAY_MINUTES,
    JOB_TITLES
)

# =============================================================================
# Default DAG arguments
# =============================================================================
default_args = {
    "owner": DAG_OWNER,
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": DAG_RETRIES,
    "retry_delay": timedelta(minutes=DAG_RETRY_DELAY_MINUTES),
}

# =============================================================================
# Task Functions
# =============================================================================

def scrape_jobs_task(**context):
    """
    Task to scrape job listings from multiple sources.
    Pushes the list of jobs to XCom for the next task.
    """
    from job_scraper import scrape_all_jobs
    
    print("Starting multi-source job scraping...")
    print(f"Searching for roles: {', '.join(JOB_TITLES)}")
    
    jobs = scrape_all_jobs()
    
    # Push jobs to XCom
    context["ti"].xcom_push(key="jobs", value=jobs)
    
    # Log summary by source
    sources = {}
    for job in jobs:
        source = job.get("source", "Unknown")
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\nSummary by source:")
    for source, count in sources.items():
        print(f"  - {source}: {count} jobs")
    
    print(f"\nTotal: {len(jobs)} jobs scraped successfully")
    return len(jobs)


def export_csv_task(**context):
    """
    Task to export scraped jobs to CSV.
    Pulls jobs from XCom and pushes the CSV filepath.
    """
    from csv_exporter import export_to_csv
    
    # Pull jobs from previous task
    ti = context["ti"]
    jobs = ti.xcom_pull(task_ids="scrape_jobs", key="jobs")
    
    if jobs is None:
        jobs = []
        print("Warning: No jobs received from scraper")
    
    print(f"Exporting {len(jobs)} jobs to CSV...")
    csv_filepath = export_to_csv(jobs)
    
    # Push filepath to XCom
    ti.xcom_push(key="csv_filepath", value=csv_filepath)
    ti.xcom_push(key="job_count", value=len(jobs))
    
    # Calculate breakdown by role
    role_counts = {}
    for job in jobs:
        title = job.get("title", "").lower()
        if "data engineer" in title:
            role = "Data Engineer"
        elif "analytics engineer" in title:
            role = "Analytics Engineer"
        elif "data scientist" in title:
            role = "Data Scientist"
        else:
            role = "Other"
        role_counts[role] = role_counts.get(role, 0) + 1
    
    ti.xcom_push(key="role_counts", value=role_counts)
    
    print(f"CSV exported to: {csv_filepath}")
    return csv_filepath


def send_notification_task(**context):
    """
    Task to send SNS notification about the job scan results.
    Pulls job count and CSV filepath from XCom.
    """
    from sns_notifier import send_notification
    
    ti = context["ti"]
    job_count = ti.xcom_pull(task_ids="export_csv", key="job_count") or 0
    csv_filepath = ti.xcom_pull(task_ids="export_csv", key="csv_filepath") or "Unknown"
    role_counts = ti.xcom_pull(task_ids="export_csv", key="role_counts") or {}
    
    print(f"Sending notification for {job_count} jobs...")
    
    # Pass role breakdown to notification
    success = send_notification(job_count, csv_filepath, role_counts)
    
    if success:
        print("Notification sent successfully!")
    else:
        print("Warning: Failed to send notification")
    
    return success


# =============================================================================
# DAG Definition
# =============================================================================

# Use PST timezone
local_tz = pendulum.timezone(SCHEDULE_TIMEZONE)

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="Scrapes Data Engineer, Analytics Engineer, and Data Scientist jobs every 6 hours starting at 6AM PST",
    schedule_interval=SCHEDULE_INTERVAL,
    start_date=datetime(2024, 1, 1, tzinfo=local_tz),
    catchup=False,
    tags=["jobs", "multi-source", "data-engineer", "analytics-engineer", "data-scientist", "scraper"],
    doc_md="""
    ## Multi-Source Job Scraper DAG
    
    This DAG automatically scrapes job listings from multiple sources:
    - **JSearch API** (LinkedIn, Indeed, Glassdoor, ZipRecruiter)
    - **Adzuna API** (Monster, CareerBuilder, SimplyHired)
    - **RemoteOK** (Remote-focused jobs)
    
    ### Job Titles Searched
    - Data Engineer
    - Analytics Engineer
    - Data Scientist (with ETL skills)
    
    ### Schedule
    Runs every 6 hours starting at 6AM PST:
    - 6:00 AM PST
    - 12:00 PM PST
    - 6:00 PM PST
    - 12:00 AM PST
    
    ### Tasks
    1. **scrape_jobs**: Fetches jobs from all sources
    2. **export_csv**: Saves jobs to timestamped CSV file
    3. **send_notification**: Sends email alert via AWS SNS
    
    ### Filters
    - Location: United States
    - Experience: 3-7 years
    - Data Scientists: Must have ETL/pipeline skills
    
    ### Configuration
    See `config/config.py` and `.env` for settings.
    """,
) as dag:
    
    # Task 1: Scrape jobs from all sources
    scrape_jobs = PythonOperator(
        task_id="scrape_jobs",
        python_callable=scrape_jobs_task,
        provide_context=True,
    )
    
    # Task 2: Export to CSV
    export_csv = PythonOperator(
        task_id="export_csv",
        python_callable=export_csv_task,
        provide_context=True,
    )
    
    # Task 3: Send notification
    send_notification = PythonOperator(
        task_id="send_notification",
        python_callable=send_notification_task,
        provide_context=True,
    )
    
    # Define task dependencies
    scrape_jobs >> export_csv >> send_notification
