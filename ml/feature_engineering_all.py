import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "ml" / "outputs"

SENSORS = [f"sensor_{i}" for i in range(1, 22)]

# Sensors identified as constant in FD001.
# We will verify these across all datasets before final model training.
CONSTANT_SENSORS = [
    "sensor_1",
    "sensor_5",
    "sensor_10",
    "sensor_16",
    "sensor_18",
    "sensor_19",
]


def create_features(df):

    df = df.copy()

    # Sort so rolling features are calculated correctly
    df = df.sort_values(["unit_id", "cycle"]).reset_index(drop=True)

    # Remove sensors that are constant in FD001
    # We will later verify whether they are constant across all datasets.
    usable_sensors = [
        s for s in SENSORS
        if s not in CONSTANT_SENSORS
    ]

    for sensor in usable_sensors:

        # Difference from previous cycle
        df[f"{sensor}_diff"] = (
            df.groupby("unit_id")[sensor]
            .diff()
            .fillna(0)
        )

        # 5-cycle rolling average
        df[f"{sensor}_rolling_mean"] = (
            df.groupby("unit_id")[sensor]
            .transform(
                lambda x: x.rolling(
                    window=5,
                    min_periods=1
                ).mean()
            )
        )

        # 5-cycle rolling standard deviation
        df[f"{sensor}_rolling_std"] = (
            df.groupby("unit_id")[sensor]
            .transform(
                lambda x: x.rolling(
                    window=5,
                    min_periods=1
                ).std()
            )
            .fillna(0)
        )

    return df


def process_dataset(dataset):

    input_file = OUTPUT_DIR / f"{dataset.lower()}_train_with_rul.csv"

    df = pd.read_csv(input_file)

    print("\n" + "=" * 60)
    print(f"FEATURE ENGINEERING: {dataset}")
    print("=" * 60)

    print("Original shape:", df.shape)

    df = create_features(df)

    print("New shape:", df.shape)

    output_file = (
        OUTPUT_DIR /
        f"{dataset.lower()}_train_features.csv"
    )

    df.to_csv(output_file, index=False)

    print("Saved:")
    print(output_file)

    return df


if __name__ == "__main__":

    datasets = [
        "FD001",
        "FD002",
        "FD003",
        "FD004"
    ]

    for dataset in datasets:
        process_dataset(dataset)