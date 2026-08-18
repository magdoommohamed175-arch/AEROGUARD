import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ============================================================
# CONFIGURATION
# ============================================================

DATASETS = ["FD001", "FD002", "FD003", "FD004"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "ml", "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

SENSOR_COLUMNS = [f"sensor_{i}" for i in range(1, 22)]

# Sensors with absolutely no variation across a dataset
# will not provide useful information for anomaly detection.


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
        ["unit_id", "cycle", "setting_1", "setting_2", "setting_3"]
        + SENSOR_COLUMNS
    )

    df = pd.read_csv(
        path,
        sep=r"\s+",
        header=None,
        names=columns
    )

    return df


# ============================================================
# CREATE ANOMALY FEATURES
# ============================================================

def prepare_features(df):

    sensor_features = []

    for sensor in SENSOR_COLUMNS:

        # Current sensor value
        sensor_features.append(sensor)

        # Rolling mean
        rolling_mean = (
            df.groupby("unit_id")[sensor]
            .transform(
                lambda x: x.rolling(
                    window=5,
                    min_periods=1
                ).mean()
            )
        )

        df[f"{sensor}_rolling_mean"] = rolling_mean

        # Rolling standard deviation
        rolling_std = (
            df.groupby("unit_id")[sensor]
            .transform(
                lambda x: x.rolling(
                    window=5,
                    min_periods=1
                ).std()
            )
            .fillna(0)
        )

        df[f"{sensor}_rolling_std"] = rolling_std

        sensor_features.append(f"{sensor}_rolling_mean")
        sensor_features.append(f"{sensor}_rolling_std")

    feature_columns = []

    for sensor in SENSOR_COLUMNS:

        feature_columns.extend([
            sensor,
            f"{sensor}_rolling_mean",
            f"{sensor}_rolling_std"
        ])

    X = df[feature_columns].copy()

    # Replace possible infinite values
    X = X.replace([np.inf, -np.inf], np.nan)

    # Fill missing values
    X = X.fillna(0)

    # Remove columns with zero variance
    valid_columns = X.columns[X.var() > 0]

    X = X[valid_columns]

    return X, valid_columns


# ============================================================
# FIND MOST ABNORMAL SENSORS
# ============================================================

def calculate_sensor_deviation(df):

    deviations = []

    for sensor in SENSOR_COLUMNS:

        # Calculate rolling mean
        rolling_mean = (
            df.groupby("unit_id")[sensor]
            .transform(
                lambda x: x.rolling(
                    window=10,
                    min_periods=1
                ).mean()
            )
        )

        rolling_std = (
            df.groupby("unit_id")[sensor]
            .transform(
                lambda x: x.rolling(
                    window=10,
                    min_periods=1
                ).std()
            )
            .fillna(0)
        )

        # Prevent division by zero
        rolling_std = rolling_std.replace(0, np.nan)

        z_score = (
            (df[sensor] - rolling_mean)
            / rolling_std
        ).abs()

        z_score = z_score.replace(
            [np.inf, -np.inf],
            np.nan
        ).fillna(0)

        deviations.append(z_score.rename(sensor))

    deviation_df = pd.concat(
        deviations,
        axis=1
    )

    return deviation_df


# ============================================================
# MAIN PROCESSING
# ============================================================

all_results = []

print("\n" + "=" * 60)
print("AEROGUARD ANOMALY DETECTION")
print("=" * 60)

for dataset in DATASETS:

    print("\n" + "=" * 60)
    print(f"PROCESSING {dataset}")
    print("=" * 60)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_dataset(dataset)

    print(f"Raw shape: {df.shape}")
    print(f"Engines: {df['unit_id'].nunique()}")

    # --------------------------------------------------------
    # Feature engineering
    # --------------------------------------------------------

    print("Creating anomaly features...")

    X, feature_columns = prepare_features(df)

    print(
        f"Features used: {len(feature_columns)}"
    )

    # --------------------------------------------------------
    # Scaling
    # --------------------------------------------------------

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    # --------------------------------------------------------
    # Isolation Forest
    # --------------------------------------------------------

    print("Training Isolation Forest...")

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_scaled)

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    raw_prediction = model.predict(X_scaled)

    decision_score = model.decision_function(X_scaled)

    # Convert so higher = more anomalous
    anomaly_score = -decision_score

    # Normalize approximately to 0-100
    score_min = anomaly_score.min()
    score_max = anomaly_score.max()

    if score_max > score_min:
        anomaly_score_normalized = (
            (anomaly_score - score_min)
            / (score_max - score_min)
            * 100
        )
    else:
        anomaly_score_normalized = np.zeros(
            len(anomaly_score)
        )

    # --------------------------------------------------------
    # Risk classification
    # --------------------------------------------------------

    status = np.where(
        anomaly_score_normalized >= 80,
        "CRITICAL",
        np.where(
            anomaly_score_normalized >= 50,
            "WARNING",
            "NORMAL"
        )
    )

    # --------------------------------------------------------
    # Sensor deviations
    # --------------------------------------------------------

    deviation_df = calculate_sensor_deviation(df)

    top_sensor_list = []

    for index in range(len(df)):

        row = deviation_df.iloc[index]

        top_sensors = (
            row
            .sort_values(
                ascending=False
            )
            .head(3)
            .index
            .tolist()
        )

        top_sensor_list.append(
            ", ".join(top_sensors)
        )

    # --------------------------------------------------------
    # Result dataframe
    # --------------------------------------------------------

    result = df[
        [
            "unit_id",
            "cycle"
        ]
    ].copy()

    result["dataset"] = dataset

    result["anomaly_score"] = np.round(
        anomaly_score_normalized,
        4
    )

    result["status"] = status

    result["top_abnormal_sensors"] = (
        top_sensor_list
    )

    all_results.append(result)

    # --------------------------------------------------------
    # Dataset statistics
    # --------------------------------------------------------

    print("\n===== ANOMALY DISTRIBUTION =====")

    print(
        result["status"]
        .value_counts()
    )

    print("\n===== TOP ANOMALOUS RECORDS =====")

    print(
        result
        .sort_values(
            "anomaly_score",
            ascending=False
        )
        .head(5)
        .to_string(index=False)
    )


# ============================================================
# COMBINE ALL DATASETS
# ============================================================

final_df = pd.concat(
    all_results,
    ignore_index=True
)

output_path = os.path.join(
    OUTPUT_DIR,
    "anomaly_detection_all.csv"
)

final_df.to_csv(
    output_path,
    index=False
)

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("FINAL ANOMALY DETECTION SUMMARY")
print("=" * 60)

print(
    f"Total records: {len(final_df)}"
)

print(
    f"Total engines: "
    f"{final_df['unit_id'].nunique()} "
    f"(across all datasets)"
)

print("\nOverall status distribution:")

print(
    final_df["status"]
    .value_counts()
)

print("\nDataset distribution:")

print(
    pd.crosstab(
        final_df["dataset"],
        final_df["status"]
    )
)

print("\nSaved:")

print(output_path)