from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os


# ============================================================
# AEROGUARD FASTAPI BACKEND
# ============================================================

app = FastAPI(
    title="AeroGuard API",
    description="AI-powered aircraft engine predictive maintenance API",
    version="2.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATHS
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

MAINTENANCE_FILE = os.path.join(
    OUTPUT_DIR,
    "maintenance_priority_all.csv"
)

FLEET_SUMMARY_FILE = os.path.join(
    OUTPUT_DIR,
    "fleet_summary.csv"
)

FLEET_TOP_FILE = os.path.join(
    OUTPUT_DIR,
    "fleet_top_priority_engines.csv"
)


# ============================================================
# DATA LOADING
# ============================================================

def load_csv(path, name):

    if not os.path.exists(path):

        raise HTTPException(
            status_code=500,
            detail=f"{name} not found"
        )

    return pd.read_csv(path)


def load_predictions():

    return load_csv(
        PREDICTION_FILE,
        "v3_all_test_predictions.csv"
    )


def load_anomalies():

    return load_csv(
        ANOMALY_FILE,
        "anomaly_detection_final.csv"
    )


def load_maintenance():

    return load_csv(
        MAINTENANCE_FILE,
        "maintenance_priority_all.csv"
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "project": "AeroGuard",
        "status": "online",
        "version": "2.0.0",
        "message": (
            "AI-powered aircraft engine "
            "predictive maintenance API"
        )
    }


# ============================================================
# API HEALTH
# ============================================================

@app.get("/api/health")
def api_health():

    return {
        "status": "online",
        "model": "XGBoost V3",
        "anomaly_detection": "Isolation Forest",
        "explainability": "SHAP",
        "datasets": [
            "FD001",
            "FD002",
            "FD003",
            "FD004"
        ],
        "total_test_engines": 707
    }


# ============================================================
# AVAILABLE DATASETS
# ============================================================

@app.get("/api/datasets")
def get_datasets():

    return {
        "datasets": [
            {
                "id": "FD001",
                "description": "C-MAPSS FD001"
            },
            {
                "id": "FD002",
                "description": "C-MAPSS FD002"
            },
            {
                "id": "FD003",
                "description": "C-MAPSS FD003"
            },
            {
                "id": "FD004",
                "description": "C-MAPSS FD004"
            }
        ]
    }


# ============================================================
# DATASET VALIDATION
# ============================================================

def validate_dataset(dataset):

    dataset = dataset.upper()

    allowed = [
        "FD001",
        "FD002",
        "FD003",
        "FD004"
    ]

    if dataset not in allowed:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid dataset '{dataset}'. "
                f"Use FD001, FD002, FD003 or FD004."
            )
        )

    return dataset


# ============================================================
# GET ALL ENGINES
# DEFAULT = FD001
# ============================================================

@app.get("/api/engines")
def get_engines():

    df = load_maintenance()

    df = df[
        df["dataset"] == "FD001"
    ]

    engines = []

    for _, row in df.iterrows():

        engines.append({
            "dataset": row["dataset"],
            "engine_id": int(row["engine_id"]),
            "rul": round(
                float(row["predicted_RUL"]),
                2
            ),
            "health_score": round(
                float(row["health_score"]),
                2
            ),
            "anomaly_score": round(
                float(row["anomaly_score"]),
                2
            ),
            "risk": row["risk_level"],
            "maintenance_priority": (
                row["maintenance_priority"]
            )
        })

    return {
        "dataset": "FD001",
        "count": len(engines),
        "engines": engines
    }


# ============================================================
# GET ALL ENGINES FOR A DATASET
# ============================================================

@app.get("/api/engines/{dataset}")
def get_dataset_engines(dataset: str):

    dataset = validate_dataset(dataset)

    df = load_maintenance()

    df = df[
        df["dataset"] == dataset
    ]

    if df.empty:

        raise HTTPException(
            status_code=404,
            detail=f"No engines found for {dataset}"
        )

    engines = []

    for _, row in df.iterrows():

        engines.append({
            "dataset": dataset,
            "engine_id": int(row["engine_id"]),
            "rul": round(
                float(row["predicted_RUL"]),
                2
            ),
            "health_score": round(
                float(row["health_score"]),
                2
            ),
            "anomaly_score": round(
                float(row["anomaly_score"]),
                2
            ),
            "risk": row["risk_level"],
            "maintenance_priority": (
                row["maintenance_priority"]
            )
        })

    return {
        "dataset": dataset,
        "count": len(engines),
        "engines": engines
    }


