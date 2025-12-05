"""
JSearch Scraper Module

Fetches jobs from JSearch API (LinkedIn, Indeed, Glassdoor, ZipRecruiter).
"""
import requests
from typing import List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import RAPIDAPI_KEY, JSEARCH_HOST, JOB_LOCATION
from scrapers.base_scraper import BaseScraper


class JSearchScraper(BaseScraper):
    """Scraper for JSearch API (LinkedIn, Indeed, Glassdoor, ZipRecruiter)."""
    
    def __init__(self):
        super().__init__("JSearch (LinkedIn/Indeed/Glassdoor)")
    
    def fetch_jobs(self, job_title: str, page: int = 1) -> List[Dict]:
        """Fetch jobs from JSearch API."""
        if not RAPIDAPI_KEY:
            print("Warning: RAPIDAPI_KEY not configured, skipping JSearch")
            return []
        
        url = "https://jsearch.p.rapidapi.com/search"
        
        querystring = {
            "query": f"{job_title} in {JOB_LOCATION}",
            "page": str(page),
            "num_pages": "1",
            "date_posted": "week"
        }
        
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": JSEARCH_HOST
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job in data.get("data", []):
                jobs.append({
                    "job_id": job.get("job_id", ""),
                    "title": job.get("job_title", ""),
                    "company": job.get("employer_name", ""),
                    "location": f"{job.get('job_city', '')}, {job.get('job_state', '')}",
                    "job_type": job.get("job_employment_type", ""),
                    "remote": job.get("job_is_remote", False),
                    "posted_date": job.get("job_posted_at_datetime_utc", ""),
                    "apply_link": job.get("job_apply_link", ""),
                    "description": job.get("job_description", ""),
                    "salary_min": job.get("job_min_salary", ""),
                    "salary_max": job.get("job_max_salary", ""),
                    "salary_currency": job.get("job_salary_currency", "USD"),
                })
            return jobs
        except Exception as e:
            print(f"Error fetching from JSearch: {e}")
            return []


if __name__ == "__main__":
    scraper = JSearchScraper()
    jobs = scraper.fetch_jobs("Data Engineer", page=1)
    print(f"Found {len(jobs)} jobs from JSearch")
    for job in jobs[:3]:
        print(f"  - {job['title']} at {job['company']}")
