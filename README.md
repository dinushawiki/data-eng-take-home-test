# Data Engineering Take-Home Test

## Overview

Build a simple analytics pipeline to process LLM application logs and produce a chart or dashboard. The dataset contains 1,000 API call records with metrics like timestamps, token counts, and latency.

1. **Load JSON Data into a Database**
   - **Database Initialization**:
     - A PostgreSQL database is configured, and a `metrics` table is defined using SQLAlchemy's ORM.
     - The schema of the table matches the fields in the JSON data.
   - **Data Insertion**:
     - The JSON file is read, and each log entry is inserted into the `metrics` table in the database.
     - The `insert_data` function ensures that each entry is mapped to the corresponding database columns.


2. **Calculate Metrics**
   - **Data Retrieval**:
     - All data from the `metrics` table is fetched into a Pandas DataFrame for processing.
   - **Metrics Calculation**:
     - The `prepare_dashboard_data` function computes key metrics from the data:  
       - **Total Tokens by Model**: Summed token usage grouped by model.  
       - **Prompt vs Completion Tokens**: Breakdown of tokens into prompt and completion categories for each model.  
       - **Average Time to First Token**: Mean latency (`time_to_first_token`) grouped by model.  
       - **Temperature Distribution**: Histogram of the temperature parameter.  
       - **Request Type Distribution**: Distribution of request types (e.g., text, completion, etc.).  
       - **Token Usage Over Time**: Trend of total token usage over time.

3. **Visualization via Dashboard**
   - **Dash App**:
     - A Dash app is set up for interactive visualization of the computed metrics.
     - The dashboard layout is defined in the `create_dashboard_layout` function and contains six visualizations.

---


## Steps to Execute the Code

1. **Prepare the Environment.**  
   Before running the container, ensure the following prerequisites are met:
   
   - Docker is installed on your machine.
   - The code for the application (including the `Dockerfile`, Python script, and JSON data file) is in a single directory.

2. **Build and Start the Docker Containers**  
   Run the following commands to build and start the application:

   ```bash
   cd data-eng-take-home-test
   docker-compose build && docker-compose up
   ```
3. **Access the App**  
   Open a web browser and navigate to [http://localhost:8050](http://localhost:8050) to view the dashboard.  
   You can access the PostgreSQL database by navigating to [http://localhost:8000](http://localhost:8000).  
   Use the credentials provided in `docker-compose.yml` to log in to pgAdmin.


4. **Shut Down and Remove the Docker Containers**  
   Run the following commands to stop and remove the containers:

   ```bash
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
## Dashboard

1. **Total Tokens Used by Model**

   - Displays the total number of tokens used by each model.
   - Helps track token consumption per model.
   ![Alt Text](images/total_tokens_by_model.png "Total Tokens Used by Model")

2. **Prompt vs. Completion Tokens by Model:**

   - A stacked bar chart shows the split between Prompt vs. Completion Tokens by Model.
   - Useful to understand model usage patterns.
   ![Alt Text](images/prompt_vs_completion.png "Prompt vs. Completion Tokens by Model")

3. **Average Time to First Token by Model:**

   - Displays each model's average time (in seconds) to generate the first token.
   - Helps identify performance bottlenecks.
   ![Alt Text](images/average_time_to_first_token.png "Average Time to First Token by Model")

4. **Temperature Distribution:**

   - Histogram of the temperature parameter.
   - Useful for understanding the range of creativity levels used.
   ![Alt Text](images/temperature_distribution.png "Temperature Distribution")

5. **Request Type Distribution:**

   - Pie chart of the type field (e.g., text, chat).
   - Provides insights into the types of requests being processed.
   ![Alt Text](images/request_type_distribution.png "Request Type Distribution")

6. **Token Usage Over Time:**

   - Line chart showing token usage over time.
   - Useful for tracking trends in token consumption.
   ![Alt Text](images/token_usage_over_time.png "Token Usage Over Time")