# ============================================================
# SINGLE ENGINE
# ============================================================

@app.get("/api/engines/{dataset}/{engine_id}")
def get_engine(
    dataset: str,
    engine_id: int
):

    dataset = validate_dataset(dataset)

    df = load_maintenance()

    engine = df[
        (df["dataset"] == dataset) &
        (df["engine_id"] == engine_id)
    ]

    if engine.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Engine {engine_id} "
                f"not found in {dataset}"
            )
        )

    row = engine.iloc[0]

    return {
        "dataset": dataset,
        "engine_id": int(engine_id),
        "predicted_rul": round(
            float(row["predicted_RUL"]),
            2
        ),
        "actual_rul": round(
            float(row["actual_RUL"]),
            2
        ),
        "health_score": round(
            float(row["health_score"]),
            2
        ),
        "anomaly_score": round(
            float(row["anomaly_score"]),
            2
        ),
        "anomaly_status": row["anomaly_status"],
        "risk": row["risk_level"],
        "priority_score": round(
            float(row["priority_score"]),
            2
        ),
        "maintenance_priority": (
            row["maintenance_priority"]
        ),
        "maintenance_recommendation": (
            row["maintenance_recommendation"]
        ),
        "top_abnormal_sensors": (
            str(row["top_abnormal_sensors"])
        )
    }


# ============================================================
# RUL PREDICTION
# ============================================================

@app.get("/api/prediction/{dataset}/{engine_id}")
def get_prediction(
    dataset: str,
    engine_id: int
):

    dataset = validate_dataset(dataset)

    df = load_predictions()

    engine = df[
        (df["dataset"] == dataset) &
        (df["engine_id"] == engine_id)
    ]

    if engine.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Prediction for Engine "
                f"{engine_id} in {dataset} not found"
            )
        )

    row = engine.iloc[0]

    return {
        "dataset": dataset,
        "engine_id": int(engine_id),
        "actual_rul": round(
            float(row["actual_RUL"]),
            2
        ),
        "predicted_rul": round(
            max(float(row["predicted_RUL"]), 0),
            2
        ),
        "error": round(
            float(row["error"]),
            2
        )
    }


# ============================================================
# ANOMALY DETECTION
# ============================================================

@app.get("/api/anomaly/{dataset}/{engine_id}")
def get_anomaly(
    dataset: str,
    engine_id: int
):

    dataset = validate_dataset(dataset)

    df = load_anomalies()

    engine = df[
        (df["dataset"] == dataset) &
        (df["unit_id"] == engine_id)
    ]

    if engine.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Anomaly data for Engine "
                f"{engine_id} in {dataset} not found"
            )
        )

    row = (
        engine
        .sort_values("cycle")
        .iloc[-1]
    )

    sensors = str(
        row["top_abnormal_sensors"]
    )

    if sensors in [
        "none",
        "insufficient_history",
        "nan"
    ]:

        abnormal_sensors = []

    else:

        abnormal_sensors = [
            sensor.strip()
            for sensor in sensors.split(",")
        ]

    return {
        "dataset": dataset,
        "engine_id": int(engine_id),
        "cycle": int(row["cycle"]),
        "anomaly_score": round(
            float(row["anomaly_score"]),
            2
        ),
        "status": row["status"],
        "top_abnormal_sensors": abnormal_sensors
    }


# ============================================================
# MAINTENANCE PRIORITY
# ============================================================

@app.get("/api/maintenance/{dataset}/{engine_id}")
def get_maintenance(
    dataset: str,
    engine_id: int
):

    dataset = validate_dataset(dataset)

    df = load_maintenance()

    engine = df[
        (df["dataset"] == dataset) &
        (df["engine_id"] == engine_id)
    ]

    if engine.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Maintenance data for Engine "
                f"{engine_id} in {dataset} not found"
            )
        )

    row = engine.iloc[0]

    return {
        "dataset": dataset,
        "engine_id": int(engine_id),
        "predicted_rul": round(
            max(float(row["predicted_RUL"]), 0),
            2
        ),
        "health_score": round(
            float(row["health_score"]),
            2
        ),
        "anomaly_score": round(
            float(row["anomaly_score"]),
            2
        ),
        "risk": row["risk_level"],
        "priority_score": round(
            float(row["priority_score"]),
            2
        ),
        "maintenance_priority": (
            row["maintenance_priority"]
        ),
        "recommendation": (
            row["maintenance_recommendation"]
        ),
        "top_abnormal_sensors": (
            str(row["top_abnormal_sensors"])
        )
    }


