# Multi-Source Job Scraper - System Design

## High-Level Design (HLD)

### System Overview

```mermaid
graph TB
    subgraph "Scheduling Layer"
        A[Apache Airflow<br/>Scheduler]
    end
    
    subgraph "Orchestration Layer"
        B[DAG<br/>linkedin_job_scraper_dag.py]
    end
    
    subgraph "Data Collection Layer"
        C[Job Scraper<br/>Orchestrator]
        D[JSearch API<br/>LinkedIn/Indeed]
        E[Adzuna API<br/>Monster/CareerBuilder]
        F[RemoteOK API<br/>Remote Jobs]
    end
    
    subgraph "Processing Layer"
        G[Job Family Filters]
        H[CSV Exporter]
    end
    
    subgraph "Notification Layer"
        I[SNS Publisher]
        J[Email Inbox]
    end
    
    subgraph "Storage Layer"
        K[(CSV Files)]
    end
    
    A -->|"Every 6 hours PST"| B
    B --> C
    C --> D & E & F
    D & E & F --> G
    G --> H
    H --> K
    H --> I
    I --> J
```

### Component Responsibilities

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| **Scheduling** | Airflow | Triggers DAG at 6AM/12PM/6PM/12AM PST |
| **Orchestration** | DAG | Chains tasks: scrape → export → notify |
| **Collection** | Scrapers | Fetch raw job data from APIs |
| **Processing** | Job Families | Filter by role, experience, skills |
| **Storage** | CSV Exporter | Persist timestamped job listings |
| **Notification** | SNS Publisher | Send email alerts |

---

## Low-Level Design (LLD)

### Class Diagram

```mermaid
classDiagram
    class BaseScraper {
        <<abstract>>
        +source_name: str
        +fetch_jobs(job_title, page)*
        +extract_years_of_experience(text)$
        +is_experience_in_range(desc, min, max)$
        +has_etl_skills(text)$
        +normalize_job_data(job, source)$
    }
    
    class JSearchScraper {
        +fetch_jobs(job_title, page)
    }
    
    class AdzunaScraper {
        +fetch_jobs(job_title, page)
    }
    
    class RemoteOKScraper {
        +fetch_jobs(job_title, page)
    }
    
    class DataEngineerJobFamily {
        +JOB_TITLE: str
        +REQUIRED_SKILLS: list
        +scrapers: list
        +scrape_jobs()
    }
    
    class AnalyticsEngineerJobFamily {
        +JOB_TITLE: str
        +REQUIRED_SKILLS: list
        +scrapers: list
        +scrape_jobs()
    }
    
    class DataScientistETLJobFamily {
        +JOB_TITLE: str
        +REQUIRED_ETL_SKILLS: list
        +scrapers: list
        +scrape_jobs()
        -_has_etl_skills(desc)
    }
    
    BaseScraper <|-- JSearchScraper
    BaseScraper <|-- AdzunaScraper
    BaseScraper <|-- RemoteOKScraper
    
    DataEngineerJobFamily --> JSearchScraper
    DataEngineerJobFamily --> AdzunaScraper
    DataEngineerJobFamily --> RemoteOKScraper
    
    AnalyticsEngineerJobFamily --> JSearchScraper
    AnalyticsEngineerJobFamily --> AdzunaScraper
    AnalyticsEngineerJobFamily --> RemoteOKScraper
    
    DataScientistETLJobFamily --> JSearchScraper
    DataScientistETLJobFamily --> AdzunaScraper
    DataScientistETLJobFamily --> RemoteOKScraper
```

### Data Flow Sequence

