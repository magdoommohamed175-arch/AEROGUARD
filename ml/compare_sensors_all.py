import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "ml" / "outputs"

SENSORS = [f"sensor_{i}" for i in range(1, 22)]

DATASETS = ["FD001", "FD002", "FD003", "FD004"]


def analyze_dataset(dataset):

    file_path = OUTPUT_DIR / f"{dataset.lower()}_train_with_rul.csv"

    df = pd.read_csv(file_path)

    results = []

    for sensor in SENSORS:

        variance = df[sensor].var()
        std = df[sensor].std()

        results.append({
            "dataset": dataset,
            "sensor": sensor,
            "variance": variance,
            "std": std,
            "is_constant": variance == 0
        })

    return pd.DataFrame(results)


if __name__ == "__main__":

    all_results = []

    for dataset in DATASETS:

        print("\n" + "=" * 60)
        print(f"SENSOR ANALYSIS: {dataset}")
        print("=" * 60)

        result = analyze_dataset(dataset)

        all_results.append(result)

        print("\nConstant sensors:")

        constant_sensors = result[
            result["is_constant"]
        ]["sensor"].tolist()

        if constant_sensors:
            print(constant_sensors)
        else:
            print("None")

        print("\nLowest variance sensors:")

        print(
            result
            .sort_values("variance")
            [["sensor", "variance"]]
            .head(10)
            .to_string(index=False)
        )

    final_results = pd.concat(
        all_results,
        ignore_index=True
    )

    output_file = OUTPUT_DIR / "sensor_comparison_all.csv"

    final_results.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 60)
    print("FINAL SENSOR COMPARISON")
    print("=" * 60)

    pivot = final_results.pivot(
        index="sensor",
        columns="dataset",
        values="variance"
    )

    print(pivot.to_string())

    print("\nSaved:")
    print(output_file)