# ============================================================
# FLEET SUMMARY
# ============================================================

@app.get("/api/fleet/summary")
def fleet_summary():

    df = load_maintenance()

    return {
        "total_engines": int(len(df)),
        "average_predicted_rul": round(
            float(df["predicted_RUL"].mean()),
            2
        ),
        "average_health_score": round(
            float(df["health_score"].mean()),
            2
        ),
        "average_anomaly_score": round(
            float(df["anomaly_score"].mean()),
            2
        ),
        "risk_distribution": {
            "LOW": int(
                (df["risk_level"] == "LOW").sum()
            ),
            "MEDIUM": int(
                (df["risk_level"] == "MEDIUM").sum()
            ),
            "HIGH": int(
                (df["risk_level"] == "HIGH").sum()
            ),
            "CRITICAL": int(
                (df["risk_level"] == "CRITICAL").sum()
            )
        },
        "maintenance_distribution": {
            "CONTINUE MONITORING": int(
                (
                    df["maintenance_priority"]
                    == "CONTINUE MONITORING"
                ).sum()
            ),
            "MONITOR CLOSELY": int(
                (
                    df["maintenance_priority"]
                    == "MONITOR CLOSELY"
                ).sum()
            ),
            "SCHEDULE MAINTENANCE": int(
                (
                    df["maintenance_priority"]
                    == "SCHEDULE MAINTENANCE"
                ).sum()
            ),
            "IMMEDIATE INSPECTION": int(
                (
                    df["maintenance_priority"]
                    == "IMMEDIATE INSPECTION"
                ).sum()
            )
        }
    }


# ============================================================
# TOP PRIORITY ENGINES
# ============================================================

@app.get("/api/fleet/top-priority")
def fleet_top_priority():

    df = load_maintenance()

    df = (
        df
        .sort_values(
            "priority_score",
            ascending=False
        )
        .head(20)
    )

    engines = []

    for _, row in df.iterrows():

        engines.append({
            "dataset": row["dataset"],
            "engine_id": int(row["engine_id"]),
            "predicted_rul": round(
                max(float(row["predicted_RUL"]), 0),
                2
            ),
            "health_score": round(
                float(row["health_score"]),
                2
            ),
            "anomaly_score": round(
                float(row["anomaly_score"]),
                2
            ),
            "risk": row["risk_level"],
            "priority_score": round(
                float(row["priority_score"]),
                2
            ),
            "maintenance_priority": (
                row["maintenance_priority"]
            ),
            "top_abnormal_sensors": (
                str(row["top_abnormal_sensors"])
            )
        })

    return {
        "count": len(engines),
        "engines": engines
    }
# ============================================================
# SHAP EXPLAINABILITY
# ============================================================

EXPLANATION_FILE = os.path.join(
    OUTPUT_DIR,
    "explanations_all.csv"
)


def load_explanations():

    return load_csv(
        EXPLANATION_FILE,
        "explanations_all.csv"
    )


@app.get("/api/explanation/{dataset}/{engine_id}")
def get_explanation(
    dataset: str,
    engine_id: int
):

    dataset = validate_dataset(dataset)

    df = load_explanations()

    engine = df[
        (df["dataset"] == dataset) &
        (df["engine_id"] == engine_id)
    ]

    if engine.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"SHAP explanation for Engine "
                f"{engine_id} in {dataset} not found"
            )
        )

    # Sort by absolute SHAP impact
    engine = engine.copy()

    engine["absolute_impact"] = (
        engine["shap_value"].abs()
    )

    engine = engine.sort_values(
        "absolute_impact",
        ascending=False
    )

    contributors = []

    for _, row in engine.iterrows():

        impact = float(row["shap_value"])

        contributors.append({
            "feature": row["feature"],
            "impact": round(impact, 4),
            "effect": row["effect"]
        })

    return {
        "dataset": dataset,
        "engine_id": int(engine_id),
        "contributors": contributors
    }
# ==========================================
# TELEMETRY EXPLORER
# ==========================================

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

TELEMETRY_COLUMNS = (
    ["unit_id", "cycle", "setting_1", "setting_2", "setting_3"]
    + [f"sensor_{i}" for i in range(1, 22)]
)


