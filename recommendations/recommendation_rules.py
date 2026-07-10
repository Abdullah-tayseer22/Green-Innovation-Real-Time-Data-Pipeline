"""
==========================================================
Agricultural Recommendation Rules
==========================================================

This module combines rule-based agricultural logic with
Machine Learning anomaly detection results to generate
actionable recommendations.

Project:
Green Innovation Real-Time Data Pipeline

Author:
Mohamed Hamdy
"""

# ==========================================================
# Import Required Libraries
# ==========================================================

from __future__ import annotations
from typing import Any

import pandas as pd


# ==========================================================
# Risk Level Utilities
# ==========================================================

RISK_PRIORITY = {
    "normal": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def select_higher_risk(
    current_risk: str,
    new_risk: str,
) -> str:
    """
    Return the higher of two risk levels.
    """

    if RISK_PRIORITY[new_risk] > RISK_PRIORITY[current_risk]:
        return new_risk

    return current_risk


# ==========================================================
# Safe Value Conversion
# ==========================================================

def safe_float(
    value: Any,
) -> float | None:
    """
    Convert a value to float safely.

    Missing or invalid values remain None instead of being
    converted to zero, preventing false recommendations.
    """

    if value is None or pd.isna(value):
        return None

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


def safe_text(
    value: Any,
) -> str:
    """
    Convert a text value safely to lowercase.
    """

    if value is None or pd.isna(value):
        return ""

    return str(value).strip().lower()


# ==========================================================
# Timestamp Preparation
# ==========================================================

def get_source_timestamp(
    row: pd.Series,
):
    """
    Return a readable source timestamp.

    Uses source_timestamp when already available. Otherwise,
    converts the Unix timestamp supplied by weather_data.
    """

    existing_timestamp = row.get("source_timestamp")

    if existing_timestamp is not None and not pd.isna(existing_timestamp):
        return existing_timestamp

    unix_timestamp = row.get("timestamp")

    if unix_timestamp is None or pd.isna(unix_timestamp):
        return None

    return pd.to_datetime(
        unix_timestamp,
        unit="s",
        errors="coerce",
        utc=True,
    ).tz_localize(None)


# ==========================================================
# Generate Recommendation for One Weather Record
# ==========================================================

def evaluate_weather_record(
    row: pd.Series,
) -> dict[str, Any]:
    """
    Evaluate one weather record using weather rules and
    Machine Learning anomaly results.
    """

    temperature = safe_float(row.get("temp"))
    humidity = safe_float(row.get("humidity"))
    wind_speed = safe_float(row.get("wind_speed"))
    rainfall = safe_float(row.get("rain_1h"))
    clouds = safe_float(row.get("clouds"))
    anomaly_score = safe_float(row.get("anomaly_score"))

    weather_description = safe_text(
        row.get("weather_description")
    )

    weather_status = safe_text(
        row.get("weather_status")
    )

    is_anomaly = bool(
        row.get("is_anomaly", False)
    )

    risk_level = "normal"
    messages: list[str] = []

    irrigation_action = (
        "Maintain the normal irrigation schedule and continue monitoring."
    )

    spraying_action = (
        "Weather conditions are suitable for agricultural spraying."
    )

    # ======================================================
    # Machine Learning Result
    # ======================================================

    if is_anomaly:
        risk_level = select_higher_risk(
            risk_level,
            "medium",
        )

        if anomaly_score is not None:
            messages.append(
                "The Machine Learning model detected an unusual weather "
                f"pattern with anomaly score {anomaly_score:.4f}. "
                "Inspect current field conditions and monitor new readings."
            )

        else:
            messages.append(
                "The Machine Learning model detected an unusual weather "
                "pattern. Inspect current field conditions and monitor "
                "new readings."
            )

    # ======================================================
    # Temperature Rules
    # ======================================================

    if temperature is not None:

        if temperature >= 40:
            risk_level = select_higher_risk(
                risk_level,
                "critical",
            )

            messages.append(
                "Extreme heat detected. Protect sensitive crops and avoid "
                "irrigation during peak afternoon temperatures."
            )

            irrigation_action = (
                "Irrigate early in the morning or after sunset to reduce "
                "water evaporation."
            )

        elif temperature >= 35:
            risk_level = select_higher_risk(
                risk_level,
                "high",
            )

            messages.append(
                "High temperature detected. Monitor crops for heat stress."
            )

            irrigation_action = (
                "Prefer irrigation during early morning or evening hours."
            )

        elif temperature <= 2:
            risk_level = select_higher_risk(
                risk_level,
                "critical",
            )

            messages.append(
                "Severe frost risk detected. Apply frost protection "
                "procedures."
            )

            irrigation_action = (
                "Avoid unnecessary irrigation unless required for frost "
                "protection under local agricultural guidance."
            )

        elif temperature <= 5:
            risk_level = select_higher_risk(
                risk_level,
                "high",
            )

            messages.append(
                "Cold conditions detected. Protect frost-sensitive crops."
            )

    # ======================================================
    # Rainfall Rules
    # ======================================================

    if rainfall is not None:

        if rainfall >= 5:
            risk_level = select_higher_risk(
                risk_level,
                "medium",
            )

            messages.append(
                "Significant rainfall detected during the previous hour."
            )

            irrigation_action = (
                "Pause irrigation and inspect drainage conditions."
            )

        elif rainfall >= 1:
            messages.append(
                "Recent rainfall detected."
            )

            irrigation_action = (
                "Delay irrigation and reassess field water requirements."
            )

    # ======================================================
    # Humidity Rules
    # ======================================================

    if humidity is not None:

        if humidity >= 90:
            risk_level = select_higher_risk(
                risk_level,
                "medium",
            )

            messages.append(
                "Very high air humidity may increase the risk of "
                "fungal disease."
            )

            spraying_action = (
                "Inspect crops for fungal symptoms and avoid unnecessary "
                "leaf wetness."
            )

        elif humidity <= 25:
            risk_level = select_higher_risk(
                risk_level,
                "medium",
            )

            messages.append(
                "Very low air humidity may increase crop water loss."
            )

            irrigation_action = (
                "Check soil moisture before increasing irrigation. "
                "Air humidity alone does not confirm dry soil."
            )

    # ======================================================
    # Wind Rules
    # ======================================================

    if wind_speed is not None:

        if wind_speed >= 15:
            risk_level = select_higher_risk(
                risk_level,
                "high",
            )

            messages.append(
                "Very strong wind detected. Crop and infrastructure "
                "damage may occur."
            )

            spraying_action = (
                "Do not spray fertilizers or pesticides during strong winds."
            )

        elif wind_speed >= 8:
            risk_level = select_higher_risk(
                risk_level,
                "medium",
            )

            messages.append(
                "Wind speed is unsuitable for precise agricultural spraying."
            )

            spraying_action = (
                "Postpone spraying until wind speed decreases."
            )

    # ======================================================
    # Storm and Weather Description Rules
    # ======================================================

    if (
        "thunderstorm" in weather_description
        or "storm" in weather_description
        or "thunderstorm" in weather_status
    ):
        risk_level = select_higher_risk(
            risk_level,
            "critical",
        )

        messages.append(
            "Thunderstorm conditions detected. Secure equipment and "
            "avoid field operations."
        )

        irrigation_action = (
            "Stop irrigation until the storm passes and inspect drainage."
        )

        spraying_action = (
            "Suspend all spraying operations."
        )

    if (
        "snow" in weather_description
        or "snow" in weather_status
    ):
        risk_level = select_higher_risk(
            risk_level,
            "high",
        )

        messages.append(
            "Snow conditions detected. Protect vulnerable crops and "
            "greenhouse systems."
        )

    if (
        clouds is not None
        and humidity is not None
        and rainfall is not None
        and clouds >= 90
        and humidity >= 80
        and rainfall == 0
    ):
        messages.append(
            "Dense cloud cover and high humidity detected. "
            "Monitor for possible rainfall."
        )

    # ======================================================
    # Default Recommendation
    # ======================================================

    if not messages:
        messages.append(
            "Current weather conditions do not indicate an immediate "
            "agricultural risk."
        )  

    return {
    "weather_id": int(row["id"]),
    "city": row.get("city"),
    "is_anomaly": is_anomaly,
    "anomaly_score": anomaly_score,
    "model_version": row.get("model_version"),
    "risk_level": risk_level,
    "irrigation_action": irrigation_action,
    "spraying_action": spraying_action,
    "recommendation": " ".join(messages),
    "source_timestamp": get_source_timestamp(row),
}
   


# ==========================================================
# Generate Recommendations for Full DataFrame
# ==========================================================

def generate_recommendations(
    weather_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate one recommendation for every weather record.
    """

    if weather_df.empty:
        return pd.DataFrame(
            columns=[
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
            ]
        )

    recommendation_records = [
        evaluate_weather_record(row)
        for _, row in weather_df.iterrows()
    ]

    return pd.DataFrame(
        recommendation_records
    )