```mermaid
sequenceDiagram
    participant AF as Airflow
    participant DAG as DAG
    participant ORC as Orchestrator
    participant FAM as Job Families
    participant SCR as Scrapers
    participant API as External APIs
    participant CSV as CSV Exporter
    participant SNS as SNS Notifier
    
    AF->>DAG: Trigger (cron: 0 6,12,18,0)
    DAG->>ORC: scrape_all_jobs()
    
    loop For each Job Family
        ORC->>FAM: family.scrape_jobs()
        
        loop For each Scraper
            FAM->>SCR: scraper.fetch_jobs(title, page)
            SCR->>API: HTTP GET
            API-->>SCR: JSON Response
            SCR-->>FAM: Raw Jobs List
        end
        
        FAM->>FAM: Filter (experience, skills)
        FAM->>FAM: Normalize data
        FAM-->>ORC: Filtered Jobs
    end
    
    ORC->>ORC: Deduplicate jobs
    ORC-->>DAG: All Jobs (via XCom)
    
    DAG->>CSV: export_to_csv(jobs)
    CSV-->>DAG: CSV filepath
    
    DAG->>SNS: send_notification(count, path)
    SNS->>SNS: AWS SNS Publish
    SNS-->>DAG: Success/Failure
```

### File Dependencies

```mermaid
graph LR
    subgraph "Config"
        CFG[config.py]
    end
    
    subgraph "Scrapers Package"
        BASE[base_scraper.py]
        JS[jsearch_scraper.py]
        AZ[adzuna_scraper.py]
        RO[remoteok_scraper.py]
    end
    
    subgraph "Job Families Package"
        DE[data_engineer.py]
        AE[analytics_engineer.py]
        DS[data_scientist_etl.py]
    end
    
    subgraph "Plugins"
        ORC[job_scraper.py]
        CSV[csv_exporter.py]
        SNS[sns_notifier.py]
    end
    
    subgraph "DAG"
        DAG[linkedin_job_scraper_dag.py]
    end
    
    CFG --> BASE & JS & AZ & RO
    CFG --> DE & AE & DS
    CFG --> CSV & SNS & DAG
    
    BASE --> JS & AZ & RO
    JS & AZ & RO --> DE & AE & DS
    DE & AE & DS --> ORC
    ORC --> DAG
    CSV --> DAG
    SNS --> DAG
```

### Job Data Schema

```mermaid
erDiagram
    JOB {
        string job_id PK
        string title
        string company
        string location
        boolean remote
        string job_type
        string posted_date
        string apply_link
        float salary_min
        float salary_max
        string salary_currency
        string experience_required
        string source
        string job_family
        datetime scraped_at
        text description_snippet
    }
```

### Configuration Flow

```mermaid
graph TD
    ENV[".env file"]
    DOTENV["python-dotenv"]
    CONFIG["config.py"]
    
    subgraph "Configuration Values"
        AWS["AWS_REGION<br/>AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY<br/>SNS_TOPIC_ARN"]
        API["RAPIDAPI_KEY<br/>ADZUNA_APP_ID<br/>ADZUNA_APP_KEY"]
        JOB["JOB_TITLES<br/>JOB_LOCATION<br/>EXPERIENCE_MIN/MAX<br/>ETL_SKILLS"]
        SCHED["SCHEDULE_INTERVAL<br/>SCHEDULE_TIMEZONE"]
    end
    
    ENV --> DOTENV
    DOTENV --> CONFIG
    CONFIG --> AWS & API & JOB & SCHED
```

---

## Key Design Patterns

| Pattern | Usage |
|---------|-------|
| **Template Method** | `BaseScraper` defines algorithm, subclasses implement `fetch_jobs()` |
| **Strategy** | Job families use different scrapers interchangeably |
| **Factory** | Each job family instantiates its own scrapers |
| **Facade** | `job_scraper.py` orchestrator hides complexity |

---

## Scalability Considerations

| Aspect | Current | Scalable To |
|--------|---------|-------------|
| **Scrapers** | 3 platforms | Add new scraper files |
| **Job Families** | 3 roles | Add new family files |
| **Scheduling** | 6-hour intervals | Any cron expression |
| **Storage** | Local CSV | S3, BigQuery, database |
| **Notifications** | Email (SNS) | Slack, SMS, webhooks |
