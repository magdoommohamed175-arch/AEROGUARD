import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ============================================================
# AEROGUARD - FINAL ANOMALY DETECTION
# ============================================================

DATASETS = ["FD001", "FD002", "FD003", "FD004"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "ml", "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

SENSORS = [f"sensor_{i}" for i in range(1, 22)]

SETTINGS = [
    "setting_1",
    "setting_2",
    "setting_3"
]


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
# FIND USEFUL SENSORS
# ============================================================

def find_useful_sensors(df):

    variances = df[SENSORS].var()

    useful = []

    for sensor in SENSORS:

        if variances[sensor] > 1e-6:
            useful.append(sensor)

    return useful


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(df, useful_sensors):

    result = df.copy()

    feature_columns = []

    for sensor in useful_sensors:

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

        deviation = (
            result[sensor]
            - rolling_mean
        )

        result[
            f"{sensor}_deviation"
        ] = deviation

        safe_std = rolling_std.clip(
            lower=1e-6
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
            .clip(-10, 10)
        )

        result[
            f"{sensor}_zscore"
        ] = z_score

        result[
            f"{sensor}_rolling_std"
        ] = rolling_std

        feature_columns.extend([
            f"{sensor}_deviation",
            f"{sensor}_zscore",
            f"{sensor}_rolling_std"
        ])

    # --------------------------------------------------------
    # Operating-condition deviations
    # --------------------------------------------------------

    for setting in SETTINGS:

        baseline = (
            result.groupby("unit_id")[setting]
            .transform(
                lambda x:
                x.expanding(
                    min_periods=1
                ).mean()
            )
        )

        result[
            f"{setting}_deviation"
        ] = (
            result[setting] - baseline
        )

        feature_columns.append(
            f"{setting}_deviation"
        )

    # --------------------------------------------------------
    # History flag
    # --------------------------------------------------------

    result["_history_ready"] = (
        result["cycle"] >= 10
    )

    X = result[
        feature_columns
    ].copy()

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    ).fillna(0)

    valid_columns = X.columns[
        X.var() > 1e-12
    ]

    X = X[valid_columns]

    return result, X


# ============================================================
# SENSOR EXPLANATION
# ============================================================

def get_top_sensors(row, useful_sensors):

    scores = {}

    for sensor in useful_sensors:

        column = f"{sensor}_zscore"

        if column not in row.index:
            continue

        score = abs(
            float(row[column])
        )

        # Ignore small deviations.
        if score >= 0.5:
            scores[sensor] = score

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:3]


# ============================================================
# PROCESS DATASET
# ============================================================

def process_dataset(dataset):

    print("\n" + "=" * 60)
    print(f"FINAL ANOMALY ANALYSIS: {dataset}")
    print("=" * 60)

    df = load_dataset(dataset)

    print(
        f"Raw shape: {df.shape}"
    )

    useful_sensors = find_useful_sensors(df)

    print(
        f"Useful sensors: {len(useful_sensors)}"
    )

    print(
        useful_sensors
    )

    feature_df, X = create_features(
        df,
        useful_sensors
    )

    training_mask = (
        feature_df["_history_ready"]
    )

    X_train = X.loc[
        training_mask
    ]

    print(
        f"Training rows: {len(X_train)}"
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
    # Score
    # --------------------------------------------------------

    X_all_scaled = scaler.transform(X)

    decision = model.decision_function(
        X_all_scaled
    )

    raw_score = -decision

    # Percentile-based score
    anomaly_score = (
        pd.Series(raw_score)
        .rank(pct=True)
        .values
        * 100
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    status = np.full(
        len(feature_df),
        "NORMAL",
        dtype=object
    )

    mature = (
        feature_df[
            "_history_ready"
        ].values
    )

    status[
        mature &
        (anomaly_score >= 97)
    ] = "CRITICAL"

    status[
        mature &
        (anomaly_score >= 85) &
        (anomaly_score < 97)
    ] = "WARNING"

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    top_sensors = []
    sensor_scores = []

    for i in range(len(feature_df)):

        row = feature_df.iloc[i]

        if not row["_history_ready"]:

            top_sensors.append(
                "insufficient_history"
            )

            sensor_scores.append("")

            continue

        ranked = get_top_sensors(
            row,
            useful_sensors
        )

        if not ranked:

            top_sensors.append(
                "none"
            )

            sensor_scores.append("")

        else:

            top_sensors.append(
                ", ".join(
                    sensor
                    for sensor, _ in ranked
                )
            )

            sensor_scores.append(
                ", ".join(
                    f"{score:.2f}"
                    for _, score in ranked
                )
            )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    output = feature_df[
        [
            "unit_id",
            "cycle"
        ]
    ].copy()

    output["dataset"] = dataset

    output["anomaly_score"] = np.round(
        anomaly_score,
        4
    )

    output["status"] = status

    output[
        "top_abnormal_sensors"
    ] = top_sensors

    output[
        "sensor_deviation_scores"
    ] = sensor_scores

    print("\n===== STATUS =====")

    print(
        output["status"].value_counts()
    )

    print("\n===== TOP ANOMALIES =====")

    print(
        output[
            output["status"] != "NORMAL"
        ]
        .sort_values(
            "anomaly_score",
            ascending=False
        )
        .head(5)
        .to_string(index=False)
    )

    return output


# ============================================================
# RUN ALL DATASETS
# ============================================================

print("\n" + "=" * 60)
print("AEROGUARD FINAL ANOMALY DETECTION")
print("=" * 60)

results = []

for dataset in DATASETS:

    result = process_dataset(dataset)

    results.append(result)


# ============================================================
# COMBINE
# ============================================================

final_df = pd.concat(
    results,
    ignore_index=True
)

output_path = os.path.join(
    OUTPUT_DIR,
    "anomaly_detection_final.csv"
)

final_df.to_csv(
    output_path,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("FINAL ANOMALY DETECTION SUMMARY")
print("=" * 60)

print(
    f"Total records: {len(final_df)}"
)

print(
    f"Datasets: {final_df['dataset'].nunique()}"
)

print(
    "\nOverall status:"
)

print(
    final_df["status"].value_counts()
)

print(
    "\nDataset-wise status:"
)

print(
    pd.crosstab(
        final_df["dataset"],
        final_df["status"]
    )
)

print(
    "\nEarly-cycle validation:"
)

early = final_df[
    final_df["cycle"] < 10
]

print(
    early["status"].value_counts()
)

print(
    "\nSaved:"
)

print(output_path)