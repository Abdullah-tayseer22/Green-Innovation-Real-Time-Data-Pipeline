"""
==========================================================
Machine Learning Recommendation Pipeline Controller
==========================================================

This module is the main entry point for the Analytics and
Machine Learning layer.

It performs the following operations:

1. Connect to PostgreSQL.
2. Check whether a trained ML model exists.
3. Train the Isolation Forest model when required.
4. Run anomaly predictions on weather records.
5. Generate agricultural recommendations.
6. Save recommendations to PostgreSQL.

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
import sys
from pathlib import Path

from db import (
    get_database_engine,
    load_weather_data,
)

from predict import (
    MODEL_PATH,
    execute_prediction_pipeline,
)

from train_model import (
    MINIMUM_RECORDS,
    run_training_pipeline,
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
# Check Available Weather Records
# ==========================================================

def get_weather_record_count() -> int:
    """
    Return the total number of records stored
    in the weather_data PostgreSQL table.
    """

    engine = get_database_engine()

    weather_df = load_weather_data(
        engine
    )

    return len(weather_df)


# ==========================================================
# Check Whether Model Exists
# ==========================================================

def model_exists() -> bool:
    """
    Check whether the trained Isolation Forest
    model file exists.
    """

    return Path(MODEL_PATH).exists()


# ==========================================================
# Train Model When Required
# ==========================================================

def ensure_model_is_available() -> bool:
    """
    Ensure that a trained model is available.

    Returns True when the model already exists or
    training completes successfully.

    Returns False when insufficient data is available.
    """

    if model_exists():

        logger.info(
            "A trained Machine Learning model already exists."
        )

        return True

    logger.info(
        "No trained Machine Learning model was found."
    )

    record_count = get_weather_record_count()

    logger.info(
        "Available weather records: %s",
        record_count,
    )

    if record_count < MINIMUM_RECORDS:

        logger.warning(
            "The model requires at least %s records, "
            "but only %s records are currently available.",
            MINIMUM_RECORDS,
            record_count,
        )

        print()
        print("=" * 60)
        print("MODEL TRAINING IS NOT READY")
        print("=" * 60)
        print(
            f"Available weather records: {record_count}"
        )
        print(
            f"Required weather records: {MINIMUM_RECORDS}"
        )
        print(
            "Run the ingestion and processing pipeline "
            "until enough historical records are stored."
        )
        print("=" * 60)

        return False

    logger.info(
        "Starting initial Machine Learning model training."
    )

    run_training_pipeline()

    return model_exists()


# ==========================================================
# Execute Complete ML Recommendation Layer
# ==========================================================

def run_ml_recommendation_system() -> None:
    """
    Execute the complete Machine Learning and
    agricultural recommendation workflow.
    """

    logger.info(
        "Starting Green Innovation ML recommendation system."
    )

    model_is_ready = ensure_model_is_available()

    if not model_is_ready:

        logger.warning(
            "Prediction was skipped because no trained model "
            "is currently available."
        )

        return

    logger.info(
        "Running weather anomaly prediction and "
        "agricultural recommendation generation."
    )

    recommendation_df = execute_prediction_pipeline(
        last_processed_id=0,
    )

    if recommendation_df is None or recommendation_df.empty:

        logger.info(
            "No recommendations were generated."
        )

        return

    logger.info(
        "%s recommendation record(s) were processed successfully.",
        len(recommendation_df),
    )

    logger.info(
        "Green Innovation ML recommendation system "
        "completed successfully."
    )


# ==========================================================
# Application Entry Point
# ==========================================================

if __name__ == "__main__":

    try:

        run_ml_recommendation_system()

    except KeyboardInterrupt:

        logger.warning(
            "Execution was stopped by the user."
        )

        sys.exit(130)

    except Exception as error:

        logger.exception(
            "The ML recommendation system failed."
        )

        print()
        print("=" * 60)
        print("SYSTEM EXECUTION FAILED")
        print("=" * 60)
        print(error)
        print("=" * 60)

        sys.exit(1)