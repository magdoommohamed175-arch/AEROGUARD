import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ============================================================
# AEROGUARD - ANOMALY DETECTION V2
# ============================================================

DATASETS = ["FD001", "FD002", "FD003", "FD004"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "ml", "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

SENSORS = [f"sensor_{i}" for i in range(1, 22)]
SETTINGS = ["setting_1", "setting_2", "setting_3"]


# ============================================================
# LOAD DATA
# ============================================================

def load_dataset(dataset):

    path = os.path.join(
        DATA_DIR,
        dataset,
        f"train_{dataset}.txt"
    )

    columns = (
        ["unit_id", "cycle"]
        + SETTINGS
        + SENSORS
    )

    return pd.read_csv(
        path,
        sep=r"\s+",
        header=None,
        names=columns
    )


# ============================================================
# CREATE ENGINE-RELATIVE FEATURES
# ============================================================

def create_features(df):

    result = df.copy()

    feature_columns = []

    for sensor in SENSORS:

        # ----------------------------------------------------
        # Rolling baseline
        # ----------------------------------------------------

        rolling_mean = (
            result.groupby("unit_id")[sensor]
            .transform(
                lambda x:
                x.rolling(
                    window=10,
                    min_periods=3
                ).mean()
            )
        )

        rolling_std = (
            result.groupby("unit_id")[sensor]
            .transform(
                lambda x:
                x.rolling(
                    window=10,
                    min_periods=3
                ).std()
            )
            .fillna(0)
        )

        result[f"{sensor}_mean"] = rolling_mean
        result[f"{sensor}_std"] = rolling_std

        # ----------------------------------------------------
        # Deviation from rolling baseline
        # ----------------------------------------------------

        deviation = (
            result[sensor] - rolling_mean
        )

        result[f"{sensor}_deviation"] = deviation

        # ----------------------------------------------------
        # Normalized deviation
        # ----------------------------------------------------

        safe_std = rolling_std.replace(
            0,
            np.nan
        )

        z_score = (
            deviation / safe_std
        )

        z_score = (
            z_score
            .replace(
                [np.inf, -np.inf],
                np.nan
            )
            .fillna(0)
        )

        result[f"{sensor}_zscore"] = z_score

        feature_columns.extend([
            f"{sensor}_deviation",
            f"{sensor}_zscore"
        ])

    # --------------------------------------------------------
    # Operating-condition features
    # --------------------------------------------------------

    for setting in SETTINGS:

        # Deviation from engine's running average
        setting_mean = (
            result.groupby("unit_id")[setting]
            .transform(
                lambda x:
                x.expanding(
                    min_periods=1
                ).mean()
            )
        )

        result[f"{setting}_deviation"] = (
            result[setting] - setting_mean
        )

        feature_columns.append(
            f"{setting}_deviation"
        )

    # --------------------------------------------------------
    # Remove first few cycles from model training
    # --------------------------------------------------------
    # Early cycles do not contain enough history to calculate
    # reliable engine-relative degradation features.

    result["_history_ready"] = (
        result["cycle"] >= 10
    )

    # --------------------------------------------------------
    # Prepare model matrix
    # --------------------------------------------------------

    X = result[
        feature_columns
    ].copy()

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    X = X.fillna(0)

    # Remove constant features
    valid_columns = X.columns[
        X.var() > 0
    ]

    X = X[valid_columns]

    return result, X, valid_columns


# ============================================================
# SENSOR ATTRIBUTION
# ============================================================

def find_abnormal_sensors(row):

    scores = {}

    for sensor in SENSORS:

        z_column = f"{sensor}_zscore"

        if z_column in row.index:

            value = abs(
                float(row[z_column])
            )

            scores[sensor] = value

    ordered = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        sensor
        for sensor, score in ordered[:3]
    ]


# ============================================================
# PROCESS ONE DATASET
# ============================================================

