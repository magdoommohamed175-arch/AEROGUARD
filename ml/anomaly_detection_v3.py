import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ============================================================
# AEROGUARD - ANOMALY DETECTION V3
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
# LOAD DATASET
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

    df = pd.read_csv(
        path,
        sep=r"\s+",
        header=None,
        names=columns
    )

    return df


# ============================================================
# FIND USEFUL SENSORS
# ============================================================

def find_useful_sensors(df):

    variances = df[SENSORS].var()

    # Ignore sensors with effectively zero variation.
    #
    # The threshold is deliberately relative to each
    # dataset because sensor scales are very different.

    useful = []

    for sensor in SENSORS:

        variance = variances[sensor]

        if variance > 1e-6:
            useful.append(sensor)

    return useful, variances


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(df, useful_sensors):

    result = df.copy()

    feature_columns = []

    for sensor in useful_sensors:

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

        # ----------------------------------------------------
        # Deviation from engine baseline
        # ----------------------------------------------------

        deviation = (
            result[sensor]
            - rolling_mean
        )

        result[
            f"{sensor}_deviation"
        ] = deviation

        # ----------------------------------------------------
        # Safe normalized deviation
        # ----------------------------------------------------

        safe_std = rolling_std.clip(
            lower=1e-6
        )

        z_score = (
            deviation
            / safe_std
        )

        z_score = (
            z_score
            .replace(
                [np.inf, -np.inf],
                np.nan
            )
            .fillna(0)
        )

        # Limit extreme numerical values.
        z_score = z_score.clip(
            -10,
            10
        )

        result[
            f"{sensor}_zscore"
        ] = z_score

        # ----------------------------------------------------
        # Rolling variability
        # ----------------------------------------------------

        result[
            f"{sensor}_rolling_std"
        ] = rolling_std

        feature_columns.extend([
            f"{sensor}_deviation",
            f"{sensor}_zscore",
            f"{sensor}_rolling_std"
        ])

    # ========================================================
    # OPERATING SETTINGS
    # ========================================================

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

        deviation = (
            result[setting]
            - baseline
        )

        result[
            f"{setting}_deviation"
        ] = deviation

        feature_columns.append(
            f"{setting}_deviation"
        )

    # ========================================================
    # ENGINE HISTORY FLAG
    # ========================================================

    result["_history_ready"] = (
        result["cycle"] >= 10
    )

    # ========================================================
    # MODEL MATRIX
    # ========================================================

    X = result[
        feature_columns
    ].copy()

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    X = X.fillna(0)

    # Remove zero-variance engineered features.

    valid_columns = X.columns[
        X.var() > 1e-12
    ]

    X = X[
        valid_columns
    ]

    return result, X, valid_columns


# ============================================================
# SENSOR ATTRIBUTION
# ============================================================

def calculate_sensor_scores(
    row,
    useful_sensors
):

    scores = {}

    for sensor in useful_sensors:

        column = f"{sensor}_zscore"

        if column not in row.index:
            continue

        value = abs(
            float(row[column])
        )

        # Ignore small deviations.
        if value < 0.5:
            continue

        scores[sensor] = value

    ordered = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return ordered[:3]


# ============================================================
# PROCESS DATASET
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

    # --------------------------------------------------------
    # Useful sensors
    # --------------------------------------------------------

    useful_sensors, variances = (
        find_useful_sensors(df)
    )

    ignored_sensors = [
        sensor
        for sensor in SENSORS
        if sensor not in useful_sensors
    ]

    print("\n===== SENSOR FILTER =====")

    print(
        f"Useful sensors: "
        f"{len(useful_sensors)}"
    )

    print(
        useful_sensors
    )

    print(
        f"Ignored near-constant sensors: "
        f"{len(ignored_sensors)}"
    )

    print(
        ignored_sensors
    )

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    print(
        "\nCreating robust anomaly features..."
    )

    feature_df, X, feature_columns = (
        create_features(
            df,
            useful_sensors
        )
    )

    print(
        f"Features used: "
        f"{len(feature_columns)}"
    )

    # --------------------------------------------------------
    # Training history
    # --------------------------------------------------------

    training_mask = (
        feature_df[
            "_history_ready"
        ]
    )

    X_train = X.loc[
        training_mask
    ]

    print(
        f"Training rows: "
        f"{len(X_train)}"
    )

    # --------------------------------------------------------
    # Scaling
    # --------------------------------------------------------

    scaler = StandardScaler()

    X_train_scaled = (
        scaler.fit_transform(
            X_train
        )
    )

    # --------------------------------------------------------
    # Isolation Forest
    # --------------------------------------------------------

    print(
        "Training Isolation Forest V3..."
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
    # Score all observations
    # --------------------------------------------------------

    X_all_scaled = (
        scaler.transform(X)
    )

    decision_scores = (
        model.decision_function(
            X_all_scaled
        )
    )

    raw_anomaly_score = (
        -decision_scores
    )

    # --------------------------------------------------------
    # Convert score to percentile
    # --------------------------------------------------------

    percentile = (
        pd.Series(
            raw_anomaly_score
        )
        .rank(
            pct=True
        )
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
        (percentile >= 97)
    ] = "CRITICAL"

    status[
        mature &
        (percentile >= 85) &
        (percentile < 97)
    ] = "WARNING"

    # --------------------------------------------------------
    # Sensor attribution
    # --------------------------------------------------------

    abnormal_sensors = []
    abnormal_sensor_scores = []

    for index in range(
        len(feature_df)
    ):

        row = feature_df.iloc[
            index
        ]

        if not row["_history_ready"]:

            abnormal_sensors.append(
                "insufficient_history"
            )

            abnormal_sensor_scores.append(
                ""
            )

            continue

        top = calculate_sensor_scores(
            row,
            useful_sensors
        )

        if len(top) == 0:

            abnormal_sensors.append(
                "none"
            )

            abnormal_sensor_scores.append(
                ""
            )

        else:

            abnormal_sensors.append(
                ", ".join(
                    [
                        item[0]
                        for item in top
                    ]
                )
            )

            abnormal_sensor_scores.append(
                ", ".join(
                    [
                        f"{item[1]:.2f}"
                        for item in top
                    ]
                )
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

    output[
        "anomaly_score"
    ] = np.round(
        percentile,
        4
    )

    output["status"] = status

    output[
        "top_abnormal_sensors"
    ] = abnormal_sensors

    output[
        "sensor_deviation_scores"
    ] = abnormal_sensor_scores

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print(
        "\n===== V3 ANOMALY DISTRIBUTION ====="
    )

    print(
        output[
            "status"
        ].value_counts()
    )

    print(
        "\n===== TOP V3 ANOMALIES ====="
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
# MAIN
# ============================================================

print("\n" + "=" * 60)
print("AEROGUARD ANOMALY DETECTION V3")
print("=" * 60)

all_results = []

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
    "anomaly_detection_v3_all.csv"
)

final_df.to_csv(
    output_path,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("FINAL V3 ANOMALY SUMMARY")
print("=" * 60)

print(
    f"Total records: "
    f"{len(final_df)}"
)

print(
    "\nOverall distribution:"
)

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
    "\nEarly-cycle check:"
)

early = final_df[
    final_df["cycle"] < 10
]

print(
    early[
        "status"
    ].value_counts()
)

print(
    "\nTop abnormal sensors:"
)

sensor_counts = (
    final_df[
        final_df["top_abnormal_sensors"]
        .notna()
    ]["top_abnormal_sensors"]
    .value_counts()
    .head(10)
)

print(sensor_counts)

print("\nSaved:")
print(output_path)