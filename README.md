# Arial - AI-Powered Financial Investment Advisor

## Overview

Arial is a financial service API endpoint designed to provide investment recommendations across various markets. [cite_start]It leverages modern data engineering practices and a modular, agent-based AI architecture to analyse market data and news, generating data-driven predictions on investment returns. [cite: 35]

This project is built with a focus on a robust, automated, and secure foundation, incorporating:
* **dbt** for reliable data transformation.
* **Python** for flexible data ingestion.
* [cite_start]**GitHub Actions** for CI/CD and process automation. [cite: 37, 38, 50]
* [cite_start]**Google Cloud Platform (GCP)** for scalable data warehousing and AI model hosting. [cite: 37]

[cite_start]The system is designed around a series of independent AI tools (using the Machine-Centric Prototyping framework) that can be orchestrated by a central agent to answer complex financial questions. [cite: 26, 29, 30, 31, 32]

## Key Features

* [cite_start]**Multi-Stock Analysis**: Ingests and analyses daily price data for a configurable list of public shares. [cite: 18, 19, 20]
* [cite_start]**News & Sentiment Analysis**: Ingests news articles to be used for semantic analysis and embedding generation. [cite: 25]
* [cite_start]**AI-Powered Predictions**: Utilises flexible AI models (e.g., time-series, XGBoost) hosted on Vertex AI to forecast investment returns. [cite: 36, 28]
* [cite_start]**Modular AI Architecture**: Built as a collection of MCP servers, allowing an orchestrating agent to use different "tools" (like ROI prediction or news retrieval) to form a recommendation. [cite: 27, 29, 32]
* [cite_start]**Automated & Tested Data Pipelines**: Employs dbt for data transformation and GitHub Actions for CI/CD, ensuring data quality with automated testing and linting. [cite: 15]
* [cite_start]**Secure by Design**: Implements security best practices, including secure secret management with GitHub Secrets and handling of corporate SSL certificates for network requests. [cite: 8, 21]

## Technology Stack

* **Data Ingestion**: Python (`alpha_vantage`, `requests`)
* **Data Warehouse**: Google BigQuery
* **Data Transformation**: dbt (Data Build Tool)
* **Vector Embeddings**: Google Vertex AI
* **AI/ML Model Serving**: Google Vertex AI
* **API & Agent Serving**: FastAPI
* **CI/CD & Automation**: GitHub Actions
* **Cloud Platform**: Google Cloud Platform (GCP)

## Project Structure

```
Arial/
├── .github/
│   ├── pull_request_template.md # The PR template for the repository
│   └── workflows/               # GitHub Actions workflows for CI/CD & scheduling
├── api/                         # (Planned) FastAPI applications for MCP servers
│   ├── agent/
│   └── tools/
├── data_ingestion/
│   └── ingest_shares.py         # Python script for ingesting share data
├── dbt/Arial/                   # dbt project for data transformations
│   ├── models/
│   │   ├── staging/             # Staging models (e.g., stg_shares.sql)
│   │   └── marts/               # (Planned) Data marts for analysis
│   ├── tests/
│   │   └── generic/             # Custom generic dbt tests
│   └── dbt_project.yml
├── notebooks/                   # (Planned) Jupyter notebooks for data exploration & model dev
├── security/
│   └── CA-Bundle-ZTNA.pem       # SSL Certificate Bundle for corporate networks
├── service accounts/
│   └── gcp-data-ingestion.json  # GCP service account key
├── .gitignore
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Getting Started

### Prerequisites

* Python 3.8+
* Google Cloud SDK
* dbt Core
* An Alpha Vantage API key.
* Access to a GCP project with BigQuery enabled.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd Arial
    ```

2.  **Set up a Python virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .\.venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the project root. Copy the contents of your `.env` file, ensuring your personal keys and paths are correct.
    **Important:** The `.env` file is listed in `.gitignore` and should never be committed to the repository.

5.  **Set up dbt:**
    Navigate to the `dbt/Arial` directory. Your `profiles.yml` file is already configured to connect to your BigQuery instance using environment variables.

## Data Pipelines

This project uses Python for ingestion and dbt for transformation.

* **Run Ingestion**:
    ```bash
    # Run from the project root directory
    python data_ingestion/ingest_shares.py
    ```
* **Run dbt Transformations**:
    ```bash
    cd dbt/Arial
    dbt run
    ```
* **Test dbt Models**:
    ```bash
    cd dbt/Arial
    dbt test
    ```

## CI/CD with GitHub Actions

The project is configured to use GitHub Actions for automation, defined in the `.github/workflows` directory. These workflows handle:
* Running Python linting and dbt tests on every pull request.
* Running the data ingestion script on a daily schedule.

## Security

* [cite_start]**Secrets Management**: All secrets (API keys, credentials) are managed via a local `.env` file for development and GitHub Secrets for CI/CD pipelines. [cite: 51] No secrets are hardcoded in the source code.
* [cite_start]**Secure Communication**: The `REQUESTS_CA_BUNDLE` variable is used to ensure that all outbound HTTPS requests from Python scripts are made through a trusted SSL certificate, which is crucial in corporate network environments. [cite: 52]

---
_This README is a living document and will be updated as the project evolves._
