"""
Analytics Engineer Job Family Module

Handles scraping and filtering for Analytics Engineer positions.
"""
from typing import List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from scrapers.jsearch_scraper import JSearchScraper
from scrapers.adzuna_scraper import AdzunaScraper
from scrapers.remoteok_scraper import RemoteOKScraper
from config.config import MAX_PAGES_PER_SOURCE, EXPERIENCE_MIN_YEARS, EXPERIENCE_MAX_YEARS


class AnalyticsEngineerJobFamily:
    """Job family handler for Analytics Engineer positions."""
    
    JOB_TITLE = "Analytics Engineer"
    SEARCH_TERMS = [
        "Analytics Engineer",
        "Senior Analytics Engineer",
        "Lead Analytics Engineer",
        "BI Engineer",
    ]
    
    # Skills specific to Analytics Engineers
    REQUIRED_SKILLS = [
        "sql", "dbt", "looker", "tableau", "power bi",
        "snowflake", "bigquery", "redshift", "data modeling",
        "python", "git", "airflow", "fivetran"
    ]
    
    def __init__(self):
        self.scrapers = [
            JSearchScraper(),
            AdzunaScraper(),
            RemoteOKScraper()
        ]
    
    def scrape_jobs(self) -> List[Dict]:
        """
        Scrape Analytics Engineer jobs from all sources.
        
        Returns:
            list: List of filtered and normalized job dictionaries
        """
        all_jobs = []
        seen_job_ids = set()
        
        print(f"\n{'=' * 50}")
        print(f"Scraping: {self.JOB_TITLE}")
        print(f"{'=' * 50}")
        
        for scraper in self.scrapers:
            print(f"\n[{scraper.source_name}] Searching for {self.JOB_TITLE}...")
            
            for page in range(1, MAX_PAGES_PER_SOURCE + 1):
                jobs = scraper.fetch_jobs(self.JOB_TITLE, page)
                
                if not jobs:
                    break
                
                for job in jobs:
                    # Create unique ID
                    job_id = f"{scraper.source_name.split()[0].lower()}_{job['job_id']}"
                    
                    if job_id in seen_job_ids:
                        continue
                    seen_job_ids.add(job_id)
                    
                    # Apply experience filter
                    description = job.get("description", "")
                    if not BaseScraper.is_experience_in_range(description, EXPERIENCE_MIN_YEARS, EXPERIENCE_MAX_YEARS):
                        continue
                    
                    # Normalize and add
                    job["job_id"] = job_id
                    normalized = BaseScraper.normalize_job_data(job, scraper.source_name)
                    normalized["job_family"] = self.JOB_TITLE
                    all_jobs.append(normalized)
            
            print(f"    Found {len([j for j in all_jobs if scraper.source_name in j['source']])} jobs")
        
        print(f"\nTotal {self.JOB_TITLE} jobs: {len(all_jobs)}")
        return all_jobs


if __name__ == "__main__":
    family = AnalyticsEngineerJobFamily()
    jobs = family.scrape_jobs()
    print(f"\nSample jobs:")
    for job in jobs[:3]:
        print(f"  - {job['title']} at {job['company']}")
