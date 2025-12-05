"""
CSV Exporter Module

Exports job listings to timestamped CSV files.
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
    
    if not jobs:
        print("No jobs to export, creating empty CSV with headers")
        # Create empty DataFrame with expected columns
        df = pd.DataFrame(columns=[
            "job_id", "title", "company", "location", "job_type",
            "posted_date", "apply_link", "description_snippet",
            "salary_min", "salary_max", "salary_currency",
            "experience_required", "source"
        ])
    else:
        df = pd.DataFrame(jobs)
    
    # Define column order
    columns = [
        "job_id", "title", "company", "location", "job_type",
        "posted_date", "apply_link", "description_snippet",
        "salary_min", "salary_max", "salary_currency",
        "experience_required", "source"
    ]
    
    # Reorder columns (only include columns that exist)
    existing_columns = [col for col in columns if col in df.columns]
    df = df[existing_columns]
    
    # Export to CSV
    df.to_csv(filepath, index=False, encoding="utf-8")
    
    print(f"Exported {len(jobs)} jobs to: {filepath}")
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
    # Test the exporter
    test_jobs = [
        {
            "job_id": "test123",
            "title": "Senior Data Engineer",
            "company": "Test Corp",
            "location": "San Francisco, CA",
            "job_type": "Full-time",
            "posted_date": "2024-01-15",
            "apply_link": "https://example.com/apply",
            "description_snippet": "We are looking for a Data Engineer...",
            "salary_min": 120000,
            "salary_max": 180000,
            "salary_currency": "USD",
            "experience_required": "3-7 years",
            "source": "Test"
        }
    ]
    
    filepath = export_to_csv(test_jobs)
    print(f"Test CSV created at: {filepath}")
