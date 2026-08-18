import os
import pandas as pd
import numpy as np


# ============================================================
# AEROGUARD - MAINTENANCE PRIORITY ENGINE
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "ml",
    "outputs"
)

PREDICTION_FILE = os.path.join(
    OUTPUT_DIR,
    "v3_all_test_predictions.csv"
)

ANOMALY_FILE = os.path.join(
    OUTPUT_DIR,
    "anomaly_detection_final.csv"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "maintenance_priority_all.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("AEROGUARD MAINTENANCE PRIORITY ENGINE")
print("=" * 60)

print("\nLoading final V3 predictions...")

predictions = pd.read_csv(
    PREDICTION_FILE
)

print(
    f"Prediction records: {len(predictions)}"
)

print("\nLoading final anomaly data...")

anomalies = pd.read_csv(
    ANOMALY_FILE
)

print(
    f"Anomaly records: {len(anomalies)}"
)


# ============================================================
# GET LATEST ANOMALY RECORD PER ENGINE
# ============================================================

latest_anomaly = (
    anomalies
    .sort_values(
        ["dataset", "unit_id", "cycle"]
    )
    .groupby(
        ["dataset", "unit_id"],
        as_index=False
    )
    .tail(1)
)

latest_anomaly = latest_anomaly[
    [
        "dataset",
        "unit_id",
        "cycle",
        "anomaly_score",
        "status",
        "top_abnormal_sensors"
    ]
].copy()

latest_anomaly = latest_anomaly.rename(
    columns={
        "unit_id": "engine_id",
        "status": "anomaly_status"
    }
)


# ============================================================
# MERGE PREDICTION + ANOMALY
# ============================================================

df = predictions.merge(
    latest_anomaly,
    on=["dataset", "engine_id"],
    how="left"
)


# ============================================================
# MISSING ANOMALY VALUES
# ============================================================

df["anomaly_score"] = (
    df["anomaly_score"]
    .fillna(0)
)

df["anomaly_status"] = (
    df["anomaly_status"]
    .fillna("NORMAL")
)

df["top_abnormal_sensors"] = (
    df["top_abnormal_sensors"]
    .fillna("none")
)


# ============================================================
# HEALTH SCORE
# ============================================================

# RUL contribution
#
# >= 120 cycles  -> excellent
# 0 cycles       -> poor

rul_score = (
    df["predicted_RUL"] / 120 * 100
)

rul_score = (
    rul_score
    .clip(0, 100)
)


# Anomaly contribution
#
# Higher anomaly score = lower health

anomaly_health = (
    100 - df["anomaly_score"]
)

anomaly_health = (
    anomaly_health
    .clip(0, 100)
)


# ============================================================
# COMBINED HEALTH SCORE
# ============================================================

df["health_score"] = (
    0.70 * rul_score
    +
    0.30 * anomaly_health
)

df["health_score"] = (
    df["health_score"]
    .clip(0, 100)
    .round(2)
)


# ============================================================
# MAINTENANCE PRIORITY SCORE
# ============================================================

# Higher score = more urgent

rul_urgency = (
    100 - rul_score
)

anomaly_urgency = (
    df["anomaly_score"]
)

priority_score = (
    0.60 * rul_urgency
    +
    0.40 * anomaly_urgency
)

df["priority_score"] = (
    priority_score
    .clip(0, 100)
    .round(2)
)


# ============================================================
# RISK LEVEL
# ============================================================

def calculate_risk(row):

    if (
        row["predicted_RUL"] <= 20
        or
        row["anomaly_score"] >= 97
    ):
        return "CRITICAL"

    elif (
        row["predicted_RUL"] <= 50
        or
        row["anomaly_score"] >= 85
    ):
        return "HIGH"

    elif (
        row["predicted_RUL"] <= 80
        or
        row["anomaly_score"] >= 70
    ):
        return "MEDIUM"

    else:
        return "LOW"


df["risk_level"] = df.apply(
    calculate_risk,
    axis=1
)


# ============================================================
# MAINTENANCE PRIORITY
# ============================================================

def calculate_priority(row):

    if row["risk_level"] == "CRITICAL":

        return "IMMEDIATE INSPECTION"

    elif row["risk_level"] == "HIGH":

        return "SCHEDULE MAINTENANCE"

    elif row["risk_level"] == "MEDIUM":

        return "MONITOR CLOSELY"

    else:

        return "CONTINUE MONITORING"


df["maintenance_priority"] = df.apply(
    calculate_priority,
    axis=1
)


# ============================================================
# MAINTENANCE RECOMMENDATION
# ============================================================

def recommendation(row):

    if row["risk_level"] == "CRITICAL":

        return (
            f"Engine requires immediate inspection. "
            f"Predicted RUL is "
            f"{row['predicted_RUL']:.1f} cycles."
        )

    elif row["risk_level"] == "HIGH":

        return (
            f"Schedule maintenance soon. "
            f"Predicted RUL is "
            f"{row['predicted_RUL']:.1f} cycles."
        )

    elif row["risk_level"] == "MEDIUM":

        return (
            f"Monitor engine closely. "
            f"Predicted RUL is "
            f"{row['predicted_RUL']:.1f} cycles."
        )

    else:

        return (
            f"Continue normal monitoring. "
            f"Predicted RUL is "
            f"{row['predicted_RUL']:.1f} cycles."
        )


df["maintenance_recommendation"] = df.apply(
    recommendation,
    axis=1
)


# ============================================================
# SELECT FINAL COLUMNS
# ============================================================

final_columns = [
    "dataset",
    "engine_id",
    "actual_RUL",
    "predicted_RUL",
    "error",
    "cycle",
    "health_score",
    "anomaly_score",
    "anomaly_status",
    "risk_level",
    "priority_score",
    "maintenance_priority",
    "maintenance_recommendation",
    "top_abnormal_sensors"
]

final_df = df[
    final_columns
].copy()


# ============================================================
# SORT BY PRIORITY
# ============================================================

final_df = final_df.sort_values(
    "priority_score",
    ascending=False
)


# ============================================================
# SAVE
# ============================================================

final_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("MAINTENANCE PRIORITY SUMMARY")
print("=" * 60)

print(
    "\nTotal engines:",
    len(final_df)
)

print(
    "\nRisk distribution:"
)

print(
    final_df["risk_level"]
    .value_counts()
)

print(
    "\nMaintenance priority:"
)

print(
    final_df["maintenance_priority"]
    .value_counts()
)

print(
    "\nTop 20 engines requiring attention:"
)

print(
    final_df[
        [
            "dataset",
            "engine_id",
            "predicted_RUL",
            "health_score",
            "anomaly_score",
            "risk_level",
            "maintenance_priority"
        ]
    ]
    .head(20)
    .to_string(index=False)
)

print(
    "\nSaved:"
)

print(OUTPUT_FILE)