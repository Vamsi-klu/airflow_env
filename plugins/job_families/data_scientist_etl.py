"""
Data Scientist (ETL Focus) Job Family Module

Handles scraping and filtering for Data Scientist positions
that require ETL and data engineering skills.
"""
from typing import List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from scrapers.jsearch_scraper import JSearchScraper
from scrapers.adzuna_scraper import AdzunaScraper
from scrapers.remoteok_scraper import RemoteOKScraper
from config.config import MAX_PAGES_PER_SOURCE, EXPERIENCE_MIN_YEARS, EXPERIENCE_MAX_YEARS, ETL_SKILLS


class DataScientistETLJobFamily:
    """Job family handler for Data Scientist positions requiring ETL skills."""
    
    JOB_TITLE = "Data Scientist"
    SEARCH_TERMS = [
        "Data Scientist",
        "Data Scientist ETL",
        "Data Scientist SQL",
        "Data Scientist Python",
        "Machine Learning Engineer",
    ]
    
    # ETL-focused skills required for Data Scientists
    REQUIRED_ETL_SKILLS = ETL_SKILLS
    MIN_SKILLS_REQUIRED = 2  # Must have at least 2 ETL skills
    
    def __init__(self):
        self.scrapers = [
            JSearchScraper(),
            AdzunaScraper(),
            RemoteOKScraper()
        ]
    
    def _has_etl_skills(self, description: str) -> bool:
        """Check if Data Scientist role requires ETL skills."""
        if not description:
            return False
        
        text = description.lower()
        skill_count = sum(1 for skill in self.REQUIRED_ETL_SKILLS if skill in text)
        return skill_count >= self.MIN_SKILLS_REQUIRED
    
    def scrape_jobs(self) -> List[Dict]:
        """
        Scrape Data Scientist jobs with ETL requirements from all sources.
        
        Returns:
            list: List of filtered and normalized job dictionaries
        """
        all_jobs = []
        seen_job_ids = set()
        
        print(f"\n{'=' * 50}")
        print(f"Scraping: {self.JOB_TITLE} (with ETL skills)")
        print(f"Required skills: {', '.join(self.REQUIRED_ETL_SKILLS[:5])}...")
        print(f"{'=' * 50}")
        
        for search_term in self.SEARCH_TERMS:
            for scraper in self.scrapers:
                print(f"\n[{scraper.source_name}] Searching for '{search_term}'...")
                
                for page in range(1, MAX_PAGES_PER_SOURCE + 1):
                    jobs = scraper.fetch_jobs(search_term, page)
                    
                    if not jobs:
                        break
                    
                    for job in jobs:
                        # Create unique ID
                        job_id = f"{scraper.source_name.split()[0].lower()}_{job['job_id']}"
                        
                        if job_id in seen_job_ids:
                            continue
                        seen_job_ids.add(job_id)
                        
                        description = job.get("description", "")
                        
                        # Apply experience filter
                        if not BaseScraper.is_experience_in_range(description, EXPERIENCE_MIN_YEARS, EXPERIENCE_MAX_YEARS):
                            continue
                        
                        # IMPORTANT: Filter for ETL skills
                        if not self._has_etl_skills(description):
                            continue
                        
                        # Normalize and add
                        job["job_id"] = job_id
                        normalized = BaseScraper.normalize_job_data(job, scraper.source_name)
                        normalized["job_family"] = f"{self.JOB_TITLE} (ETL)"
                        all_jobs.append(normalized)
        
        print(f"\nTotal {self.JOB_TITLE} (ETL) jobs: {len(all_jobs)}")
        return all_jobs


if __name__ == "__main__":
    family = DataScientistETLJobFamily()
    jobs = family.scrape_jobs()
    print(f"\nSample jobs:")
    for job in jobs[:3]:
        print(f"  - {job['title']} at {job['company']}")
