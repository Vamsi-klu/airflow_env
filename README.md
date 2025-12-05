# LinkedIn Job Scraper with Airflow

An automated pipeline that scrapes Data Engineer job listings every 6 hours and sends email notifications via AWS SNS.

## 🚀 Features

- **Automated Scheduling**: Runs every 6 hours using Apache Airflow
- **Smart Filtering**: Filters jobs for 3-7 years of experience
- **CSV Export**: Saves timestamped job listings to CSV files
- **Email Alerts**: Sends notifications via AWS SNS when new jobs are found

## 📁 Project Structure

```
airflow_env/
├── dags/
│   └── linkedin_job_scraper_dag.py    # Main Airflow DAG
├── plugins/
│   ├── job_scraper.py                 # Job scraping logic
│   ├── csv_exporter.py                # CSV generation
│   └── sns_notifier.py                # AWS SNS notifications
├── config/
│   └── config.py                      # Configuration settings
├── output/                            # CSV output directory
├── requirements.txt                   # Python dependencies
├── .env.example                       # Example environment variables
└── README.md                          # This file
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:job-alerts

# RapidAPI Configuration
RAPIDAPI_KEY=your_rapidapi_key
```

### 3. Get RapidAPI Key

1. Go to [JSearch API on RapidAPI](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
2. Sign up for a free account
3. Subscribe to the free tier
4. Copy your API key to `.env`

### 4. Set Up AWS SNS

1. **Create SNS Topic**:
   ```bash
   aws sns create-topic --name job-alerts
   ```

2. **Subscribe Your Email**:
   ```bash
   aws sns subscribe \
     --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:job-alerts \
     --protocol email \
     --notification-endpoint your-email@example.com
   ```

3. **Confirm Subscription**: Check your email and click the confirmation link

### 5. Initialize Airflow

```bash
# Set Airflow home
export AIRFLOW_HOME=$(pwd)

# Initialize database
airflow db init

# Create admin user
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin
```

### 6. Start Airflow

```bash
# Start the scheduler (in one terminal)
airflow scheduler

# Start the web server (in another terminal)
airflow webserver --port 8080
```

Visit `http://localhost:8080` to access the Airflow UI.

## 📊 Usage

### Run Manually

Trigger the DAG manually via Airflow UI or CLI:

```bash
airflow dags trigger linkedin_job_scraper
```

### Test Individual Components

```bash
# Test job scraper
python plugins/job_scraper.py

# Test CSV exporter
python plugins/csv_exporter.py

# Test SNS notifier (requires AWS config)
python plugins/sns_notifier.py
```

## ⚙️ Configuration

Edit `config/config.py` to modify:

| Setting | Default | Description |
|---------|---------|-------------|
| `JOB_SEARCH_QUERY` | "Data Engineer" | Job title to search |
| `JOB_LOCATION` | "United States" | Location filter |
| `EXPERIENCE_MIN_YEARS` | 3 | Minimum years of experience |
| `EXPERIENCE_MAX_YEARS` | 7 | Maximum years of experience |
| `SCHEDULE_INTERVAL` | "0 */6 * * *" | Cron expression for scheduling |
| `MAX_PAGES` | 5 | Maximum pages to fetch |

## 📧 Email Notification Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 LinkedIn Job Scraper Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕐 Scan Time: 2024-01-15 12:00:00
🔍 Search Query: Data Engineer in United States
📋 Experience Filter: 3-7 years

✅ Total Jobs Found: 45
📁 CSV File: /path/to/output/data_engineer_jobs_20240115_120000.csv
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🔧 Troubleshooting

### DAG Not Appearing in Airflow

1. Check DAG syntax: `python dags/linkedin_job_scraper_dag.py`
2. Verify AIRFLOW_HOME is set correctly
3. Check Airflow logs: `airflow dags list`

### API Rate Limits

The free tier of JSearch API has rate limits. If you hit limits:
- Reduce `MAX_PAGES` in config
- Increase time between requests

### SNS Notifications Not Working

1. Verify AWS credentials in `.env`
2. Check SNS topic ARN is correct
3. Ensure email subscription is confirmed
4. Check CloudWatch logs for errors

## 📝 License

MIT License - feel free to use and modify as needed.
