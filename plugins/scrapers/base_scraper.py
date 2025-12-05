"""
Base Scraper Module

Abstract base class and common utilities for all job scrapers.
"""
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import EXPERIENCE_MIN_YEARS, EXPERIENCE_MAX_YEARS, ETL_SKILLS


class BaseScraper(ABC):
    """Abstract base class for job scrapers."""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
    
    @abstractmethod
    def fetch_jobs(self, job_title: str, page: int = 1) -> List[Dict]:
        """Fetch jobs from the source. Must be implemented by subclasses."""
        pass
    
    @staticmethod
    def extract_years_of_experience(text: str) -> tuple:
        """Extract years of experience requirements from text."""
        if not text:
            return None, None
        
        text = text.lower()
        
        patterns = [
            r'(\d+)\s*[-–to]+\s*(\d+)\s*(?:\+)?\s*years?\s*(?:of)?\s*(?:experience|exp)?',
            r'(\d+)\s*\+\s*years?\s*(?:of)?\s*(?:experience|exp)?',
            r'(\d+)\s*years?\s*(?:of)?\s*(?:experience|exp)?',
            r'minimum\s*(?:of)?\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups) == 2 and groups[1]:
                    return int(groups[0]), int(groups[1])
                elif groups[0]:
                    years = int(groups[0])
                    return years, years + 3
        
        return None, None
    
    @staticmethod
    def is_experience_in_range(description: str, min_years: int = EXPERIENCE_MIN_YEARS, 
                                max_years: int = EXPERIENCE_MAX_YEARS) -> bool:
        """Check if experience requirement is in range."""
        req_min, req_max = BaseScraper.extract_years_of_experience(description)
        
        if req_min is None:
            return True
        
        return not (req_max < min_years or req_min > max_years)
    
    @staticmethod
    def has_etl_skills(text: str) -> bool:
        """Check if description mentions ETL-related skills."""
        if not text:
            return False
        
        text = text.lower()
        skill_count = sum(1 for skill in ETL_SKILLS if skill in text)
        return skill_count >= 2
    
    @staticmethod
    def normalize_job_data(job: Dict, source: str) -> Dict:
        """Normalize job data to common format."""
        return {
            "job_id": job.get("job_id", ""),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "job_type": job.get("job_type", "Full-time"),
            "remote": job.get("remote", False),
            "posted_date": job.get("posted_date", ""),
            "apply_link": job.get("apply_link", ""),
            "description_snippet": job.get("description", "")[:500] + "..." if len(job.get("description", "")) > 500 else job.get("description", ""),
            "salary_min": job.get("salary_min", ""),
            "salary_max": job.get("salary_max", ""),
            "salary_currency": job.get("salary_currency", "USD"),
            "experience_required": f"{EXPERIENCE_MIN_YEARS}-{EXPERIENCE_MAX_YEARS} years",
            "source": source,
            "scraped_at": datetime.now().isoformat()
        }
