import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "ml" / "outputs"

PREDICTION_FILE = OUTPUT_DIR / "v3_all_test_predictions.csv"
MAINTENANCE_FILE = OUTPUT_DIR / "maintenance_priority_all.csv"
ANOMALY_FILE = OUTPUT_DIR / "anomaly_detection_final.csv"


def compare_engines(dataset, engine1_id, engine2_id):

    predictions = pd.read_csv(PREDICTION_FILE)
    maintenance = pd.read_csv(MAINTENANCE_FILE)
    anomalies = pd.read_csv(ANOMALY_FILE)

    def get_engine(engine_id):

        p = predictions[
            (predictions["dataset"] == dataset) &
            (predictions["engine_id"] == engine_id)
        ]

        m = maintenance[
            (maintenance["dataset"] == dataset) &
            (maintenance["engine_id"] == engine_id)
        ]

        a = anomalies[
            (anomalies["dataset"] == dataset) &
            (anomalies["unit_id"] == engine_id)
        ]

        if p.empty:
            raise ValueError(
                f"Engine {engine_id} not found"
            )

        prediction = p.iloc[0]

        if not m.empty:
            maintenance_row = m.iloc[0]
        else:
            maintenance_row = None

        if not a.empty:
            latest_anomaly = (
                a.sort_values("cycle").iloc[-1]
            )
        else:
            latest_anomaly = None

        result = {
            "engine_id": engine_id,
            "predicted_rul": round(
                float(prediction["predicted_RUL"]),
                2
            ),
            "actual_rul": round(
                float(prediction["actual_RUL"]),
                2
            )
        }

        if maintenance_row is not None:

            result["health_score"] = round(
                float(
                    maintenance_row["health_score"]
                ),
                2
            )

            result["risk"] = (
                maintenance_row["risk_level"]
            )

            result["priority_score"] = round(
                float(
                    maintenance_row["priority_score"]
                ),
                2
            )

            result["maintenance_priority"] = (
                maintenance_row[
                    "maintenance_priority"
                ]
            )

        else:

            result["health_score"] = None
            result["risk"] = "UNKNOWN"
            result["priority_score"] = None
            result["maintenance_priority"] = "UNKNOWN"

        if latest_anomaly is not None:

            result["anomaly_score"] = round(
                float(
                    latest_anomaly["anomaly_score"]
                ),
                2
            )

            result["anomaly_status"] = (
                latest_anomaly["status"]
            )

            sensor_text = str(
                latest_anomaly[
                    "top_abnormal_sensors"
                ]
            )

            if sensor_text in [
                "none",
                "insufficient_history",
                "nan"
            ]:
                result["top_abnormal_sensors"] = []
            else:
                result["top_abnormal_sensors"] = [
                    x.strip()
                    for x in sensor_text.split(",")
                ]

        else:

            result["anomaly_score"] = None
            result["anomaly_status"] = "UNKNOWN"
            result["top_abnormal_sensors"] = []

        return result

    engine1 = get_engine(engine1_id)
    engine2 = get_engine(engine2_id)

    # --------------------------------------------------
    # DETERMINE BETTER ENGINE
    # --------------------------------------------------

    score1 = 0
    score2 = 0

    if engine1["predicted_rul"] > engine2["predicted_rul"]:
        score1 += 1
    else:
        score2 += 1

    if engine1["health_score"] > engine2["health_score"]:
        score1 += 1
    else:
        score2 += 1

    if engine1["anomaly_score"] < engine2["anomaly_score"]:
        score1 += 1
    else:
        score2 += 1

    if engine1["priority_score"] < engine2["priority_score"]:
        score1 += 1
    else:
        score2 += 1

    if score1 > score2:
        better_engine = engine1_id
    elif score2 > score1:
        better_engine = engine2_id
    else:
        better_engine = "TIE"

    return {
        "dataset": dataset,
        "engine_1": engine1,
        "engine_2": engine2,
        "better_engine": better_engine,
        "comparison_score": {
            f"engine_{engine1_id}": score1,
            f"engine_{engine2_id}": score2
        }
    }


if __name__ == "__main__":

    print("=" * 60)
    print("AEROGUARD ENGINE COMPARISON")
    print("=" * 60)

    result = compare_engines(
        "FD001",
        20,
        34
    )

    print("\nDataset:", result["dataset"])

    print("\nENGINE 1")
    print(result["engine_1"])

    print("\nENGINE 2")
    print(result["engine_2"])

    print(
        "\nBetter engine:",
        result["better_engine"]
    )

    print(
        "\nComparison score:",
        result["comparison_score"]
    )

    print("\nEngine comparison complete.")