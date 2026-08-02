"""
==========================================================
Green Innovation FastAPI Backend
==========================================================

Provides:
1. API health check.
2. Recent agricultural recommendations.
3. Recommendations filtered by city.
4. Live location analysis using latitude and longitude.
5. OpenWeather current weather retrieval.
6. Machine Learning anomaly detection.
7. Agricultural recommendation generation.
8. Saving weather and recommendation results to PostgreSQL.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
import secrets
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import jwt
import requests
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Path as FastAPIPath, Query, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


# ==========================================================
# Project Paths
# ==========================================================

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
RECOMMENDATIONS_DIR = PROJECT_ROOT / "recommendations"
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH)

# recommendations/predict.py imports modules such as "db"
# directly, so this directory must be available in sys.path.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(RECOMMENDATIONS_DIR) not in sys.path:
    sys.path.insert(0, str(RECOMMENDATIONS_DIR))


# ==========================================================
# Project Imports
# ==========================================================

from recommendations.db import get_database_engine
from recommendations.predict import (  # noqa: E402
    build_recommendations,
    load_model,
    predict_weather,
    save_prediction_results,
)


# ==========================================================
# Logging
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ==========================================================
# Environment Configuration
# ==========================================================

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

OPENWEATHER_CURRENT_URL = (
    "https://api.openweathermap.org/data/2.5/weather"
)

MODEL_VERSION = "1.0.0"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-development-secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title="Green Innovation API",
    description=(
        "Real-time agricultural recommendations, "
        "location analysis, and anomaly detection API."
    ),
    version="1.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


# ==========================================================
# CORS Configuration
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ==========================================================
# Request Models
# ==========================================================

class LocationAnalysisRequest(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude between -90 and 90.",
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude between -180 and 180.",
    )


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==========================================================
# Utility Functions
# ==========================================================


def create_users_table() -> None:
    engine = get_database_engine()
    query = text(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(120) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        CREATE UNIQUE INDEX IF NOT EXISTS users_email_lower_idx
            ON users (LOWER(email));
        """
    )
    try:
        with engine.begin() as connection:
            connection.execute(query)
    finally:
        engine.dispose()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = 310_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, digest_text = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_text)
        expected = base64.b64decode(digest_text)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations_text))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, email: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "email": email, "exp": expires_at, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_user_by_email(email: str) -> dict[str, Any] | None:
    engine = get_database_engine()
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text("SELECT id, full_name, email, password_hash, is_active FROM users WHERE LOWER(email)=LOWER(:email) LIMIT 1"),
                {"email": email.strip()},
            ).mappings().first()
        return dict(row) if row else None
    finally:
        engine.dispose()


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You must log in before analyzing a location.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = int(payload.get("sub"))
    except (jwt.PyJWTError, TypeError, ValueError):
        raise credentials_error

    engine = get_database_engine()
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text("SELECT id, full_name, email, is_active FROM users WHERE id=:user_id LIMIT 1"),
                {"user_id": user_id},
            ).mappings().first()
    finally:
        engine.dispose()

    if not row or not row["is_active"]:
        raise credentials_error
    return dict(row)


def make_json_safe(value: Any) -> Any:
    """
    Convert pandas, NumPy and datetime values into values
    FastAPI can safely serialize as JSON.
    """

    if value is None:
        return None

    if isinstance(value, (datetime, date, pd.Timestamp)):
        return value.isoformat()

    if isinstance(value, np.generic):
        return value.item()

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    return value


def serialize_record(record: dict[str, Any]) -> dict[str, Any]:
    """
    Convert all values inside a record into JSON-safe values.
    """

    return {
        key: make_json_safe(value)
        for key, value in record.items()
    }


