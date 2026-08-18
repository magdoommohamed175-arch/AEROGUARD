import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

COLUMNS = (
    ["unit_id", "cycle", "setting_1", "setting_2", "setting_3"]
    + [f"sensor_{i}" for i in range(1, 22)]
)

DATASETS = ["FD001", "FD002", "FD003", "FD004"]


def load_dataset(dataset):
    file_path = DATA_DIR / dataset / f"test_{dataset}.txt"

    return pd.read_csv(
        file_path,
        sep=r"\s+",
        header=None,
        names=COLUMNS
    )


def get_latest_telemetry(dataset, engine_id):
    df = load_dataset(dataset)

    engine = df[
        df["unit_id"] == engine_id
    ].sort_values("cycle")

    if engine.empty:
        raise ValueError(
            f"Engine {engine_id} not found in {dataset}"
        )

    row = engine.iloc[-1]

    telemetry = {
        "dataset": dataset,
        "engine_id": int(engine_id),
        "cycle": int(row["cycle"])
    }

    for sensor in [f"sensor_{i}" for i in range(1, 22)]:
        telemetry[sensor] = round(
            float(row[sensor]),
            4
        )

    telemetry["setting_1"] = round(
        float(row["setting_1"]),
        4
    )

    telemetry["setting_2"] = round(
        float(row["setting_2"]),
        4
    )

    telemetry["setting_3"] = round(
        float(row["setting_3"]),
        4
    )

    return telemetry


def simulate_next_cycle(dataset, engine_id):
    telemetry = get_latest_telemetry(
        dataset,
        engine_id
    )

    next_cycle = telemetry["cycle"] + 1

    simulated = telemetry.copy()

    simulated["cycle"] = next_cycle

    rng = np.random.default_rng(
        seed=engine_id + next_cycle
    )

    for sensor in [f"sensor_{i}" for i in range(1, 22)]:

        value = telemetry[sensor]

        noise = rng.normal(
            0,
            max(abs(value) * 0.005, 0.001)
        )

        simulated[sensor] = round(
            value + noise,
            4
        )

    return simulated


if __name__ == "__main__":

    print("=" * 60)
    print("AEROGUARD REAL-TIME TELEMETRY SIMULATOR")
    print("=" * 60)

    dataset = "FD001"
    engine_id = 20

    print("\nCurrent telemetry:")

    current = get_latest_telemetry(
        dataset,
        engine_id
    )

    print(
        f"Dataset : {current['dataset']}"
    )

    print(
        f"Engine  : {current['engine_id']}"
    )

    print(
        f"Cycle   : {current['cycle']}"
    )

    print("\nSimulated next cycle:")

    simulated = simulate_next_cycle(
        dataset,
        engine_id
    )

    print(
        f"Cycle   : {simulated['cycle']}"
    )

    print(
        f"Sensor 11: {simulated['sensor_11']}"
    )

    print(
        f"Sensor 13: {simulated['sensor_13']}"
    )

    print("\nTelemetry simulation successful.")