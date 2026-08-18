import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "ml" / "outputs"

COLUMNS = (
    ["unit_id", "cycle", "setting_1", "setting_2", "setting_3"]
    + [f"sensor_{i}" for i in range(1, 22)]
)

DATASETS = ["FD001", "FD002", "FD003", "FD004"]


def load_test_data(dataset):

    test_file = (
        DATA_DIR /
        dataset /
        f"test_{dataset}.txt"
    )

    if not test_file.exists():
        raise FileNotFoundError(
            f"Test file not found: {test_file}"
        )

    return pd.read_csv(
        test_file,
        sep=r"\s+",
        header=None,
        names=COLUMNS
    )


def load_predictions():

    prediction_file = (
        OUTPUT_DIR /
        "v3_all_test_predictions.csv"
    )

    if not prediction_file.exists():
        raise FileNotFoundError(
            f"Prediction file not found: {prediction_file}"
        )

    return pd.read_csv(prediction_file)


def load_anomalies():

    anomaly_file = (
        OUTPUT_DIR /
        "anomaly_detection_final.csv"
    )

    if not anomaly_file.exists():
        raise FileNotFoundError(
            f"Anomaly file not found: {anomaly_file}"
        )

    return pd.read_csv(anomaly_file)


def create_timeline(dataset, engine_id):

    test = load_test_data(dataset)

    predictions = load_predictions()
    anomalies = load_anomalies()

    # --------------------------------------------------
    # ENGINE TELEMETRY
    # --------------------------------------------------

    engine = test[
        test["unit_id"] == engine_id
    ].copy()

    if engine.empty:
        raise ValueError(
            f"Engine {engine_id} not found in {dataset}"
        )

    engine = engine.sort_values(
        "cycle"
    ).reset_index(drop=True)

    # --------------------------------------------------
    # ENGINE PREDICTION
    # --------------------------------------------------

    prediction = predictions[
        (predictions["dataset"] == dataset) &
        (predictions["engine_id"] == engine_id)
    ]

    if prediction.empty:
        raise ValueError(
            f"Prediction not found for {dataset} engine {engine_id}"
        )

    predicted_rul = float(
        prediction.iloc[0]["predicted_RUL"]
    )

    actual_rul = float(
        prediction.iloc[0]["actual_RUL"]
    )

    # --------------------------------------------------
    # ENGINE ANOMALY DATA
    # --------------------------------------------------

    anomaly = anomalies[
        (anomalies["dataset"] == dataset) &
        (anomalies["unit_id"] == engine_id)
    ].copy()

    anomaly = anomaly.sort_values(
        "cycle"
    )

    # --------------------------------------------------
    # NORMALIZE ANOMALY SCORE
    # --------------------------------------------------

    if not anomaly.empty:

        anomaly["anomaly_score"] = pd.to_numeric(
            anomaly["anomaly_score"],
            errors="coerce"
        ).fillna(0)

        anomaly_lookup = anomaly[
            ["cycle", "anomaly_score", "status"]
        ]

        engine = engine.merge(
            anomaly_lookup,
            on="cycle",
            how="left"
        )

    else:

        engine["anomaly_score"] = 0
        engine["status"] = "NORMAL"

    engine["anomaly_score"] = (
        engine["anomaly_score"]
        .fillna(0)
    )

    engine["status"] = (
        engine["status"]
        .fillna("NORMAL")
    )

    # --------------------------------------------------
    # HEALTH ESTIMATION
    # --------------------------------------------------

    max_cycle = engine["cycle"].max()

    engine["cycle_progress"] = (
        engine["cycle"] / max_cycle
    )

    # Health decreases as engine progresses.
    engine["health_score"] = (
        100 * (1 - engine["cycle_progress"])
    )

    # Anomaly impact
    anomaly_impact = (
        engine["anomaly_score"] * 0.25
    )

    engine["health_score"] = (
        engine["health_score"] -
        anomaly_impact
    ).clip(0, 100)

    # --------------------------------------------------
    # RUL TREND
    # --------------------------------------------------

    # Estimate remaining RUL at each historical cycle
    # relative to the final predicted RUL.

    remaining_cycles = (
        max_cycle - engine["cycle"]
    )

    engine["estimated_rul"] = (
        remaining_cycles +
        predicted_rul
    )

    engine["estimated_rul"] = (
        engine["estimated_rul"]
        .clip(lower=0)
    )

    # --------------------------------------------------
    # DEGRADATION LEVEL
    # --------------------------------------------------

    def get_degradation_status(row):

        if row["status"] == "CRITICAL":
            return "CRITICAL"

        if row["status"] == "WARNING":
            return "WARNING"

        if row["health_score"] < 30:
            return "CRITICAL"

        if row["health_score"] < 60:
            return "WARNING"

        return "NORMAL"

    engine["degradation_status"] = (
        engine.apply(
            get_degradation_status,
            axis=1
        )
    )

    # --------------------------------------------------
    # SELECT OUTPUT
    # --------------------------------------------------

    timeline = engine[
        [
            "cycle",
            "estimated_rul",
            "health_score",
            "anomaly_score",
            "status",
            "degradation_status"
        ]
    ].copy()

    timeline["cycle"] = (
        timeline["cycle"].astype(int)
    )

    timeline["estimated_rul"] = (
        timeline["estimated_rul"].round(2)
    )

    timeline["health_score"] = (
        timeline["health_score"].round(2)
    )

    timeline["anomaly_score"] = (
        timeline["anomaly_score"].round(2)
    )

    return timeline, predicted_rul, actual_rul


def process_all_engines():

    print("=" * 60)
    print("AEROGUARD DEGRADATION TIMELINE")
    print("=" * 60)

    all_timelines = []

    predictions = load_predictions()

    for _, row in predictions.iterrows():

        dataset = row["dataset"]
        engine_id = int(row["engine_id"])

        try:

            timeline, predicted_rul, actual_rul = (
                create_timeline(
                    dataset,
                    engine_id
                )
            )

            timeline.insert(
                0,
                "engine_id",
                engine_id
            )

            timeline.insert(
                0,
                "dataset",
                dataset
            )

            all_timelines.append(
                timeline
            )

        except Exception as e:

            print(
                f"Skipping {dataset} Engine {engine_id}: {e}"
            )

    final = pd.concat(
        all_timelines,
        ignore_index=True
    )

    output_file = (
        OUTPUT_DIR /
        "degradation_timeline_all.csv"
    )

    final.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 60)
    print("DEGRADATION TIMELINE COMPLETE")
    print("=" * 60)

    print(
        "Total engines:",
        final.groupby(
            ["dataset", "engine_id"]
        ).ngroups
    )

    print(
        "Total timeline records:",
        len(final)
    )

    print("\nSaved:")
    print(output_file)


if __name__ == "__main__":
    process_all_engines()