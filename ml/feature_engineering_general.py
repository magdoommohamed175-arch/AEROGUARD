import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "ml" / "outputs"

SENSORS = [f"sensor_{i}" for i in range(1, 22)]

DATASETS = ["FD001", "FD002", "FD003", "FD004"]


def create_features(df):

    df = df.copy()

    # Sort by engine and operating cycle
    df = df.sort_values(
        ["unit_id", "cycle"]
    ).reset_index(drop=True)

    # Create degradation features for ALL sensors.
    # We are not removing sensors based only on FD001.
    for sensor in SENSORS:

        # Change from previous cycle
        df[f"{sensor}_diff"] = (
            df.groupby("unit_id")[sensor]
            .diff()
            .fillna(0)
        )

        # Recent 5-cycle average
        df[f"{sensor}_rolling_mean"] = (
            df.groupby("unit_id")[sensor]
            .transform(
                lambda x: x.rolling(
                    window=5,
                    min_periods=1
                ).mean()
            )
        )

        # Recent 5-cycle variation
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

    input_file = (
        OUTPUT_DIR /
        f"{dataset.lower()}_train_with_rul.csv"
    )

    df = pd.read_csv(input_file)

    print("\n" + "=" * 60)
    print(f"GENERAL FEATURE ENGINEERING: {dataset}")
    print("=" * 60)

    print("Original shape:", df.shape)

    df = create_features(df)

    print("New shape:", df.shape)

    output_file = (
        OUTPUT_DIR /
        f"{dataset.lower()}_train_general_features.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print("Saved:")
    print(output_file)

    return df


if __name__ == "__main__":

    for dataset in DATASETS:
        process_dataset(dataset)

    print("\n" + "=" * 60)
    print("GENERAL FEATURE ENGINEERING COMPLETE")
    print("=" * 60)