"""
LinkedIn Job Scraper DAG

Automated pipeline that runs every 6 hours to:
1. Scrape Data Engineer jobs from job boards
2. Filter for positions requiring 3-7 years of experience
3. Export results to CSV
4. Send email notification via AWS SNS
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import sys
import os

# Add plugins directory to path
plugins_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
sys.path.insert(0, plugins_path)

# Add config directory to path
config_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, config_path)

from config.config import (
    DAG_ID,
    SCHEDULE_INTERVAL,
    DAG_OWNER,
    DAG_RETRIES,
    DAG_RETRY_DELAY_MINUTES
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
    Task to scrape job listings from the API.
    Pushes the list of jobs to XCom for the next task.
    """
    from job_scraper import scrape_jobs
    
    print("Starting job scraping...")
    jobs = scrape_jobs()
    
    # Push jobs to XCom
    context["ti"].xcom_push(key="jobs", value=jobs)
    
    print(f"Scraped {len(jobs)} jobs successfully")
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
    
    print(f"Sending notification for {job_count} jobs...")
    success = send_notification(job_count, csv_filepath)
    
    if success:
        print("Notification sent successfully!")
    else:
        print("Warning: Failed to send notification")
    
    return success


# =============================================================================
# DAG Definition
# =============================================================================

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="Scrapes Data Engineer jobs every 6 hours and sends email notifications",
    schedule_interval=SCHEDULE_INTERVAL,
    start_date=days_ago(1),
    catchup=False,
    tags=["jobs", "linkedin", "data-engineer", "scraper"],
    doc_md="""
    ## LinkedIn Job Scraper DAG
    
    This DAG automatically scrapes job listings for Data Engineer positions
    in the United States, filters for 3-7 years of experience, saves results
    to CSV, and sends email notifications via AWS SNS.
    
    ### Schedule
    Runs every 6 hours (0 */6 * * *)
    
    ### Tasks
    1. **scrape_jobs**: Fetches jobs from JSearch API
    2. **export_csv**: Saves jobs to timestamped CSV file
    3. **send_notification**: Sends email alert via AWS SNS
    
    ### Configuration
    See `config/config.py` and `.env` for settings.
    """,
) as dag:
    
    # Task 1: Scrape jobs
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
