"""
==========================================================
Feature Engineering Module
==========================================================

This module prepares weather data for Machine Learning.

Responsibilities
----------------
1. Validate the incoming weather dataset.
2. Handle missing values.
3. Generate time-based features.
4. Select ML input features.
5. Prepare datasets for both training and prediction.

Project:
Green Innovation Real-Time Data Pipeline

Author:
Mohamed Hamdy
"""

# ==========================================================
# Import Required Libraries
# ==========================================================

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd


# ==========================================================
# Feature Configuration
# ==========================================================

FEATURE_COLUMNS: List[str] = [
    "temp",
    "humidity",
    "pressure",
    "sea_level",
    "wind_speed",
    "clouds",
    "rain_1h",
    "hour",
    "day",
    "month",
    "season",
]

REQUIRED_COLUMNS: List[str] = [
    "id",
    "city",
    "temp",
    "humidity",
    "pressure",
    "sea_level",
    "wind_speed",
    "clouds",
    "rain_1h",
    "timestamp",
]


# ==========================================================
# Dataset Validation
# ==========================================================

def validate_weather_dataframe(
    weather_df: pd.DataFrame,
) -> None:
    """
    Validate that the incoming dataframe contains all
    required columns before feature engineering starts.
    """

    if weather_df.empty:
        raise ValueError(
            "The weather dataframe is empty."
        )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in weather_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )


# ==========================================================
# Timestamp Processing
# ==========================================================

def convert_timestamp(
    weather_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert Unix timestamp into pandas datetime.
    """

    dataframe = weather_df.copy()

    dataframe["datetime"] = pd.to_datetime(
        dataframe["timestamp"],
        unit="s",
        errors="coerce",
        utc=True,
    ).dt.tz_localize(None)

    return dataframe


# ==========================================================
# Time-Based Features
# ==========================================================

def create_time_features(
    weather_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate time-related ML features.
    """

    dataframe = weather_df.copy()

    dataframe["hour"] = dataframe["datetime"].dt.hour

    dataframe["day"] = dataframe["datetime"].dt.day

    dataframe["month"] = dataframe["datetime"].dt.month

    dataframe["season"] = (
        (dataframe["month"] % 12 + 3) // 3
    )

    return dataframe

# ==========================================================
# Missing Values Handling
# ==========================================================

def handle_missing_values(
    weather_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Handle missing numerical values before training
    or prediction.
    """

    dataframe = weather_df.copy()

    numeric_columns = [
        "temp",
        "humidity",
        "pressure",
        "sea_level",
        "wind_speed",
        "clouds",
        "rain_1h",
    ]

    for column in numeric_columns:

        if column not in dataframe.columns:
            continue

        median_value = dataframe[column].median()

        if pd.isna(median_value):
          raise ValueError(
        f"Column '{column}' contains no valid numerical values."
        )

        dataframe[column] = dataframe[column].fillna(
            median_value
        )

    return dataframe


# ==========================================================
# Feature Selection
# ==========================================================

def select_features(
    weather_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Select only the ML input features.
    """

    dataframe = weather_df.copy()

    return dataframe[FEATURE_COLUMNS]


# ==========================================================
# Feature Data Type Validation
# ==========================================================

def convert_feature_types(
    weather_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert all ML features to numeric values.
    """

    dataframe = weather_df.copy()

    for feature in FEATURE_COLUMNS:

        dataframe[feature] = pd.to_numeric(
            dataframe[feature],
            errors="coerce",
        )

    return dataframe


# ==========================================================
# Remove Duplicate Records
# ==========================================================

def remove_duplicate_records(
    weather_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove duplicated weather records.
    """

    dataframe = weather_df.copy()

    dataframe = dataframe.drop_duplicates(
        subset=["id"],
        keep="last",
    )

    dataframe = dataframe.reset_index(
        drop=True,
    )

    return dataframe

# ==========================================================
# Complete Feature Engineering Pipeline
# ==========================================================

def prepare_features(
    weather_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Execute the complete feature engineering pipeline.

    Pipeline Steps
    --------------
    1. Validate dataset
    2. Remove duplicate records
    3. Convert timestamps
    4. Generate time features
    5. Handle missing values
    6. Convert feature types
    7. Select ML features

    Returns
    -------
    pd.DataFrame
        Clean ML feature dataframe.
    """

    validate_weather_dataframe(weather_df)

    dataframe = remove_duplicate_records(
        weather_df
    )

    dataframe = convert_timestamp(
        dataframe
    )

    dataframe = create_time_features(
        dataframe
    )

    dataframe = handle_missing_values(
        dataframe
    )

    dataframe = convert_feature_types(
        dataframe
    )

    dataframe = select_features(
        dataframe
    )

    return dataframe


# ==========================================================
# Prepare Dataset With Metadata
# ==========================================================

def prepare_dataset(
    weather_df: pd.DataFrame,
):
    """
    Prepare both metadata and ML features.

    Returns
    -------
    tuple
        metadata dataframe,
        ML features dataframe
    """

    validate_weather_dataframe(weather_df)

    metadata = weather_df.copy()

    features = prepare_features(
        weather_df
    )

    return metadata, features


# ==========================================================
# Utility Function
# ==========================================================

def get_feature_names():
    """
    Return the ML feature names.
    """

    return FEATURE_COLUMNS.copy()


# ==========================================================
# Module Test
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("Feature Engineering Module")
    print("=" * 60)

    print("\nSelected Features:")

    for feature in FEATURE_COLUMNS:
        print(f"• {feature}")

    print("\nModule loaded successfully.")