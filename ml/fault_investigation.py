import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "ml" / "outputs"

EXPLANATION_FILE = OUTPUT_DIR / "explanations_all.csv"
ANOMALY_FILE = OUTPUT_DIR / "anomaly_detection_final.csv"
MAINTENANCE_FILE = OUTPUT_DIR / "maintenance_priority_all.csv"
PREDICTION_FILE = OUTPUT_DIR / "v3_all_test_predictions.csv"


def investigate(dataset, engine_id):

    predictions = pd.read_csv(PREDICTION_FILE)
    explanations = pd.read_csv(EXPLANATION_FILE)
    anomalies = pd.read_csv(ANOMALY_FILE)
    maintenance = pd.read_csv(MAINTENANCE_FILE)

    # Prediction
    prediction = predictions[
        (predictions["dataset"] == dataset) &
        (predictions["engine_id"] == engine_id)
    ]

    if prediction.empty:
        raise ValueError("Engine not found")

    p = prediction.iloc[0]

    # Maintenance
    m = maintenance[
        (maintenance["dataset"] == dataset) &
        (maintenance["engine_id"] == engine_id)
    ]

    # SHAP
    e = explanations[
        (explanations["dataset"] == dataset) &
        (explanations["engine_id"] == engine_id)
    ].copy()

    e["absolute_impact"] = e["shap_value"].abs()

    e = e.sort_values(
        "absolute_impact",
        ascending=False
    ).head(10)

    contributors = []

    for _, row in e.iterrows():

        impact = float(row["shap_value"])

        contributors.append({
            "feature": row["feature"],
            "impact": round(impact, 4),
            "effect": (
                "increased predicted RUL"
                if impact > 0
                else "decreased predicted RUL"
            )
        })

    # Anomaly
    a = anomalies[
        (anomalies["dataset"] == dataset) &
        (anomalies["unit_id"] == engine_id)
    ]

    if not a.empty:

        latest = a.sort_values(
            "cycle"
        ).iloc[-1]

        sensor_text = str(
            latest["top_abnormal_sensors"]
        )

        if sensor_text in [
            "none",
            "insufficient_history",
            "nan"
        ]:
            abnormal_sensors = []
        else:
            abnormal_sensors = [
                x.strip()
                for x in sensor_text.split(",")
            ]

        anomaly_score = float(
            latest["anomaly_score"]
        )

        anomaly_status = latest["status"]

    else:

        abnormal_sensors = []
        anomaly_score = 0
        anomaly_status = "NORMAL"

    result = {
        "dataset": dataset,
        "engine_id": engine_id,
        "predicted_rul": round(
            float(p["predicted_RUL"]), 2
        ),
        "actual_rul": round(
            float(p["actual_RUL"]), 2
        ),
        "anomaly_score": round(
            anomaly_score, 2
        ),
        "anomaly_status": anomaly_status,
        "top_abnormal_sensors": abnormal_sensors,
        "contributors": contributors
    }

    if not m.empty:

        maintenance_row = m.iloc[0]

        result["health_score"] = round(
            float(maintenance_row["health_score"]),
            2
        )

        result["risk"] = maintenance_row[
            "risk_level"
        ]

        result["priority_score"] = round(
            float(maintenance_row["priority_score"]),
            2
        )

        result["maintenance_priority"] = (
            maintenance_row[
                "maintenance_priority"
            ]
        )

        result["maintenance_recommendation"] = (
            maintenance_row[
                "maintenance_recommendation"
            ]
        )

    return result


if __name__ == "__main__":

    print("=" * 60)
    print("AEROGUARD FAULT INVESTIGATION")
    print("=" * 60)

    result = investigate(
        "FD001",
        20
    )

    print("\nEngine:", result["engine_id"])
    print("Predicted RUL:", result["predicted_rul"])
    print("Risk:", result.get("risk"))
    print(
        "Anomaly:",
        result["anomaly_status"]
    )

    print("\nTop contributing factors:")

    for item in result["contributors"]:
        print(
            f"{item['feature']}: "
            f"{item['impact']} "
            f"({item['effect']})"
        )

    print("\nTop abnormal sensors:")

    for sensor in result["top_abnormal_sensors"]:
        print(sensor)

    print("\nFault investigation complete.")