"""
Job Scraper Module

Fetches Data Engineer job listings from JSearch API (RapidAPI)
and filters for positions requiring 3-7 years of experience.
"""
import requests
import re
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import (
    RAPIDAPI_KEY,
    RAPIDAPI_HOST,
    JOB_SEARCH_QUERY,
    JOB_LOCATION,
    EXPERIENCE_MIN_YEARS,
    EXPERIENCE_MAX_YEARS,
    RESULTS_PER_PAGE,
    MAX_PAGES
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
    
    # Pattern: "3-7 years", "3 to 7 years", "3+ years"
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
                # For "X+ years" or single number, assume range up to years + 3
                return years, years + 3
    
    return None, None


def is_experience_in_range(job_description: str, min_years: int, max_years: int) -> bool:
    """
    Check if the job's experience requirement falls within the specified range.
    
    Args:
        job_description: The job description text
        min_years: Minimum years required
        max_years: Maximum years required
        
    Returns:
        bool: True if experience requirement is in range or not specified
    """
    req_min, req_max = extract_years_of_experience(job_description)
    
    # If no experience requirement found, include the job
    if req_min is None:
        return True
    
    # Check if there's any overlap between ranges
    return not (req_max < min_years or req_min > max_years)


def fetch_jobs_from_api(page: int = 1) -> list:
    """
    Fetch job listings from JSearch API.
    
    Args:
        page: Page number to fetch
        
    Returns:
        list: List of job dictionaries
    """
    url = "https://jsearch.p.rapidapi.com/search"
    
    querystring = {
        "query": f"{JOB_SEARCH_QUERY} in {JOB_LOCATION}",
        "page": str(page),
        "num_pages": "1",
        "date_posted": "week"  # Jobs posted in last week
    }
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching jobs from API: {e}")
        return []


def scrape_jobs() -> list:
    """
    Main function to scrape and filter job listings.
    
    Returns:
        list: List of filtered job dictionaries with relevant fields
    """
    all_jobs = []
    
    print(f"Searching for: {JOB_SEARCH_QUERY} in {JOB_LOCATION}")
    print(f"Experience filter: {EXPERIENCE_MIN_YEARS}-{EXPERIENCE_MAX_YEARS} years")
    
    for page in range(1, MAX_PAGES + 1):
        print(f"Fetching page {page}...")
        jobs = fetch_jobs_from_api(page)
        
        if not jobs:
            print(f"No more jobs found at page {page}")
            break
        
        for job in jobs:
            # Get job description for experience filtering
            description = job.get("job_description", "")
            
            # Check if experience requirement is in range
            if is_experience_in_range(description, EXPERIENCE_MIN_YEARS, EXPERIENCE_MAX_YEARS):
                filtered_job = {
                    "job_id": job.get("job_id", ""),
                    "title": job.get("job_title", ""),
                    "company": job.get("employer_name", ""),
                    "location": f"{job.get('job_city', '')}, {job.get('job_state', '')}",
                    "job_type": job.get("job_employment_type", ""),
                    "posted_date": job.get("job_posted_at_datetime_utc", ""),
                    "apply_link": job.get("job_apply_link", ""),
                    "description_snippet": description[:500] + "..." if len(description) > 500 else description,
                    "salary_min": job.get("job_min_salary", ""),
                    "salary_max": job.get("job_max_salary", ""),
                    "salary_currency": job.get("job_salary_currency", "USD"),
                    "experience_required": f"{EXPERIENCE_MIN_YEARS}-{EXPERIENCE_MAX_YEARS} years",
                    "source": "JSearch API (LinkedIn + others)"
                }
                all_jobs.append(filtered_job)
    
    print(f"Total jobs found after filtering: {len(all_jobs)}")
    return all_jobs


if __name__ == "__main__":
    # Test the scraper
    jobs = scrape_jobs()
    for job in jobs[:3]:  # Print first 3 jobs
        print(f"\n{job['title']} at {job['company']}")
        print(f"Location: {job['location']}")
        print(f"Apply: {job['apply_link']}")
