import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

COLUMNS = (
    ["unit_id", "cycle", "setting_1", "setting_2", "setting_3"]
    + [f"sensor_{i}" for i in range(1, 22)]
)


def load_dataset(dataset_name):
    dataset_path = DATA_DIR / dataset_name

    train_file = dataset_path / f"train_{dataset_name}.txt"
    test_file = dataset_path / f"test_{dataset_name}.txt"
    rul_file = dataset_path / f"RUL_{dataset_name}.txt"

    train = pd.read_csv(
        train_file,
        sep=r"\s+",
        header=None,
        names=COLUMNS
    )

    test = pd.read_csv(
        test_file,
        sep=r"\s+",
        header=None,
        names=COLUMNS
    )

    rul = pd.read_csv(
        rul_file,
        header=None,
        names=["RUL"]
    )

    return train, test, rul


def inspect_dataset(dataset_name):
    train, test, rul = load_dataset(dataset_name)

    print("\n" + "=" * 60)
    print(f"DATASET: {dataset_name}")
    print("=" * 60)

    print(f"Train shape: {train.shape}")
    print(f"Test shape : {test.shape}")
    print(f"RUL shape  : {rul.shape}")

    print(f"Training engines: {train['unit_id'].nunique()}")
    print(f"Test engines    : {test['unit_id'].nunique()}")

    print(f"Training sensors: {len([c for c in train.columns if c.startswith('sensor_')])}")

    print(f"Training missing values: {train.isnull().sum().sum()}")
    print(f"Test missing values    : {test.isnull().sum().sum()}")

    print(f"Max training cycle: {train['cycle'].max()}")
    print(f"Max test cycle    : {test['cycle'].max()}")

    print("\nRUL statistics:")
    print(rul["RUL"].describe())

    return train, test, rul


if __name__ == "__main__":

    datasets = ["FD001", "FD002", "FD003", "FD004"]

    for dataset in datasets:
        inspect_dataset(dataset)