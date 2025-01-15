import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, Float
import logging
import time
import json
import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger(__name__)

# Initialize Dash app
dashboard = dash.Dash(__name__)

# Database configuration
DB_CONFIG = {
    "username": "postgres",
    "password": "postgres",
    "host": "postgres",
    "port": 5432,
    "database": "oltp_db"
}

# Functions
def get_db_engine():
    """Create a connection to the PostgreSQL database."""
    connection_url = f"postgresql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(connection_url)

def initialize_db(engine):
    """Initialize the database schema."""
    meta = MetaData()
    metrics = Table(
        "metrics", meta,
        Column("created", String),
        Column("model", String),
        Column("stream", Boolean),
        Column("max_tokens", Integer),
        Column("temperature", Float),
        Column("type", String),
        Column("metrics_start", Float),
        Column("metrics_end", Float),
        Column("metrics_tokens", Integer),
        Column("metrics_prompt_tokens", Integer),
        Column("metrics_completion_tokens", Integer),
        Column("metrics_time_to_first_token", Float),
        schema="llm",
    )
    meta.create_all(engine)
    return metrics

def retry_connection(get_engine_func, retries=5, delay=5):
    """Retry mechanism for database connection."""
    while retries > 0:
        try:
            engine = get_engine_func().connect()
            LOGGER.info("Successfully connected to the database.")
            return engine
        except Exception as e:
            LOGGER.warning(f"Retrying connection to the database: {e}")
            retries -= 1
            time.sleep(delay)
    raise ConnectionError("Failed to connect to the database after multiple attempts.")

def read_json(file_path):
    """Read data from a JSON file."""
    with open(file_path, "r") as file:
        return json.load(file)

def insert_data(engine, table, data):
    """Insert JSON data into the database."""
    for item in data["data"]:
        engine.execute(
            table.insert().values(
                created=item.get("created"),
                model=item.get("model"),
                stream=item.get("stream"),
                max_tokens=item.get("max_tokens"),
                temperature=item.get("temperature"),
                type=item.get("type"),
                metrics_start=item.get("metrics", {}).get("start"),
                metrics_end=item.get("metrics", {}).get("end"),
                metrics_tokens=item.get("metrics", {}).get("tokens"),
                metrics_prompt_tokens=item.get("metrics", {}).get("prompt_tokens"),
                metrics_completion_tokens=item.get("metrics", {}).get("completion_tokens"),
                metrics_time_to_first_token=item.get("metrics", {}).get("time_to_first_token"),
            )
        )
        LOGGER.info(f"Inserted log entry for {item['created']}")

def fetch_data(engine, table):
    """Fetch data from the database."""
    query = sqlalchemy.select([table])
    result = engine.execute(query).fetchall()
    return pd.DataFrame(result, columns=[
        "created", "model", "stream", "max_tokens", "temperature", "type",
        "metrics_start", "metrics_end", "metrics_tokens", "metrics_prompt_tokens",
        "metrics_completion_tokens", "metrics_time_to_first_token"
    ])

def prepare_dashboard_data(df):
    """Prepare data for visualizations."""
    df["created"] = pd.to_datetime(df["created"])
    return {
        "total_tokens": df.groupby("model")["metrics_tokens"].sum().reset_index(),
        "prompt_vs_completion": df.groupby("model")[["metrics_prompt_tokens", "metrics_completion_tokens"]].sum().reset_index(),
        "time_to_first_token": df.groupby("model")["metrics_time_to_first_token"].mean().reset_index(),
        "temperature_distribution": df["temperature"],
        "request_type_distribution": df["type"].value_counts().reset_index(),
        "tokens_over_time": df[["created", "metrics_tokens"]],
    }

def create_dashboard_layout(data):
    """Define the layout of the Dash dashboard."""
    return html.Div([
        html.H1("LLM Log Metrics Dashboard", style={"textAlign": "center"}),

        # Chart 1: Total Tokens by Model
        html.Div([
            dcc.Graph(
                id="total-tokens-by-model",
                figure=px.bar(data["total_tokens"], x="model", y="metrics_tokens", title="Total Tokens Used by Model")
            )
        ]),

        # Chart 2: Prompt vs Completion Tokens by Model
        html.Div([
            dcc.Graph(
                id="prompt-vs-completion-tokens",
                figure=px.bar(
                    data["prompt_vs_completion"],
                    x="model",
                    y=["metrics_prompt_tokens", "metrics_completion_tokens"],
                    title="Prompt vs Completion Tokens by Model",
                    labels={"value": "Tokens", "variable": "Type"},
                    barmode="stack"
                )
            )
        ]),

        # Chart 3: Average Time to First Token by Model
        html.Div([
            dcc.Graph(
                id="time-to-first-token",
                figure=px.bar(
                    data["time_to_first_token"],
                    x="model",
                    y="metrics_time_to_first_token",
                    title="Average Time to First Token by Model (seconds)"
                )
            )
        ]),

        # Chart 4: Temperature Distribution
        html.Div([
            dcc.Graph(
                id="temperature-distribution",
                figure=px.histogram(
                    data["temperature_distribution"],
                    x=data["temperature_distribution"],
                    title="Temperature Distribution",
                    labels={"x": "Temperature"}
                )
            )
        ]),

        # Chart 5: Request Type Distribution
        html.Div([
            dcc.Graph(
                id="request-type-distribution",
                figure=px.pie(
                    data["request_type_distribution"],
                    names="index",
                    values="type",
                    title="Request Type Distribution"
                )
            )
        ]),

        # Chart 6: Token Usage Over Time
        html.Div([
            dcc.Graph(
                id="tokens-over-time",
                figure=px.line(
                    data["tokens_over_time"],
                    x="created",
                    y="metrics_tokens",
                    title="Token Usage Over Time",
                    labels={"created": "Timestamp", "metrics_tokens": "Tokens"}
                )
            )
        ]),
    ])

# Main script
if __name__ == "__main__":
    # Initialize database
    engine = retry_connection(get_db_engine)
    metrics_table = initialize_db(engine)

    # Insert data into the database
    json_data = read_json("data/llm-logs.json")
    insert_data(engine, metrics_table, json_data)

    # Fetch data and prepare for visualization
    df = fetch_data(engine, metrics_table)
    dashboard_data = prepare_dashboard_data(df)

    # Set up the dashboard layout
    dashboard.layout = create_dashboard_layout(dashboard_data)

    # Run the Dash app
    dashboard.run_server(host="0.0.0.0", port=8050)
