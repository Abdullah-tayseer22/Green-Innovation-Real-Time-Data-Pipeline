"""
==========================================================
Machine Learning Training Module
==========================================================

This module trains the Machine Learning model using
historical weather data stored in PostgreSQL.

Project:
Green Innovation Real-Time Data Pipeline

Author:
Mohamed Hamdy
"""

# ==========================================================
# Import Required Libraries
# ==========================================================

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from db import (
    get_database_engine,
    load_weather_data,
)

from feature_engineering import (
    prepare_dataset,
    get_feature_names,
)

# ==========================================================
# Logging Configuration
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# ==========================================================
# Model Configuration
# ==========================================================

MODEL_VERSION = "1.0.0"

MODEL_DIRECTORY = (
    Path(__file__).resolve().parent / "models"
)

MODEL_DIRECTORY.mkdir(
    exist_ok=True
)

MODEL_PATH = (
    MODEL_DIRECTORY /
    "weather_anomaly_model.joblib"
)

METADATA_PATH = (
    MODEL_DIRECTORY /
    "model_metadata.json"
)

MINIMUM_RECORDS = 100

CONTAMINATION_RATE = 0.05

RANDOM_STATE = 42

# ==========================================================
# Create Isolation Forest
# ==========================================================

def build_model() -> IsolationForest:
    """
    Create a new Isolation Forest model.
    """

    return IsolationForest(
        n_estimators=200,
        contamination=CONTAMINATION_RATE,
        random_state=RANDOM_STATE,
        bootstrap=False,
        n_jobs=-1,
    )

# ==========================================================
# Load Training Dataset
# ==========================================================

def load_training_dataset():
    """
    Load weather data from PostgreSQL
    and prepare ML features.
    """

    logger.info(
        "Connecting to PostgreSQL..."
    )

    engine = get_database_engine()

    logger.info(
        "Loading weather data..."
    )

    weather_df = load_weather_data(
        engine
    )

    logger.info(
        "Weather records: %s",
        len(weather_df)
    )

    if weather_df.empty:

        raise ValueError(
            "weather_data table is empty."
        )

    metadata_df, features_df = (
        prepare_dataset(
            weather_df
        )
    )

    return (
        metadata_df,
        features_df,
    )

# ==========================================================
# Validate Dataset Size
# ==========================================================

def validate_dataset_size(
    features_df: pd.DataFrame,
):
    """
    Ensure enough data exists before
    training the model.
    """

    total_records = len(
        features_df
    )

    logger.info(
        "Training records: %s",
        total_records
    )

    if total_records < MINIMUM_RECORDS:

        raise ValueError(
            f"""
Not enough historical weather data.

Current records : {total_records}

Required records : {MINIMUM_RECORDS}

Collect more weather data before
training the Machine Learning model.
"""
        )

# ==========================================================
# Train Isolation Forest
# ==========================================================

def train_model():

    logger.info(
        "Loading dataset..."
    )

    metadata_df, features_df = (
        load_training_dataset()
    )

    validate_dataset_size(
        features_df
    )

    logger.info(
        "Building model..."
    )

    model = build_model()

    logger.info(
        "Training Isolation Forest..."
    )

    model.fit(
        features_df
    )

    logger.info(
        "Training completed successfully."
    )

    return (
        model,
        metadata_df,
        features_df,
    )

# ==========================================================
# Generate Predictions On Training Data
# ==========================================================

def evaluate_training_dataset(
    model: IsolationForest,
    metadata_df: pd.DataFrame,
    features_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate anomaly predictions for the
    historical weather dataset.
    """

    logger.info(
        "Evaluating training dataset..."
    )

    predictions = model.predict(
        features_df
    )

    anomaly_scores = model.decision_function(
        features_df
    )

    results_df = metadata_df.copy()

    results_df["prediction"] = predictions

    results_df["is_anomaly"] = (
        results_df["prediction"] == -1
    )

    results_df["anomaly_score"] = (
        anomaly_scores
    )

    anomaly_count = int(
        results_df["is_anomaly"].sum()
    )

    logger.info(
        "Detected anomalies: %s",
        anomaly_count,
    )

    return results_df


# ==========================================================
# Save Trained Model
# ==========================================================

def save_model(
    model: IsolationForest,
) -> None:
    """
    Save trained model.
    """

    logger.info(
        "Saving model..."
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    logger.info(
        "Model saved successfully."
    )


# ==========================================================
# Save Model Metadata
# ==========================================================

def save_metadata(
    results_df: pd.DataFrame,
):
    """
    Save model metadata.
    """

    metadata = {

        "model_version":
            MODEL_VERSION,

        "algorithm":
            "Isolation Forest",

        "trained_at":
            datetime.utcnow().isoformat(),

        "training_records":
            int(len(results_df)),

        "anomalies_detected":
            int(results_df["is_anomaly"].sum()),

        "features":
            get_feature_names(),

        "contamination":
            CONTAMINATION_RATE,

        "random_state":
            RANDOM_STATE,

    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )

    logger.info(
        "Metadata saved successfully."
    )


# ==========================================================
# Print Training Summary
# ==========================================================

def print_training_summary(
    results_df: pd.DataFrame,
):
    """
    Display training statistics.
    """

    print()

    print("=" * 60)

    print("MODEL TRAINING SUMMARY")

    print("=" * 60)

    print(
        f"Records : {len(results_df)}"
    )

    print(
        f"Anomalies : {results_df['is_anomaly'].sum()}"
    )

    print(
        f"Normal : {(~results_df['is_anomaly']).sum()}"
    )

    print(
        f"Model Version : {MODEL_VERSION}"
    )

    print(
        f"Saved Model : {MODEL_PATH}"
    )

    print("=" * 60)

    # ==========================================================
# Complete Training Pipeline
# ==========================================================

def run_training_pipeline():
    """
    Execute the complete Machine Learning
    training pipeline.
    """

    logger.info(
        "Starting Machine Learning pipeline..."
    )

    (
        model,
        metadata_df,
        features_df,
    ) = train_model()

    results_df = evaluate_training_dataset(
        model=model,
        metadata_df=metadata_df,
        features_df=features_df,
    )

    save_model(
        model=model,
    )

    save_metadata(
        results_df,
    )

    print_training_summary(
        results_df,
    )

    logger.info(
        "Machine Learning pipeline completed successfully."
    )

    return (
        model,
        results_df,
    )


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    try:

        run_training_pipeline()

    except Exception as error:

        logger.exception(
            "Training pipeline failed."
        )

        print()

        print("=" * 60)

        print("TRAINING FAILED")

        print("=" * 60)

        print(error)

        print("=" * 60)