# Data Engineering Take-Home Test

## Overview

Build a simple analytics pipeline to process LLM application logs and produce a chart or dashboard. The dataset contains 1,000 API call records with metrics like timestamps, token counts, and latency.

1. Load JSON Data into a Database
Database Initialization:
 - A PostgreSQL database is configured, and a metrics table is defined using SQLAlchemy's ORM.
 - The schema of the table matches the fields in the JSON data.
Data Insertion:
 - The JSON file is read, and each log entry is inserted into the metrics table in the database.
 - The insert_data function ensures that each entry is mapped to the corresponding database columns.

2. Calculate Metrics
Data Retrieval:
 - All data from the metrics table is fetched into a Pandas DataFrame for processing.
Metrics Calculation:
 - The prepare_dashboard_data function computes key metrics from the data:  
  - Total Tokens by Model: Summed token usage grouped by model.
  - Prompt vs Completion Tokens: Breakdown of tokens into prompt and completion categories for each model.
  - Average Time to First Token: Mean latency (time_to_first_token) grouped by model.
  - Temperature Distribution: Histogram of the temperature parameter.
  - Request Type Distribution: Distribution of request types (text, completion, etc.).
  - Token Usage Over Time: Trend of total token usage over time.

3. Visualization via Dashboard
Dash App:
 - A Dash app is set up for interactive visualization of the computed metrics.
 - The dashboard layout is defined in the create_dashboard_layout function and contains six visualizations:

## Steps to execute the code

1. Prepare the Environment
Before running the container, ensure the following prerequisites are met:

 - Docker is installed on your machine.
 - The code for the application (including the Dockerfile, Python script, and JSON data file) is in a single directory.

2. Build and start the Docker Containers
Build and run the containers with the following command:

```
cd data-eng-take-home-test
docker-compose build && docker-compose up
```
3. Access the App
Open a web browser and navigate to http://localhost:8050 to view the dashboard.
You can access the postgres database by navigating to http://localhost:8000. Use the credentials given in docker-compose.yml to login into pgAdmin.

4. Shut Down and Remove the Docker Containers

```
docker-compose down 
docker-compose down --volumes        
```

## Data Format

```json
{
  "created": "2024-12-18 16:40:40",
  "model": "gpt-4o-2024-11-20",
  "metrics": {
    "tokens": 1213,
    "prompt_tokens": 337,
    "completion_tokens": 876,
    "time_to_first_token": 12.769
  }
}
```