def process_dataset(dataset):

    print("\n" + "=" * 60)
    print(f"PROCESSING {dataset}")
    print("=" * 60)

    df = load_dataset(dataset)

    print(
        f"Raw shape: {df.shape}"
    )

    print(
        f"Engines: {df['unit_id'].nunique()}"
    )

    print(
        "Creating engine-relative features..."
    )

    feature_df, X, feature_columns = (
        create_features(df)
    )

    print(
        f"Features used: {len(feature_columns)}"
    )

    # --------------------------------------------------------
    # Only use records with enough history for training
    # --------------------------------------------------------

    training_mask = (
        feature_df["_history_ready"]
    )

    X_train = X.loc[
        training_mask
    ]

    print(
        f"Training rows after history filter: "
        f"{len(X_train)}"
    )

    # --------------------------------------------------------
    # Scale
    # --------------------------------------------------------

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(
        X_train
    )

    # --------------------------------------------------------
    # Isolation Forest
    # --------------------------------------------------------

    print(
        "Training Isolation Forest V2..."
    )

    model = IsolationForest(
        n_estimators=300,
        contamination=0.03,
        max_samples="auto",
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train_scaled
    )

    # --------------------------------------------------------
    # Score ALL records
    # --------------------------------------------------------

    X_all_scaled = scaler.transform(
        X
    )

    decision = model.decision_function(
        X_all_scaled
    )

    raw_score = -decision

    # --------------------------------------------------------
    # Convert score into percentile
    # --------------------------------------------------------
    # Percentile is more stable than simply min-max scaling.

    reference_scores = raw_score[
        training_mask.values
    ]

    percentile = (
        pd.Series(
            raw_score
        )
        .rank(
            pct=True
        )
        .values
        * 100
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # First 9 cycles are treated as insufficient history.
    # They are not classified as critical merely because
    # their baseline is immature.
    # --------------------------------------------------------

    status = np.full(
        len(feature_df),
        "NORMAL",
        dtype=object
    )

    mature_mask = (
        feature_df["_history_ready"].values
    )

    mature_percentile = percentile[
        mature_mask
    ]

    status[
        mature_mask &
        (percentile >= 97)
    ] = "CRITICAL"

    status[
        mature_mask &
        (percentile >= 85) &
        (percentile < 97)
    ] = "WARNING"

    # --------------------------------------------------------
    # Sensor attribution
    # --------------------------------------------------------

    top_sensors = []

    for index in range(
        len(feature_df)
    ):

        row = feature_df.iloc[index]

        # Don't claim sensor-level anomaly
        # when there isn't enough history.
        if not row["_history_ready"]:

            top_sensors.append(
                "insufficient_history"
            )

        else:

            sensors = find_abnormal_sensors(
                row
            )

            top_sensors.append(
                ", ".join(sensors)
            )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    output = feature_df[
        [
            "unit_id",
            "cycle"
        ]
    ].copy()

    output["dataset"] = dataset

    output["anomaly_score"] = np.round(
        percentile,
        4
    )

    output["status"] = status

    output[
        "top_abnormal_sensors"
    ] = top_sensors

    print(
        "\n===== V2 ANOMALY DISTRIBUTION ====="
    )

    print(
        output["status"].value_counts()
    )

    print(
        "\n===== TOP V2 ANOMALIES ====="
    )

    print(
        output[
            output["status"] != "NORMAL"
        ]
        .sort_values(
            "anomaly_score",
            ascending=False
        )
        .head(10)
        .to_string(
            index=False
        )
    )

    return output


# ============================================================
# RUN ALL DATASETS
# ============================================================

all_results = []

print("\n" + "=" * 60)
print("AEROGUARD ANOMALY DETECTION V2")
print("=" * 60)

for dataset in DATASETS:

    result = process_dataset(
        dataset
    )

    all_results.append(
        result
    )


# ============================================================
# COMBINE
# ============================================================

final_df = pd.concat(
    all_results,
    ignore_index=True
)

output_path = os.path.join(
    OUTPUT_DIR,
    "anomaly_detection_v2_all.csv"
)

final_df.to_csv(
    output_path,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("FINAL V2 ANOMALY SUMMARY")
print("=" * 60)

print(
    f"Total records: {len(final_df)}"
)

print("\nOverall distribution:")

print(
    final_df[
        "status"
    ].value_counts()
)

print(
    "\nDataset distribution:"
)

print(
    pd.crosstab(
        final_df["dataset"],
        final_df["status"]
    )
)

print(
    "\nCycle 1-9 status check:"
)

early = final_df[
    final_df["cycle"] < 10
]

print(
    early["status"].value_counts()
)

print("\nSaved:")

print(output_path)