"""
Job Scraper Orchestrator

Coordinates scraping across all job families and scrapers.
Uses the modular scraper and job family structure.
"""
import sys
import os
from typing import List, Dict
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_families.data_engineer import DataEngineerJobFamily
from job_families.analytics_engineer import AnalyticsEngineerJobFamily
from job_families.data_scientist_etl import DataScientistETLJobFamily


def scrape_all_jobs() -> List[Dict]:
    """
    Main orchestrator function to scrape jobs from all families and sources.
    
    Returns:
        list: Combined list of all job dictionaries
    """
    all_jobs = []
    seen_job_ids = set()
    
    print(f"\n{'=' * 60}")
    print(f"🚀 Multi-Source Job Scraper - Orchestrator")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")
    
    # Initialize all job families
    job_families = [
        DataEngineerJobFamily(),
        AnalyticsEngineerJobFamily(),
        DataScientistETLJobFamily(),
    ]
    
    # Scrape from each family
    for family in job_families:
        print(f"\n{'─' * 60}")
        jobs = family.scrape_jobs()
        
        for job in jobs:
            if job['job_id'] not in seen_job_ids:
                seen_job_ids.add(job['job_id'])
                all_jobs.append(job)
    
    # Print summary
    print(f"\n{'=' * 60}")
    print(f"📊 FINAL SUMMARY")
    print(f"{'=' * 60}")
    
    # By job family
    family_counts = {}
    for job in all_jobs:
        family = job.get('job_family', 'Unknown')
        family_counts[family] = family_counts.get(family, 0) + 1
    
    print(f"\nBy Job Family:")
    for family, count in family_counts.items():
        print(f"  • {family}: {count}")
    
    # By source
    source_counts = {}
    for job in all_jobs:
        source = job.get('source', 'Unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    print(f"\nBy Source:")
    for source, count in source_counts.items():
        print(f"  • {source}: {count}")
    
    print(f"\n✅ TOTAL JOBS: {len(all_jobs)}")
    print(f"{'=' * 60}\n")
    
    return all_jobs


# Alias for backward compatibility with DAG
scrape_jobs = scrape_all_jobs


if __name__ == "__main__":
    jobs = scrape_all_jobs()
    
    print("\nSample jobs from each family:")
    shown_families = set()
    for job in jobs:
        family = job.get('job_family', 'Unknown')
        if family not in shown_families:
            shown_families.add(family)
            print(f"\n[{family}]")
            print(f"  {job['title']} at {job['company']}")
            print(f"  Location: {job['location']}")
            print(f"  Source: {job['source']}")
