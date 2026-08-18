import os
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "ml",
    "outputs"
)

INPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "maintenance_priority_all.csv"
)

SUMMARY_FILE = os.path.join(
    OUTPUT_DIR,
    "fleet_summary.csv"
)

TOP_ENGINES_FILE = os.path.join(
    OUTPUT_DIR,
    "fleet_top_priority_engines.csv"
)


print("=" * 60)
print("AEROGUARD FLEET ANALYTICS")
print("=" * 60)


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("\nTotal engine records:", len(df))


# ============================================================
# BASIC FLEET METRICS
# ============================================================

total_engines = len(df)

average_rul = df["predicted_RUL"].mean()
average_health = df["health_score"].mean()
average_anomaly = df["anomaly_score"].mean()


# ============================================================
# RISK COUNTS
# ============================================================

risk_counts = (
    df["risk_level"]
    .value_counts()
)


low_count = int(
    risk_counts.get("LOW", 0)
)

medium_count = int(
    risk_counts.get("MEDIUM", 0)
)

high_count = int(
    risk_counts.get("HIGH", 0)
)

critical_count = int(
    risk_counts.get("CRITICAL", 0)
)


# ============================================================
# MAINTENANCE COUNTS
# ============================================================

maintenance_counts = (
    df["maintenance_priority"]
    .value_counts()
)


monitor_count = int(
    maintenance_counts.get(
        "CONTINUE MONITORING",
        0
    )
)

monitor_closely_count = int(
    maintenance_counts.get(
        "MONITOR CLOSELY",
        0
    )
)

schedule_count = int(
    maintenance_counts.get(
        "SCHEDULE MAINTENANCE",
        0
    )
)

immediate_count = int(
    maintenance_counts.get(
        "IMMEDIATE INSPECTION",
        0
    )
)


# ============================================================
# DATASET SUMMARY
# ============================================================

dataset_summary = (
    df.groupby("dataset")
    .agg(
        engines=("engine_id", "count"),
        average_rul=("predicted_RUL", "mean"),
        average_health=("health_score", "mean"),
        average_anomaly=("anomaly_score", "mean")
    )
    .reset_index()
)

print("\n===== DATASET SUMMARY =====")
print(
    dataset_summary.to_string(
        index=False
    )
)


# ============================================================
# FLEET SUMMARY
# ============================================================

summary = pd.DataFrame([
    {
        "total_engines": total_engines,
        "average_predicted_RUL": round(
            average_rul, 2
        ),
        "average_health_score": round(
            average_health, 2
        ),
        "average_anomaly_score": round(
            average_anomaly, 2
        ),
        "low_risk": low_count,
        "medium_risk": medium_count,
        "high_risk": high_count,
        "critical_risk": critical_count,
        "continue_monitoring": monitor_count,
        "monitor_closely": monitor_closely_count,
        "schedule_maintenance": schedule_count,
        "immediate_inspection": immediate_count
    }
])


# ============================================================
# TOP PRIORITY ENGINES
# ============================================================

top_engines = (
    df[
        [
            "dataset",
            "engine_id",
            "predicted_RUL",
            "health_score",
            "anomaly_score",
            "risk_level",
            "priority_score",
            "maintenance_priority",
            "top_abnormal_sensors"
        ]
    ]
    .sort_values(
        "priority_score",
        ascending=False
    )
    .head(20)
)


# ============================================================
# SAVE
# ============================================================

summary.to_csv(
    SUMMARY_FILE,
    index=False
)

top_engines.to_csv(
    TOP_ENGINES_FILE,
    index=False
)


# ============================================================
# DISPLAY
# ============================================================

print("\n===== FLEET OVERVIEW =====")

print(
    "Total engines:",
    total_engines
)

print(
    "Average predicted RUL:",
    round(average_rul, 2)
)

print(
    "Average health score:",
    round(average_health, 2)
)

print(
    "Average anomaly score:",
    round(average_anomaly, 2)
)

print("\nRisk distribution:")

print(
    risk_counts
)

print("\nMaintenance distribution:")

print(
    maintenance_counts
)

print("\n===== TOP 20 PRIORITY ENGINES =====")

print(
    top_engines.to_string(
        index=False
    )
)

print("\nSaved:")
print(SUMMARY_FILE)
print(TOP_ENGINES_FILE)