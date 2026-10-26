# CloudPulse — AWS Cloud Cost Monitoring & Budget Alert System (v2.0)

## Overview

**CloudPulse** is a Python and Flask-based cloud financial management (FinOps) dashboard that tracks AWS cloud expenses, analyzes service-wise costs, monitors budget utilization, and provides real-time budget threshold alerts.

**Version 2.0 Update**: Integrates with **AWS Cost Explorer API** via **AWS Boto3 SDK**, featuring live cloud billing sync, SQLite local caching to optimize API costs, and realistic enterprise AWS spending analytics.

---

## Key Features

- **AWS Cost Explorer Integration**: Programmatically syncs cloud billing data using the AWS Python SDK (`boto3`).
- **Cost-Optimized SQLite Caching**: Caches AWS cost data locally to prevent expensive repetitive API calls ($0.01/call on Cost Explorer).
- **Service-Wise Cost Analysis**: Tracks spending on core AWS services (**Amazon EC2**, **Amazon RDS**, **Amazon S3**, **AWS Lambda**, **Amazon CloudFront**, and **NAT Gateway**).
- **Monthly Budget Tracking**: Visualizes spend against allocated thresholds with live utilization percentages.
- **Dynamic Threshold Alerts**:
  - `50%`: Notice
  - `75%`: Warning
  - `90%`: High Risk
  - `100%+`: Critical Over-Budget
- **Interactive Visualizations**: Line and doughnut charts powered by Chart.js.
- **CSV Financial Export**: One-click download of billing history for audits and reporting.
- **RESTful API**: Clean JSON endpoints for spending summaries, services, alerts, and manual AWS sync triggers.

---

## Technologies Used

- **Cloud & SDK**: AWS Boto3, AWS Cost Explorer API, AWS IAM
- **Backend**: Python 3, Flask, SQLite3
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Chart.js
- **Tools**: Git, GitHub, RESTful APIs

---

## Project Structure

```text
Cloud-Cost-Monitoring/
├── app.py                  # Flask web server & REST API
├── aws_sync.py             # AWS Cost Explorer integration via Boto3
├── cost_calculator.py      # Core spending calculations and summary logic
├── database_setup.py       # SQLite database initialization & CSV seeder
├── requirements.txt        # Python package dependencies
├── README.md               # Documentation
├── .gitignore              # Ignored files (credentials, db, cache)
├── data/
│   └── cloud_costs.csv     # AWS enterprise billing dataset
├── static/
│   ├── css/style.css       # Dashboard styling
│   └── js/dashboard.js     # Chart.js rendering & API client
└── templates/
    └── index.html          # Main dashboard view
```

---

## Getting Started

### 1. Prerequisites
- Python 3.8+
- AWS Account & IAM credentials (optional for live sync; demo data included)

### 2. Installation
```bash
git clone https://github.com/your-username/Cloud-Cost-Monitoring.git
cd Cloud-Cost-Monitoring
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
python database_setup.py
```

### 4. (Optional) Configure AWS Credentials
To sync real data from your AWS account:
```bash
aws configure
# Or place AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in ~/.aws/credentials
```

### 5. Run the Application
```bash
python app.py
```
Open **`http://127.0.0.1:5000/dashboard`** in your browser.

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/dashboard` | `GET` | Web dashboard user interface |
| `/api/summary` | `GET` | Monthly budget, total spend, and utilization |
| `/api/services` | `GET` | Service-by-service cost breakdown |
| `/api/expenses` | `GET` | Paginated/historical expense records |
| `/api/daily-spending` | `GET` | Daily cost trend data for charts |
| `/api/monthly-spending` | `GET` | Month-over-month cost history |
| `/api/alerts` | `GET` | Active budget alert level and message |
| `/api/budget` | `POST` | Update the current monthly budget limit |
| `/api/sync-aws` | `POST` | Trigger live sync from AWS Cost Explorer to SQLite |
| `/export/csv` | `GET` | Download full cost history as CSV |
