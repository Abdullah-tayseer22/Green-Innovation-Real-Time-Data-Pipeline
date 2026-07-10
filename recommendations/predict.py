"""
==========================================================
Prediction Module
==========================================================

This module loads the trained Machine Learning model,
reads new weather records from PostgreSQL,
predicts anomalies,
generates agricultural recommendations,
and saves them back to PostgreSQL.

Project:
Green Innovation Real-Time Data Pipeline

Author:
Mohamed Hamdy
"""

# ==========================================================
# Import Required Libraries
# ==========================================================

from __future__ import annotations

import logging
from pathlib import Path

import joblib
import pandas as pd

from db import (
    get_database_engine,
    load_new_weather_data,
    create_recommendations_table,
    save_recommendations,
)

from feature_engineering import (
    prepare_dataset,
)

from recommendation_rules import (
    generate_recommendations,
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
# Model Location
# ==========================================================

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "weather_anomaly_model.joblib"
)

# ==========================================================
# Load Trained Model
# ==========================================================

def load_model():
    """
    Load the trained Isolation Forest model.
    """

    logger.info(
        "Loading trained model..."
    )

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found:\n{MODEL_PATH}"
        )

    model = joblib.load(
        MODEL_PATH
    )

    logger.info(
        "Model loaded successfully."
    )

    return model

# ==========================================================
# Predict Weather Anomalies
# ==========================================================

def predict_weather(
    model,
    weather_df: pd.DataFrame,
):

    metadata_df, features_df = prepare_dataset(
        weather_df
    )

    predictions = model.predict(
        features_df
    )

    scores = model.decision_function(
        features_df
    )

    metadata_df["prediction"] = predictions

    metadata_df["is_anomaly"] = (
        metadata_df["prediction"] == -1
    )

    metadata_df["anomaly_score"] = scores

    return metadata_df

# ==========================================================
# Generate Recommendations
# ==========================================================

def build_recommendations(
    prediction_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate agricultural recommendations
    from prediction results.
    """

    logger.info(
        "Generating recommendations..."
    )

    recommendation_df = generate_recommendations(
        prediction_df
    )

    logger.info(
        "Recommendations generated successfully."
    )

    return recommendation_df


# ==========================================================
# Save Recommendation Results
# ==========================================================

def save_prediction_results(
    recommendation_df: pd.DataFrame,
):
    """
    Save recommendations to PostgreSQL.
    """

    engine = get_database_engine()

    create_recommendations_table(
        engine
    )

    inserted_rows = save_recommendations(
        recommendation_df,
        engine,
    )

    logger.info(
        "%s recommendation(s) saved.",
        inserted_rows,
    )

    return inserted_rows


# ==========================================================
# Prediction Pipeline
# ==========================================================

def run_prediction_pipeline(
    last_processed_id: int = 0,
):
    """
    Execute the prediction workflow.
    """

    logger.info(
        "Starting prediction pipeline..."
    )

    engine = get_database_engine()

    weather_df = load_new_weather_data(
        engine=engine,
        last_processed_id=last_processed_id,
    )

    if weather_df.empty:

        logger.info(
            "No new weather records found."
        )

        return None

    logger.info(
        "%s new weather record(s) found.",
        len(weather_df),
    )

    model = load_model()

    prediction_df = predict_weather(
        model=model,
        weather_df=weather_df,
    )

    recommendation_df = build_recommendations(
        prediction_df
    )

    save_prediction_results(
        recommendation_df
    )

    logger.info(
        "Prediction pipeline completed successfully."
    )

    return recommendation_df

# ==========================================================
# Print Prediction Summary
# ==========================================================

def print_prediction_summary(
    recommendation_df: pd.DataFrame,
) -> None:
    """
    Display a summary of generated agricultural
    recommendations.
    """

    if recommendation_df is None or recommendation_df.empty:
        print()
        print("=" * 60)
        print("PREDICTION SUMMARY")
        print("=" * 60)
        print("No new weather records were processed.")
        print("=" * 60)
        return

    print()
    print("=" * 60)
    print("PREDICTION SUMMARY")
    print("=" * 60)

    print(
        f"Processed records: {len(recommendation_df)}"
    )

    print("\nRisk level distribution:")

    risk_counts = (
        recommendation_df["risk_level"]
        .value_counts()
        .to_dict()
    )

    for risk_level, count in risk_counts.items():
        print(
            f"- {risk_level}: {count}"
        )

    print("=" * 60)


# ==========================================================
# Complete Prediction Execution
# ==========================================================

def execute_prediction_pipeline(
    last_processed_id: int = 0,
) -> pd.DataFrame | None:
    """
    Run the prediction pipeline and display
    the final result summary.
    """

    recommendation_df = run_prediction_pipeline(
        last_processed_id=last_processed_id,
    )

    print_prediction_summary(
        recommendation_df
    )

    return recommendation_df


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    try:

        execute_prediction_pipeline(
            last_processed_id=0,
        )

    except Exception as error:

        logger.exception(
            "Prediction pipeline failed."
        )

        print()
        print("=" * 60)
        print("PREDICTION FAILED")
        print("=" * 60)
        print(error)
        print("=" * 60)