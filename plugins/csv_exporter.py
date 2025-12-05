"""
CSV Exporter Module

Exports job listings to timestamped CSV files with enhanced columns
for multi-source job data.
"""
import os
import pandas as pd
from datetime import datetime
import sys

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import OUTPUT_DIR, CSV_FILENAME_PREFIX


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")


def export_to_csv(jobs: list) -> str:
    """
    Export job listings to a CSV file.
    
    Args:
        jobs: List of job dictionaries
        
    Returns:
        str: Path to the created CSV file
    """
    ensure_output_dir()
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{CSV_FILENAME_PREFIX}_{timestamp}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Define column order for multi-source data
    columns = [
        "job_id",
        "title", 
        "company",
        "location",
        "remote",
        "job_type",
        "posted_date",
        "apply_link",
        "salary_min",
        "salary_max",
        "salary_currency",
        "experience_required",
        "source",
        "scraped_at",
        "description_snippet"
    ]
    
    if not jobs:
        print("No jobs to export, creating empty CSV with headers")
        df = pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(jobs)
        
        # Reorder columns (only include columns that exist)
        existing_columns = [col for col in columns if col in df.columns]
        df = df[existing_columns]
    
    # Export to CSV
    df.to_csv(filepath, index=False, encoding="utf-8")
    
    # Print summary
    print(f"\n{'=' * 50}")
    print(f"CSV Export Summary")
    print(f"{'=' * 50}")
    print(f"Total jobs exported: {len(jobs)}")
    print(f"File: {filepath}")
    
    if jobs:
        # Summary by source
        source_counts = df['source'].value_counts().to_dict() if 'source' in df.columns else {}
        print(f"\nBy Source:")
        for source, count in source_counts.items():
            print(f"  - {source}: {count}")
        
        # Summary by remote status
        if 'remote' in df.columns:
            remote_count = df['remote'].sum()
            print(f"\nRemote jobs: {remote_count} ({remote_count/len(jobs)*100:.1f}%)")
    
    print(f"{'=' * 50}\n")
    
    return filepath


def get_latest_csv() -> str:
    """
    Get the path to the most recently created CSV file.
    
    Returns:
        str: Path to the latest CSV file, or None if no files exist
    """
    ensure_output_dir()
    
    csv_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".csv")]
    
    if not csv_files:
        return None
    
    # Sort by modification time, get most recent
    csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
    
    return os.path.join(OUTPUT_DIR, csv_files[0])


if __name__ == "__main__":
    # Test the exporter with multi-source data
    test_jobs = [
        {
            "job_id": "jsearch_123",
            "title": "Senior Data Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "remote": False,
            "job_type": "Full-time",
            "posted_date": "2024-01-15",
            "apply_link": "https://example.com/apply1",
            "description_snippet": "We are looking for a Data Engineer with ETL experience...",
            "salary_min": 150000,
            "salary_max": 200000,
            "salary_currency": "USD",
            "experience_required": "3-7 years",
            "source": "JSearch (LinkedIn/Indeed)",
            "scraped_at": datetime.now().isoformat()
        },
        {
            "job_id": "adzuna_456",
            "title": "Analytics Engineer",
            "company": "Data Inc",
            "location": "New York, NY",
            "remote": True,
            "job_type": "Full-time",
            "posted_date": "2024-01-14",
            "apply_link": "https://example.com/apply2",
            "description_snippet": "Join our team as an Analytics Engineer...",
            "salary_min": 130000,
            "salary_max": 170000,
            "salary_currency": "USD",
            "experience_required": "3-7 years",
            "source": "Adzuna (Monster/CareerBuilder)",
            "scraped_at": datetime.now().isoformat()
        },
        {
            "job_id": "remoteok_789",
            "title": "Data Scientist - ETL Focus",
            "company": "Remote First Co",
            "location": "Remote - Worldwide",
            "remote": True,
            "job_type": "Full-time",
            "posted_date": "2024-01-13",
            "apply_link": "https://example.com/apply3",
            "description_snippet": "Data Scientist with strong SQL and Python skills...",
            "salary_min": 140000,
            "salary_max": 180000,
            "salary_currency": "USD",
            "experience_required": "3-7 years",
            "source": "RemoteOK (Remote Jobs)",
            "scraped_at": datetime.now().isoformat()
        }
    ]
    
    filepath = export_to_csv(test_jobs)
    print(f"Test CSV created at: {filepath}")
