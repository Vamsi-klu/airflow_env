# Multi-Source Job Scraper with Airflow

An automated pipeline that scrapes Data Engineer, Analytics Engineer, and Data Scientist job listings every 6 hours from multiple job boards and sends email notifications via AWS SNS.

## 🚀 Features

- **Multi-Source Scraping**: JSearch (LinkedIn/Indeed), Adzuna (Monster/CareerBuilder), RemoteOK
- **Multiple Job Families**: Data Engineer, Analytics Engineer, Data Scientist (ETL focus)
- **Smart Filtering**: 3-7 years experience, ETL skills for Data Scientists
- **PST Scheduling**: Runs at 6AM, 12PM, 6PM, 12AM Pacific Time
- **Email Alerts**: AWS SNS notifications with job breakdown
- **Modular Architecture**: Separate files for each scraper and job family

## 📁 Project Structure

```
airflow_env/
├── dags/
│   └── linkedin_job_scraper_dag.py    # Airflow DAG
├── plugins/
│   ├── scrapers/                      # Platform-specific scrapers
│   │   ├── base_scraper.py           # Abstract base class + utilities
│   │   ├── jsearch_scraper.py        # LinkedIn, Indeed, Glassdoor, ZipRecruiter
│   │   ├── adzuna_scraper.py         # Monster, CareerBuilder, SimplyHired
│   │   └── remoteok_scraper.py       # Remote-focused jobs (no API key)
│   ├── job_families/                  # Job type handlers
│   │   ├── data_engineer.py          # Data Engineer positions
│   │   ├── analytics_engineer.py     # Analytics Engineer positions
│   │   └── data_scientist_etl.py     # Data Scientist (ETL skills required)
│   ├── job_scraper.py                # Orchestrator
│   ├── csv_exporter.py               # CSV generation
│   └── sns_notifier.py               # AWS SNS notifications
├── config/
│   └── config.py                     # Configuration settings
├── output/                           # CSV output directory
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:job-alerts
RAPIDAPI_KEY=your_rapidapi_key

# Optional (for additional sources)
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
REMOTEOK_ENABLED=true
```

### 3. Get API Keys

| Source | URL | Free Tier |
|--------|-----|-----------|
| JSearch | [rapidapi.com/jsearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) | 500 req/month |
| Adzuna | [developer.adzuna.com](https://developer.adzuna.com/) | 200 req/month |
| RemoteOK | No key needed | Unlimited |

### 4. Set Up AWS SNS

```bash
# Create topic
aws sns create-topic --name job-alerts

# Subscribe your email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:job-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

Check your email and confirm the subscription.

### 5. Start Airflow

```bash
export AIRFLOW_HOME=$(pwd)
airflow db init
airflow users create --username admin --password admin --role Admin --email admin@example.com --firstname Admin --lastname User
airflow scheduler &
airflow webserver --port 8080
```

## 📊 Job Sources

| Source | Platforms Covered |
|--------|-------------------|
| **JSearch** | LinkedIn, Indeed, Glassdoor, ZipRecruiter |
| **Adzuna** | Monster, CareerBuilder, SimplyHired |
| **RemoteOK** | Remote-focused positions |

## 🎯 Job Families

| Family | Description | Special Filtering |
|--------|-------------|-------------------|
| **Data Engineer** | ETL, pipelines, data infrastructure | Experience 3-7 years |
| **Analytics Engineer** | dbt, Looker, data modeling | Experience 3-7 years |
| **Data Scientist (ETL)** | ML + data engineering | Must have 2+ ETL skills |

## ⏰ Schedule

The DAG runs every 6 hours in Pacific Time:

| Time (PST) | Time (UTC) |
|------------|------------|
| 6:00 AM | 2:00 PM |
| 12:00 PM | 8:00 PM |
| 6:00 PM | 2:00 AM |
| 12:00 AM | 8:00 AM |

## 📧 Email Notification Sample

```
📊 Multi-Source Job Scraper Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕐 Scan Time: 2024-01-15 06:00:00 PST
📍 Location: United States

✅ Total Jobs Found: 85

📊 By Role:
   • Data Engineer: 40
   • Analytics Engineer: 25
   • Data Scientist (ETL): 20
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🧪 Testing

```bash
# Test all imports
python -c "from plugins.job_scraper import scrape_all_jobs; print('OK')"

# Test individual scraper
python plugins/scrapers/jsearch_scraper.py

# Test job family
python plugins/job_families/data_engineer.py

# Test CSV export
python plugins/csv_exporter.py
```

## 🔧 Adding New Scrapers

Create a new file in `plugins/scrapers/`:

```python
from scrapers.base_scraper import BaseScraper

class NewPlatformScraper(BaseScraper):
    def __init__(self):
        super().__init__("New Platform")
    
    def fetch_jobs(self, job_title: str, page: int = 1):
        # Implement API call
        pass
```

## 🔧 Adding New Job Families

Create a new file in `plugins/job_families/`:

```python
from scrapers.base_scraper import BaseScraper
from scrapers.jsearch_scraper import JSearchScraper

class NewJobFamily:
    JOB_TITLE = "MLOps Engineer"
    
    def scrape_jobs(self):
        # Implement scraping logic
        pass
```

## 📝 License

MIT License - feel free to use and modify as needed.