def load_test_telemetry(dataset):

    if dataset not in ["FD001", "FD002", "FD003", "FD004"]:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset {dataset} not found"
        )

    test_file = os.path.join(
        DATA_DIR,
        dataset,
        f"test_{dataset}.txt"
    )

    if not os.path.exists(test_file):
        raise HTTPException(
            status_code=404,
            detail=f"Telemetry file for {dataset} not found"
        )

    return pd.read_csv(
        test_file,
        sep=r"\s+",
        header=None,
        names=TELEMETRY_COLUMNS
    )


@app.get("/api/telemetry/{dataset}/{engine_id}")
def get_telemetry(
    dataset: str,
    engine_id: int
):

    df = load_test_telemetry(dataset)

    engine = df[
        df["unit_id"] == engine_id
    ].sort_values("cycle")

    if engine.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Engine {engine_id} "
                f"not found in {dataset}"
            )
        )

    # Return telemetry records
    # without the internal unit_id column.
    telemetry = []

    for _, row in engine.iterrows():

        record = {
            "cycle": int(row["cycle"]),
            "setting_1": round(float(row["setting_1"]), 4),
            "setting_2": round(float(row["setting_2"]), 4),
            "setting_3": round(float(row["setting_3"]), 4)
        }

        for i in range(1, 22):

            sensor = f"sensor_{i}"

            record[sensor] = round(
                float(row[sensor]),
                4
            )

        telemetry.append(record)

    return {
        "dataset": dataset,
        "engine_id": engine_id,
        "total_cycles": len(telemetry),
        "latest_cycle": telemetry[-1]["cycle"],
        "telemetry": telemetry
    }
# ==========================================
# DEGRADATION TIMELINE
# ==========================================

DEGRADATION_FILE = os.path.join(
    OUTPUT_DIR,
    "degradation_timeline_all.csv"
)


def load_degradation_data():

    if not os.path.exists(DEGRADATION_FILE):
        raise FileNotFoundError(
            "degradation_timeline_all.csv not found"
        )

    return pd.read_csv(DEGRADATION_FILE)


@app.get("/api/degradation/{dataset}/{engine_id}")
def get_degradation(
    dataset: str,
    engine_id: int
):

    df = load_degradation_data()

    engine = df[
        (df["dataset"] == dataset) &
        (df["engine_id"] == engine_id)
    ].copy()

    if engine.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Degradation timeline for "
                f"{dataset} engine {engine_id} not found"
            )
        )

    timeline = []

    for _, row in engine.iterrows():

        timeline.append({
            "cycle": int(row["cycle"]),
            "estimated_rul": round(
                float(row["estimated_rul"]),
                2
            ),
            "health_score": round(
                float(row["health_score"]),
                2
            ),
            "anomaly_score": round(
                float(row["anomaly_score"]),
                2
            ),
            "status": row["status"],
            "degradation_status": row["degradation_status"]
        })

    return {
        "dataset": dataset,
        "engine_id": engine_id,
        "total_cycles": len(timeline),
        "timeline": timeline
    }
# ==========================================
# REAL-TIME TELEMETRY SIMULATION
# ==========================================

from ml.telemetry_simulator import (
    get_latest_telemetry,
    simulate_next_cycle
)


@app.get("/api/live-telemetry/{dataset}/{engine_id}")
def get_live_telemetry(
    dataset: str,
    engine_id: int
):

    try:
        current = get_latest_telemetry(
            dataset,
            engine_id
        )

        simulated = simulate_next_cycle(
            dataset,
            engine_id
        )

        return {
            "dataset": dataset,
            "engine_id": engine_id,
            "current": current,
            "simulated_next_cycle": simulated
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    # ==========================================
# FAULT INVESTIGATION
# ==========================================

from ml.fault_investigation import investigate


@app.get("/api/fault-investigation/{dataset}/{engine_id}")
def get_fault_investigation(
    dataset: str,
    engine_id: int
):

    try:

        return investigate(
            dataset,
            engine_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    # ==========================================
# ENGINE COMPARISON
# ==========================================

from ml.engine_comparison import compare_engines


@app.get("/api/compare/{dataset}/{engine1_id}/{engine2_id}")
def get_engine_comparison(
    dataset: str,
    engine1_id: int,
    engine2_id: int
):

    try:

        return compare_engines(
            dataset,
            engine1_id,
            engine2_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    