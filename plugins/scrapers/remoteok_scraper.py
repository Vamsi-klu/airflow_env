"""
RemoteOK Scraper Module

Fetches remote jobs from RemoteOK API (no API key required).
"""
import requests
from typing import List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import REMOTEOK_ENABLED
from scrapers.base_scraper import BaseScraper


class RemoteOKScraper(BaseScraper):
    """Scraper for RemoteOK API (Remote-focused jobs, no API key needed)."""
    
    def __init__(self):
        super().__init__("RemoteOK (Remote Jobs)")
    
    def fetch_jobs(self, job_title: str = None, page: int = 1) -> List[Dict]:
        """
        Fetch remote data jobs from RemoteOK API.
        Note: RemoteOK doesn't support pagination or specific search,
        so we fetch all and filter.
        """
        if not REMOTEOK_ENABLED:
            return []
        
        url = "https://remoteok.com/api"
        
        headers = {
            "User-Agent": "JobScraper/1.0"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            # Skip first item (it's metadata)
            for job in data[1:]:
                title = job.get("position", "").lower()
                tags = " ".join(job.get("tags", [])).lower()
                
                # Filter for relevant job titles
                is_relevant = any(
                    keyword in title or keyword in tags
                    for keyword in ["data engineer", "analytics engineer", "data scientist", "etl", "data pipeline"]
                )
                
                if is_relevant:
                    jobs.append({
                        "job_id": str(job.get("id", "")),
                        "title": job.get("position", ""),
                        "company": job.get("company", ""),
                        "location": "Remote - " + job.get("location", "Worldwide"),
                        "job_type": "Full-time",
                        "remote": True,
                        "posted_date": job.get("date", ""),
                        "apply_link": job.get("url", ""),
                        "description": job.get("description", ""),
                        "salary_min": job.get("salary_min", ""),
                        "salary_max": job.get("salary_max", ""),
                        "salary_currency": "USD",
                    })
            return jobs
        except Exception as e:
            print(f"Error fetching from RemoteOK: {e}")
            return []


if __name__ == "__main__":
    scraper = RemoteOKScraper()
    jobs = scraper.fetch_jobs()
    print(f"Found {len(jobs)} remote data jobs from RemoteOK")
    for job in jobs[:3]:
        print(f"  - {job['title']} at {job['company']}")
