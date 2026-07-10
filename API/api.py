"""
==========================================================
Recommendations API Layer
==========================================================

This module provides RESTful API endpoints to serve
agricultural recommendations from PostgreSQL to the
front-end application seamlessly.

Project:
Green Innovation Real-Time Data Pipeline
"""

# ==========================================================
# Import Required Libraries
# ==========================================================

import sys
import logging
from pathlib import Path
from typing import Any, List, Dict

from fastapi import FastAPI, HTTPException, Query, Path as FastAPIPath
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

# ==========================================================
# Path Configuration for Imports
# ==========================================================

# Resolve the parent directory to allow module imports
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent

if str(PARENT_DIR) not in sys.path:
    sys.path.append(str(PARENT_DIR))

# Dynamic Import to handle different project structures automatically
try:
    from database.db import get_database_engine
except ModuleNotFoundError:
    try:
        from recommendations.db import get_database_engine
    except ModuleNotFoundError:
        from db import get_database_engine

# ==========================================================
# Logging Configuration
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ==========================================================
# FastAPI Application Setup
# ==========================================================

app = FastAPI(
    title="Green Innovation API",
    description="Real-time agricultural recommendations and anomaly detection API.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ==========================================================
# CORS Middleware Configuration
# ==========================================================

# Configured to allow seamless connection from any front-end framework
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific domains in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ==========================================================
# Database Connection Dependency
# ==========================================================

def execute_query(query: text, params: dict = None) -> pd.DataFrame:
    """
    Safely execute a SQL query and return a pandas DataFrame.
    """
    engine = get_database_engine()
    try:
        df = pd.read_sql(query, engine, params=params)
        return df
    except SQLAlchemyError as e:
        logger.error("Database query failed: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal server error while accessing the database."
        )
    finally:
        engine.dispose()

# ==========================================================
# API Endpoints
# ==========================================================

@app.get("/api/v1/health", tags=["System"])
def health_check() -> Dict[str, str]:
    """
    Perform a simple health check to ensure the API is running.
    """
    return {"status": "success", "message": "API is up and running."}


@app.get("/api/v1/recommendations", tags=["Recommendations"])
def get_recent_recommendations(
    limit: int = Query(50, ge=1, le=500, description="Number of records to return")
) -> List[Dict[str, Any]]:
    """
    Retrieve the most recent agricultural recommendations.
    """
    logger.info("Fetching the latest %s recommendations.", limit)
    
    query = text(
        """
        SELECT 
            weather_id, city, is_anomaly, anomaly_score, 
            risk_level, irrigation_action, spraying_action, 
            recommendation, source_timestamp, generated_at 
        FROM recommendations 
        ORDER BY generated_at DESC 
        LIMIT :limit;
        """
    )
    
    df = execute_query(query, {"limit": limit})
    
    if df.empty:
        return []
    
    # Handle NaNs or missing values safely for JSON serialization
    df = df.fillna(value="")
    
    # Convert DataFrame to a list of dictionaries for the API response
    return df.to_dict(orient="records")


@app.get("/api/v1/recommendations/{city}", tags=["Recommendations"])
def get_recommendations_by_city(
    city: str = FastAPIPath(..., description="The name of the city to filter by"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return")
) -> List[Dict[str, Any]]:
    """
    Retrieve the most recent agricultural recommendations for a specific city.
    """
    logger.info("Fetching recommendations for city: %s", city)
    
    query = text(
        """
        SELECT 
            weather_id, city, is_anomaly, anomaly_score, 
            risk_level, irrigation_action, spraying_action, 
            recommendation, source_timestamp, generated_at 
        FROM recommendations 
        WHERE LOWER(city) = LOWER(:city)
        ORDER BY generated_at DESC 
        LIMIT :limit;
        """
    )
    
    df = execute_query(query, {"city": city, "limit": limit})
    
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendations found for the city: {city}"
        )
        
    df = df.fillna(value="")
    return df.to_dict(orient="records")