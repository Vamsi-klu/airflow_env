"""
Multi-Source Job Scraper Module

Fetches job listings from multiple sources:
- JSearch API (LinkedIn, Indeed, Glassdoor, ZipRecruiter)
- Adzuna API (Monster, CareerBuilder, SimplyHired)
- RemoteOK (Remote-focused jobs)

Filters for Data Engineer, Analytics Engineer, and Data Scientist roles
requiring 3-7 years of experience with ETL skills.
"""
import requests
import re
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
import time

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import (
    RAPIDAPI_KEY,
    JSEARCH_HOST,
    ADZUNA_APP_ID,
    ADZUNA_APP_KEY,
    REMOTEOK_ENABLED,
    JOB_TITLES,
    JOB_LOCATION,
    JOB_COUNTRY_CODE,
    EXPERIENCE_MIN_YEARS,
    EXPERIENCE_MAX_YEARS,
    ETL_SKILLS,
    RESULTS_PER_PAGE,
    MAX_PAGES_PER_SOURCE
)


def extract_years_of_experience(text: str) -> tuple:
    """
    Extract years of experience requirements from job description text.
    
    Returns:
        tuple: (min_years, max_years) or (None, None) if not found
    """
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


def is_experience_in_range(job_description: str, min_years: int, max_years: int) -> bool:
    """Check if the job's experience requirement falls within the specified range."""
    req_min, req_max = extract_years_of_experience(job_description)
    
    if req_min is None:
        return True
    
    return not (req_max < min_years or req_min > max_years)


def has_etl_skills(text: str) -> bool:
    """Check if the job description mentions ETL-related skills."""
    if not text:
        return False
    
    text = text.lower()
    skill_count = sum(1 for skill in ETL_SKILLS if skill in text)
    
    # Require at least 2 ETL-related skills
    return skill_count >= 2


def normalize_job_data(job: Dict, source: str) -> Dict:
    """Normalize job data from different sources to a common format."""
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


# =============================================================================
# JSearch API (LinkedIn, Indeed, Glassdoor, ZipRecruiter)
# =============================================================================

def fetch_jobs_jsearch(job_title: str, page: int = 1) -> List[Dict]:
    """Fetch job listings from JSearch API."""
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


# =============================================================================
# Adzuna API (Monster, CareerBuilder, SimplyHired)
# =============================================================================

def fetch_jobs_adzuna(job_title: str, page: int = 1) -> List[Dict]:
    """Fetch job listings from Adzuna API."""
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
                "job_id": job.get("id", ""),
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


# =============================================================================
# RemoteOK API (Remote Jobs - No API Key Required)
# =============================================================================

def fetch_jobs_remoteok() -> List[Dict]:
    """Fetch job listings from RemoteOK API (free, no API key)."""
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


# =============================================================================
# Main Scraper Function
# =============================================================================

def scrape_all_jobs() -> List[Dict]:
    """
    Main function to scrape jobs from all sources for all job titles.
    
    Returns:
        list: List of filtered and normalized job dictionaries
    """
    all_jobs = []
    seen_job_ids = set()  # Deduplicate jobs
    
    print(f"=" * 60)
    print(f"Starting Multi-Source Job Scraper")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 60)
    print(f"Job Titles: {', '.join(JOB_TITLES)}")
    print(f"Location: {JOB_LOCATION}")
    print(f"Experience: {EXPERIENCE_MIN_YEARS}-{EXPERIENCE_MAX_YEARS} years")
    print(f"=" * 60)
    
    # Scrape from JSearch for each job title
    for job_title in JOB_TITLES:
        print(f"\n[JSearch] Searching for: {job_title}")
        for page in range(1, MAX_PAGES_PER_SOURCE + 1):
            jobs = fetch_jobs_jsearch(job_title, page)
            if not jobs:
                break
            
            for job in jobs:
                job_id = f"jsearch_{job['job_id']}"
                if job_id in seen_job_ids:
                    continue
                seen_job_ids.add(job_id)
                
                # Apply filters
                description = job.get("description", "")
                if not is_experience_in_range(description, EXPERIENCE_MIN_YEARS, EXPERIENCE_MAX_YEARS):
                    continue
                
                # For Data Scientist roles, require ETL skills
                if "scientist" in job_title.lower() and not has_etl_skills(description):
                    continue
                
                job["job_id"] = job_id
                all_jobs.append(normalize_job_data(job, "JSearch (LinkedIn/Indeed)"))
            
            time.sleep(0.5)  # Rate limiting
        print(f"    Found {len([j for j in all_jobs if 'JSearch' in j['source']])} jobs from JSearch")
    
    # Scrape from Adzuna for each job title
    for job_title in JOB_TITLES:
        print(f"\n[Adzuna] Searching for: {job_title}")
        for page in range(1, MAX_PAGES_PER_SOURCE + 1):
            jobs = fetch_jobs_adzuna(job_title, page)
            if not jobs:
                break
            
            for job in jobs:
                job_id = f"adzuna_{job['job_id']}"
                if job_id in seen_job_ids:
                    continue
                seen_job_ids.add(job_id)
                
                description = job.get("description", "")
                if not is_experience_in_range(description, EXPERIENCE_MIN_YEARS, EXPERIENCE_MAX_YEARS):
                    continue
                
                if "scientist" in job_title.lower() and not has_etl_skills(description):
                    continue
                
                job["job_id"] = job_id
                all_jobs.append(normalize_job_data(job, "Adzuna (Monster/CareerBuilder)"))
            
            time.sleep(0.5)
    adzuna_count = len([j for j in all_jobs if 'Adzuna' in j['source']])
    print(f"    Found {adzuna_count} jobs from Adzuna")
    
    # Scrape from RemoteOK
    print(f"\n[RemoteOK] Searching for remote data jobs...")
    remote_jobs = fetch_jobs_remoteok()
    for job in remote_jobs:
        job_id = f"remoteok_{job['job_id']}"
        if job_id in seen_job_ids:
            continue
        seen_job_ids.add(job_id)
        
        description = job.get("description", "")
        if not is_experience_in_range(description, EXPERIENCE_MIN_YEARS, EXPERIENCE_MAX_YEARS):
            continue
        
        job["job_id"] = job_id
        all_jobs.append(normalize_job_data(job, "RemoteOK (Remote Jobs)"))
    
    remoteok_count = len([j for j in all_jobs if 'RemoteOK' in j['source']])
    print(f"    Found {remoteok_count} jobs from RemoteOK")
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL JOBS FOUND: {len(all_jobs)}")
    print(f"{'=' * 60}")
    
    return all_jobs


# Alias for backward compatibility
scrape_jobs = scrape_all_jobs


if __name__ == "__main__":
    # Test the scraper
    jobs = scrape_all_jobs()
    
    print(f"\nSample jobs:")
    for job in jobs[:5]:
        print(f"\n{job['title']} at {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  Source: {job['source']}")
        print(f"  Apply: {job['apply_link']}")
