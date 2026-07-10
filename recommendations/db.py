"""
==========================================================
Database Access Layer (DAL)
==========================================================

This module manages the connection between the Analytics
and Recommendation layer and the PostgreSQL database.

Project:
Green Innovation Real-Time Data Pipeline

Author:
Mohamed Hamdy
"""

# ==========================================================
# Import Required Libraries
# ==========================================================

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL


# ==========================================================
# Load Environment Variables
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH)


# ==========================================================
# Database Configuration
# ==========================================================

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")

REQUIRED_VARIABLES = {
    "POSTGRES_DB": DB_NAME,
    "POSTGRES_USER": DB_USER,
    "POSTGRES_PASSWORD": DB_PASSWORD,
    "POSTGRES_PORT": DB_PORT,
}

missing_variables = [
    variable_name
    for variable_name, variable_value in REQUIRED_VARIABLES.items()
    if not variable_value
]

if missing_variables:
    raise ValueError(
        "Missing required environment variables: "
        + ", ".join(missing_variables)
    )


# ==========================================================
# Create Database URL and Engine
# ==========================================================

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)


def get_database_engine() -> Engine:
    """
    Create and return a SQLAlchemy engine connected to PostgreSQL.
    """

    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )


# ==========================================================
# Read Weather Data
# ==========================================================

def load_weather_data(engine: Engine) -> pd.DataFrame:
    """
    Read all processed weather records from PostgreSQL.
    """

    query = """
        SELECT
            id,
            city,
            latitude,
            longitude,
            temp,
            humidity,
            pressure,
            sea_level,
            wind_speed,
            clouds,
            rain_1h,
            weather_description,
            timestamp,
            weather_status
        FROM weather_data
        ORDER BY id;
    """

    return pd.read_sql(query, engine)


# ==========================================================
# Create Recommendations Table
# ==========================================================

def create_recommendations_table(engine: Engine) -> None:
    """
    Create the recommendations table and add any missing
    Machine Learning columns safely.
    """

    create_table_query = """
        CREATE TABLE IF NOT EXISTS recommendations (
            id SERIAL PRIMARY KEY,
            weather_id INTEGER NOT NULL UNIQUE,
            city VARCHAR(100),
            is_anomaly BOOLEAN NOT NULL DEFAULT FALSE,
            anomaly_score DOUBLE PRECISION,
            model_version VARCHAR(50),
            risk_level VARCHAR(20) NOT NULL,
            irrigation_action TEXT NOT NULL,
            spraying_action TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            source_timestamp TIMESTAMP,
            generated_at TIMESTAMP WITH TIME ZONE
                DEFAULT CURRENT_TIMESTAMP
        );
    """

    alter_table_query = """
        ALTER TABLE recommendations
            ADD COLUMN IF NOT EXISTS is_anomaly
                BOOLEAN NOT NULL DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS anomaly_score
                DOUBLE PRECISION,
            ADD COLUMN IF NOT EXISTS model_version
                VARCHAR(50);
    """

    with engine.begin() as connection:
        connection.execute(text(create_table_query))
        connection.execute(text(alter_table_query))

# ==========================================================
# Save Recommendations
# ==========================================================

def save_recommendations(
    recommendations_df: pd.DataFrame,
    engine: Engine,
) -> int:
    """
    Insert new recommendations or update existing records
    using weather_id as the unique identifier.
    """

    if recommendations_df.empty:
        return 0

    required_columns = {
        "weather_id",
        "city",
        "is_anomaly",
        "anomaly_score",
        "model_version",
        "risk_level",
        "irrigation_action",
        "spraying_action",
        "recommendation",
        "source_timestamp",
    }

    missing_columns = required_columns.difference(
        recommendations_df.columns
    )

    if missing_columns:
        raise ValueError(
            "Missing recommendation columns: "
            + ", ".join(sorted(missing_columns))
        )

    upsert_query = text(
        """
        INSERT INTO recommendations (
            weather_id,
            city,
            is_anomaly,
            anomaly_score,
            model_version,
            risk_level,
            irrigation_action,
            spraying_action,
            recommendation,
            source_timestamp,
            generated_at
        )
        VALUES (
            :weather_id,
            :city,
            :is_anomaly,
            :anomaly_score,
            :model_version,
            :risk_level,
            :irrigation_action,
            :spraying_action,
            :recommendation,
            :source_timestamp,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT (weather_id)
        DO UPDATE SET
            city = EXCLUDED.city,
            is_anomaly = EXCLUDED.is_anomaly,
            anomaly_score = EXCLUDED.anomaly_score,
            model_version = EXCLUDED.model_version,
            risk_level = EXCLUDED.risk_level,
            irrigation_action = EXCLUDED.irrigation_action,
            spraying_action = EXCLUDED.spraying_action,
            recommendation = EXCLUDED.recommendation,
            source_timestamp = EXCLUDED.source_timestamp,
            generated_at = CURRENT_TIMESTAMP;
        """
    )

    records = recommendations_df.to_dict(
        orient="records"
    )

    with engine.begin() as connection:
        connection.execute(
            upsert_query,
            records,
        )

    return len(records)

# ==========================================================
# Load New Weather Records
# ==========================================================

def load_new_weather_data(
    engine: Engine,
    last_processed_id: int = 0,
) -> pd.DataFrame:
    """
    Load only new weather records that have not
    been processed yet.
    """

    query = text(
        """
        SELECT
            id,
            city,
            latitude,
            longitude,
            temp,
            humidity,
            pressure,
            sea_level,
            wind_speed,
            clouds,
            rain_1h,
            weather_description,
            timestamp,
            weather_status
        FROM weather_data
        WHERE id > :last_processed_id
        ORDER BY id;
        """
    )

    return pd.read_sql(
        query,
        engine,
        params={
            "last_processed_id": last_processed_id,
        },
    )


# ==========================================================
# Get Latest Weather Record ID
# ==========================================================

def get_latest_weather_id(
    engine: Engine,
) -> int:
    """
    Return the latest weather record ID.
    """

    query = text(
        """
        SELECT
            COALESCE(MAX(id),0)
        FROM weather_data;
        """
    )

    with engine.begin() as connection:

        latest_id = connection.execute(
            query
        ).scalar()

    return int(latest_id)


# ==========================================================
# Check Recommendations Table
# ==========================================================

def recommendations_table_exists(
    engine: Engine,
) -> bool:
    """
    Check whether recommendations table exists.
    """

    query = text(
        """
        SELECT EXISTS (

            SELECT 1

            FROM information_schema.tables

            WHERE table_name='recommendations'

        );
        """
    )

    with engine.begin() as connection:

        return bool(
            connection.execute(
                query
            ).scalar()
        )