def execute_select_query(
    query,
    params: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Execute a SELECT query and return a DataFrame.
    """

    engine = get_database_engine()

    try:
        return pd.read_sql(
            query,
            engine,
            params=params,
        )

    except SQLAlchemyError as error:
        logger.exception(
            "Database SELECT query failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "The server could not read data "
                "from PostgreSQL."
            ),
        ) from error

    finally:
        engine.dispose()


# ==========================================================
# OpenWeather Integration
# ==========================================================

def fetch_current_weather(
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    """
    Fetch current weather for any valid latitude and longitude.
    """

    if not OPENWEATHER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail=(
                "OPENWEATHER_API_KEY is missing from "
                "the backend .env file."
            ),
        )

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        response = requests.get(
            OPENWEATHER_CURRENT_URL,
            params=params,
            timeout=20,
        )

    except requests.Timeout as error:
        raise HTTPException(
            status_code=504,
            detail="The weather service took too long to respond.",
        ) from error

    except requests.RequestException as error:
        logger.exception(
            "Could not connect to OpenWeather."
        )

        raise HTTPException(
            status_code=502,
            detail="Could not connect to the live weather service.",
        ) from error

    try:
        data = response.json()
    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail="The weather service returned an invalid response.",
        ) from error

    if response.status_code == 401:
        raise HTTPException(
            status_code=500,
            detail=(
                "The OpenWeather API key is invalid "
                "or has not been activated yet."
            ),
        )

    if response.status_code == 429:
        raise HTTPException(
            status_code=429,
            detail=(
                "The OpenWeather API request limit "
                "has been reached."
            ),
        )

    if response.status_code != 200:
        weather_error = data.get(
            "message",
            "The selected location could not be analyzed.",
        )

        raise HTTPException(
            status_code=response.status_code,
            detail=str(weather_error),
        )

    main_data = data.get("main", {})
    wind_data = data.get("wind", {})
    clouds_data = data.get("clouds", {})
    rain_data = data.get("rain", {})
    weather_list = data.get("weather", [])

    if not main_data:
        raise HTTPException(
            status_code=502,
            detail="The weather response is missing required data.",
        )

    weather_description = ""

    if weather_list:
        weather_description = str(
            weather_list[0].get("description", "")
        )

    pressure = main_data.get("pressure")

    # Some locations do not return sea_level.
    # Falling back to pressure is safer than inserting zero.
    sea_level = main_data.get(
        "sea_level",
        pressure,
    )

    city_name = str(
        data.get("name")
        or f"Location {latitude:.4f}, {longitude:.4f}"
    )

    return {
        "city": city_name,
        "latitude": float(latitude),
        "longitude": float(longitude),
        "temp": float(main_data.get("temp")),
        "humidity": int(main_data.get("humidity")),
        "pressure": int(pressure),
        "sea_level": int(sea_level),
        "wind_speed": float(
            wind_data.get("speed", 0.0)
        ),
        "clouds": int(
            clouds_data.get("all", 0)
        ),
        "rain_1h": float(
            rain_data.get("1h", 0.0)
        ),
        "weather_description": weather_description,
        "timestamp": float(
            data.get("dt")
            or datetime.now().timestamp()
        ),
        "weather_status": "analyzed",
    }


# ==========================================================
# PostgreSQL Weather Storage
# ==========================================================

def save_weather_record(
    weather: dict[str, Any],
) -> int:
    """
    Save one live weather record and return its generated ID.
    """

    query = text(
        """
        INSERT INTO weather_data (
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
        )
        VALUES (
            :city,
            :latitude,
            :longitude,
            :temp,
            :humidity,
            :pressure,
            :sea_level,
            :wind_speed,
            :clouds,
            :rain_1h,
            :weather_description,
            :timestamp,
            :weather_status
        )
        RETURNING id;
        """
    )

    engine = get_database_engine()

    try:
        with engine.begin() as connection:
            weather_id = connection.execute(
                query,
                weather,
            ).scalar_one()

        return int(weather_id)

    except SQLAlchemyError as error:
        logger.exception(
            "Could not save live weather data."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Live weather was retrieved, but it could "
                "not be saved to PostgreSQL."
            ),
        ) from error

    finally:
        engine.dispose()


# ==========================================================
# ML and Recommendation Processing
# ==========================================================

def analyze_weather_record(
    weather_id: int,
    weather: dict[str, Any],
) -> dict[str, Any]:
    """
    Run the existing trained model and recommendation rules
    for one live weather record.
    """

    model_input = {
        "id": weather_id,
        **weather,
    }

    weather_df = pd.DataFrame(
        [model_input]
    )

    try:
        model = load_model()

        prediction_df = predict_weather(
            model=model,
            weather_df=weather_df,
        )

        prediction_df["model_version"] = MODEL_VERSION

        recommendation_df = build_recommendations(
            prediction_df
        )

        save_prediction_results(
            recommendation_df
        )

    except FileNotFoundError as error:
        logger.exception(
            "The trained ML model was not found."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "The trained anomaly detection model "
                "could not be found."
            ),
        ) from error

    except Exception as error:
        logger.exception(
            "Location analysis failed during ML processing."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "The weather was retrieved, but the Machine "
                "Learning analysis could not be completed."
            ),
        ) from error

    if recommendation_df.empty:
        raise HTTPException(
            status_code=500,
            detail="No recommendation was generated.",
        )

    result = recommendation_df.iloc[0].to_dict()

    # Add location and live weather values needed by the UI.
    result.update(
        {
            "latitude": weather["latitude"],
            "longitude": weather["longitude"],
            "temp": weather["temp"],
            "humidity": weather["humidity"],
            "pressure": weather["pressure"],
            "sea_level": weather["sea_level"],
            "wind_speed": weather["wind_speed"],
            "clouds": weather["clouds"],
            "rain_1h": weather["rain_1h"],
            "weather_description": weather[
                "weather_description"
            ],
            "weather_status": weather["weather_status"],
        }
    )

    # generated_at is assigned by PostgreSQL, so read the
    # final saved recommendation from the database.
    saved_query = text(
        """
        SELECT
            r.weather_id,
            r.city,
            r.is_anomaly,
            r.anomaly_score,
            r.model_version,
            r.risk_level,
            r.irrigation_action,
            r.spraying_action,
            r.recommendation,
            r.source_timestamp,
            r.generated_at,
            w.latitude,
            w.longitude,
            w.temp,
            w.humidity,
            w.pressure,
            w.sea_level,
            w.wind_speed,
            w.clouds,
            w.rain_1h,
            w.weather_description,
            w.weather_status
        FROM recommendations AS r
        JOIN weather_data AS w
            ON w.id = r.weather_id
        WHERE r.weather_id = :weather_id
        LIMIT 1;
        """
    )

    saved_df = execute_select_query(
        saved_query,
        {"weather_id": weather_id},
    )

    if saved_df.empty:
        raise HTTPException(
            status_code=500,
            detail=(
                "The recommendation was generated but "
                "could not be loaded."
            ),
        )

    return serialize_record(
        saved_df.iloc[0].to_dict()
    )


# ==========================================================
# API Endpoints
# ==========================================================

@app.on_event("startup")
def initialize_auth_storage() -> None:
    create_users_table()


@app.post("/api/v1/auth/register", response_model=AuthResponse, status_code=201, tags=["Authentication"])
def register_user(payload: RegisterRequest) -> dict[str, Any]:
    email = payload.email.lower().strip()
    full_name = " ".join(payload.full_name.split())
    if get_user_by_email(email):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    engine = get_database_engine()
    try:
        with engine.begin() as connection:
            row = connection.execute(
                text("""
                    INSERT INTO users (full_name, email, password_hash)
                    VALUES (:full_name, :email, :password_hash)
                    RETURNING id, full_name, email
                """),
                {"full_name": full_name, "email": email, "password_hash": hash_password(payload.password)},
            ).mappings().one()
    except SQLAlchemyError as error:
        logger.exception("Could not register user.")
        raise HTTPException(status_code=500, detail="The account could not be created.") from error
    finally:
        engine.dispose()

    user = dict(row)
    return {"access_token": create_access_token(user["id"], user["email"]), "token_type": "bearer", "user": user}


@app.post("/api/v1/auth/login", response_model=AuthResponse, tags=["Authentication"])
def login_user(payload: LoginRequest) -> dict[str, Any]:
    user = get_user_by_email(payload.email)
    if not user or not user["is_active"] or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.", headers={"WWW-Authenticate": "Bearer"})

    safe_user = {"id": user["id"], "full_name": user["full_name"], "email": user["email"]}
    return {"access_token": create_access_token(user["id"], user["email"]), "token_type": "bearer", "user": safe_user}


@app.get("/api/v1/auth/me", response_model=UserResponse, tags=["Authentication"])
def read_current_user(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return current_user


@app.get(
    "/api/v1/health",
    tags=["System"],
)
def health_check() -> dict[str, str]:
    """
    Confirm that the API is running.
    """

    return {
        "status": "success",
        "message": "API is up and running.",
    }


@app.get(
    "/api/v1/recommendations",
    tags=["Recommendations"],
)
def get_recent_recommendations(
    limit: int = Query(
        50,
        ge=1,
        le=500,
        description="Number of records to return.",
    ),
) -> list[dict[str, Any]]:
    """
    Return the most recent recommendation records.
    """

    logger.info(
        "Fetching the latest %s recommendations.",
        limit,
    )

    query = text(
        """
        SELECT
            r.weather_id,
            r.city,
            r.is_anomaly,
            r.anomaly_score,
            r.model_version,
            r.risk_level,
            r.irrigation_action,
            r.spraying_action,
            r.recommendation,
            r.source_timestamp,
            r.generated_at,
            w.latitude,
            w.longitude,
            w.temp,
            w.humidity,
            w.pressure,
            w.sea_level,
            w.wind_speed,
            w.clouds,
            w.rain_1h,
            w.weather_description,
            w.weather_status
        FROM recommendations AS r
        LEFT JOIN weather_data AS w
            ON w.id = r.weather_id
        ORDER BY r.generated_at DESC
        LIMIT :limit;
        """
    )

    df = execute_select_query(
        query,
        {"limit": limit},
    )

    if df.empty:
        return []

    return [
        serialize_record(record)
        for record in df.to_dict(orient="records")
    ]


@app.get(
    "/api/v1/recommendations/{city}",
    tags=["Recommendations"],
)
def get_recommendations_by_city(
    city: str = FastAPIPath(
        ...,
        min_length=1,
        description="City name.",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of records to return.",
    ),
) -> list[dict[str, Any]]:
    """
    Return recommendations for one city.
    """

    logger.info(
        "Fetching recommendations for city: %s",
        city,
    )

    query = text(
        """
        SELECT
            r.weather_id,
            r.city,
            r.is_anomaly,
            r.anomaly_score,
            r.model_version,
            r.risk_level,
            r.irrigation_action,
            r.spraying_action,
            r.recommendation,
            r.source_timestamp,
            r.generated_at,
            w.latitude,
            w.longitude,
            w.temp,
            w.humidity,
            w.pressure,
            w.sea_level,
            w.wind_speed,
            w.clouds,
            w.rain_1h,
            w.weather_description,
            w.weather_status
        FROM recommendations AS r
        LEFT JOIN weather_data AS w
            ON w.id = r.weather_id
        WHERE LOWER(r.city) = LOWER(:city)
        ORDER BY r.generated_at DESC
        LIMIT :limit;
        """
    )

    df = execute_select_query(
        query,
        {
            "city": city.strip(),
            "limit": limit,
        },
    )

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No recommendations were found "
                f"for the city: {city}"
            ),
        )

    return [
        serialize_record(record)
        for record in df.to_dict(orient="records")
    ]


@app.post(
    "/api/v1/analyze-location",
    tags=["Location Analysis"],
)
def analyze_location(
    coordinates: LocationAnalysisRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Analyze any valid latitude and longitude.

    Workflow:
    1. Retrieve current weather from OpenWeather.
    2. Save the live weather to PostgreSQL.
    3. Run anomaly detection.
    4. Generate agricultural recommendations.
    5. Save and return the final result.
    """

    logger.info(
        "Analyzing location latitude=%s longitude=%s",
        coordinates.latitude,
        coordinates.longitude,
    )

    weather = fetch_current_weather(
        latitude=coordinates.latitude,
        longitude=coordinates.longitude,
    )

    weather_id = save_weather_record(
        weather
    )

    result = analyze_weather_record(
        weather_id=weather_id,
        weather=weather,
    )

    logger.info(
        "Location analysis completed for weather ID %s.",
        weather_id,
    )

    return result