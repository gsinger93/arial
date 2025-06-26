# Arial - AI-Powered Financial Investment Advisor

## Overview

Arial is a financial service API endpoint designed to provide investment recommendations across various markets. It leverages modern AI models to analyse public shares, forex, indexes, bonds, news stories, and financial reports to generate data-driven predictions on investment returns.

This project is built with a focus on modern data engineering principles, incorporating a robust CI/CD pipeline, scheduled computing, and security-first development practices.

## Key Features

* **Multi-Market Analysis**: Ingests and analyses data from diverse financial markets.
* **AI-Powered Predictions**: Utilises flexible AI models to forecast investment returns.
* **Secure by Design**: Implements security best practices, including handling of SSL certificates.
* **Automated Data Pipelines**: Employs dbt for data transformation and GitHub Actions for CI/CD and automation.
* **Cloud-Native**: Built on Google Cloud Platform (GCP), utilising services like BigQuery for data warehousing.

## Technology Stack

* **Data Ingestion**: Python (`alpha_vantage` library)
* **Data Warehouse**: Google BigQuery
* **Data Transformation**: dbt (Data Build Tool)
* **CI/CD & Automation**: GitHub Actions
* **Cloud Platform**: Google Cloud Platform (GCP)
* **Infrastructure as Code**: (Planned)
* **API**: (Planned)

## Project Structure


Arial/
├── .github/workflows/         # GitHub Actions workflows for CI/CD
├── dbt/Arial/                 # dbt project for data transformations
│   ├── models/
│   │   └── staging/
│   │       └── stg_shares.sql   # Example staging model
│   ├── dbt_project.yml        # dbt project configuration
│   └── README.md
├── security/
│   └── CA-Bundle-ZTNA.pem     # SSL Certificate Bundle
├── service accounts/
│   └── gcp-data-ingestion.json # GCP service account key
├── .env                       # Environment variables (DO NOT COMMIT)
├── .gitignore
├── data_ingestion.py          # (Planned) Python script for data ingestion
├── requirements.txt           # Python dependencies
└── README.md                  # This file


## Getting Started

### Prerequisites

* Python 3.8+
* Google Cloud SDK
* dbt Core
* Access to a GCP project with BigQuery enabled.
* An Alpha Vantage API key.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd Arial
    ```

2.  **Set up a Python virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.\.venv\Scripts\activate`
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add the following, replacing the placeholder values with your actual credentials:
    ```
    # GCP and BigQuery configuration
    GCP_PROJECT_ID="your-gcp-project-id"
    BIGQUERY_DATASET_ID="financial_data_landing"
    BIGQUERY_TABLE_ID="stock_values"
    GOOGLE_APPLICATION_CREDENTIALS="C:\Users\George.Singer\Documents\GitHub\Arial\service accounts\gcp-data-ingestion.json"

    # Alpha Vantage API key
    ALPHA_VANTAGE_API_KEY="your-alpha-vantage-key"

    # Path to your CA Bundle for secure requests
    REQUESTS_CA_BUNDLE="C:\Users\George.Singer\Documents\GitHub\Arial\security\CA-Bundle-ZTNA.pem"
    ```
    **Important:** Ensure your `.gitignore` file includes `.env` to prevent committing secrets.

5.  **Set up dbt:**
    Navigate to the `dbt/Arial` directory and follow the dbt setup instructions to connect to your BigQuery instance. You will need to configure your `profiles.yml` file (typically located in `~/.dbt/`).

## Data Transformation with dbt

This project uses dbt to transform raw data landed in BigQuery into clean, reliable models for analysis.

* **Staging Models**: Raw data is first cleaned and prepared in staging models (e.g., `stg_shares.sql`).
* **Run dbt models**:
    ```bash
    cd dbt/Arial
    dbt run
    ```
* **Test dbt models**:
    ```bash
    dbt test
    ```

## CI/CD with GitHub Actions

The project is configured to use GitHub Actions for continuous integration and deployment. Workflows are defined in the `.github/workflows` directory and will handle:
* Running Python scripts on a schedule.
* Executing dbt model runs and tests.
* (Future) Deploying the API endpoint.

## Security

Security is a core consideration for this project.
* **Secrets Management**: All secrets (API keys, credentials) are managed via environment variables and are not hardcoded. The `.env` file is explicitly ignored in version control.
* **Secure Communication**: The `REQUESTS_CA_BUNDLE` variable is used to ensure that all outbound HTTPS requests from Python scripts are made through a trusted SSL certificate, which is crucial in corporate network environments.

---
_This README is a living document and will be updated as the project evolves._