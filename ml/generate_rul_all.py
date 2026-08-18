import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "ml" / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COLUMNS = (
    ["unit_id", "cycle", "setting_1", "setting_2", "setting_3"]
    + [f"sensor_{i}" for i in range(1, 22)]
)


def load_train(dataset_name):

    file_path = DATA_DIR / dataset_name / f"train_{dataset_name}.txt"

    df = pd.read_csv(
        file_path,
        sep=r"\s+",
        header=None,
        names=COLUMNS
    )

    return df


def generate_rul(df):

    max_cycles = (
        df.groupby("unit_id")["cycle"]
        .max()
        .reset_index()
    )

    max_cycles.columns = ["unit_id", "max_cycle"]

    df = df.merge(max_cycles, on="unit_id")

    df["RUL"] = df["max_cycle"] - df["cycle"]

    df.drop(columns=["max_cycle"], inplace=True)

    return df


if __name__ == "__main__":

    datasets = ["FD001", "FD002", "FD003", "FD004"]

    for dataset in datasets:

        print("\n" + "=" * 60)
        print(f"PROCESSING {dataset}")
        print("=" * 60)

        df = load_train(dataset)

        print("Original shape:", df.shape)

        df = generate_rul(df)

        print("RUL generated.")
        print("New shape:", df.shape)

        print("\nRUL statistics:")
        print(df["RUL"].describe())

        output_file = OUTPUT_DIR / f"{dataset.lower()}_train_with_rul.csv"

        df.to_csv(output_file, index=False)

        print("\nSaved:")
        print(output_file)