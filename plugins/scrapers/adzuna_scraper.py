"""
Adzuna Scraper Module

Fetches jobs from Adzuna API (Monster, CareerBuilder, SimplyHired).
"""
import requests
from typing import List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import ADZUNA_APP_ID, ADZUNA_APP_KEY, JOB_LOCATION, JOB_COUNTRY_CODE, RESULTS_PER_PAGE
from scrapers.base_scraper import BaseScraper


class AdzunaScraper(BaseScraper):
    """Scraper for Adzuna API (Monster, CareerBuilder, SimplyHired)."""
    
    def __init__(self):
        super().__init__("Adzuna (Monster/CareerBuilder)")
    
    def fetch_jobs(self, job_title: str, page: int = 1) -> List[Dict]:
        """Fetch jobs from Adzuna API."""
        if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
            print("Warning: Adzuna API keys not configured, skipping Adzuna")
            return []
        
        url = f"https://api.adzuna.com/v1/api/jobs/{JOB_COUNTRY_CODE}/search/{page}"
        
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "what": job_title,
            "where": JOB_LOCATION,
            "results_per_page": RESULTS_PER_PAGE,
            "max_days_old": 7,
            "sort_by": "date"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job in data.get("results", []):
                location = job.get("location", {})
                location_str = ", ".join(location.get("display_name", "").split(", ")[:2])
                
                jobs.append({
                    "job_id": str(job.get("id", "")),
                    "title": job.get("title", ""),
                    "company": job.get("company", {}).get("display_name", ""),
                    "location": location_str,
                    "job_type": job.get("contract_type", "Full-time"),
                    "remote": "remote" in job.get("title", "").lower() or "remote" in job.get("description", "").lower(),
                    "posted_date": job.get("created", ""),
                    "apply_link": job.get("redirect_url", ""),
                    "description": job.get("description", ""),
                    "salary_min": job.get("salary_min", ""),
                    "salary_max": job.get("salary_max", ""),
                    "salary_currency": "USD",
                })
            return jobs
        except Exception as e:
            print(f"Error fetching from Adzuna: {e}")
            return []


if __name__ == "__main__":
    scraper = AdzunaScraper()
    jobs = scraper.fetch_jobs("Data Engineer", page=1)
    print(f"Found {len(jobs)} jobs from Adzuna")
    for job in jobs[:3]:
        print(f"  - {job['title']} at {job['company']}")
