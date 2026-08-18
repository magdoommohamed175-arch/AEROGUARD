import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "ml" / "models"
OUTPUT_DIR = BASE_DIR / "ml" / "outputs"

COLUMNS = (
    ["unit_id", "cycle", "setting_1", "setting_2", "setting_3"]
    + [f"sensor_{i}" for i in range(1, 22)]
)

SENSORS = [f"sensor_{i}" for i in range(1, 22)]

DATASETS = ["FD001", "FD002", "FD003", "FD004"]


def create_features(df):

    df = df.copy()

    df = df.sort_values(
        ["unit_id", "cycle"]
    ).reset_index(drop=True)

    for sensor in SENSORS:

        df[f"{sensor}_diff"] = (
            df.groupby("unit_id")[sensor]
            .diff()
            .fillna(0)
        )

        df[f"{sensor}_rolling_mean"] = (
            df.groupby("unit_id")[sensor]
            .transform(
                lambda x: x.rolling(
                    window=5,
                    min_periods=1
                ).mean()
            )
        )

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


def load_test_dataset(dataset):

    test_file = (
        DATA_DIR /
        dataset /
        f"test_{dataset}.txt"
    )

    rul_file = (
        DATA_DIR /
        dataset /
        f"RUL_{dataset}.txt"
    )

    test = pd.read_csv(
        test_file,
        sep=r"\s+",
        header=None,
        names=COLUMNS
    )

    true_rul = pd.read_csv(
        rul_file,
        header=None,
        names=["RUL"]
    )

    return test, true_rul


def calculate_test_rul(test, true_rul):

    # Last observed cycle for every test engine
    last_cycles = (
        test.groupby("unit_id")["cycle"]
        .max()
        .reset_index()
    )

    last_cycles.columns = [
        "unit_id",
        "last_cycle"
    ]

    # The official RUL file gives the remaining life
    # at the final observed cycle.
    test = test.merge(
        last_cycles,
        on="unit_id"
    )

    test["actual_RUL"] = 0.0

    for engine_index, row in true_rul.iterrows():

        engine_id = engine_index + 1

        mask = test["unit_id"] == engine_id

        test.loc[mask, "actual_RUL"] = (
            row["RUL"] +
            test.loc[mask, "last_cycle"] -
            test.loc[mask, "cycle"]
        )

    return test


if __name__ == "__main__":

    model_path = MODEL_DIR / "rul_xgboost_v3.pkl"

    print("Loading V3 model...")

    model = joblib.load(model_path)

    print("Model loaded successfully.")

    all_results = []

    for dataset in DATASETS:

        print("\n" + "=" * 60)
        print(f"TESTING {dataset}")
        print("=" * 60)

        test, true_rul = load_test_dataset(dataset)

        print("Raw test shape:", test.shape)
        print("Test engines:", test["unit_id"].nunique())

        test = calculate_test_rul(
            test,
            true_rul
        )

        print("Creating degradation features...")

        test = create_features(test)

        # These columns are not ML features
        exclude_columns = [
            "unit_id",
            "last_cycle",
            "actual_RUL"
        ]

        features = [
            column
            for column in test.columns
            if column not in exclude_columns
        ]

        X_test = test[features]
        y_test = test["actual_RUL"]

        predictions = model.predict(X_test)

        # We only evaluate the final observation
        # of each test engine.
        final_rows = (
            test.groupby("unit_id")["cycle"]
            .idxmax()
        )

        y_actual = y_test.loc[final_rows]
        y_predicted = pd.Series(
            predictions,
            index=test.index
        ).loc[final_rows]

        rmse = np.sqrt(
            mean_squared_error(
                y_actual,
                y_predicted
            )
        )

        mae = mean_absolute_error(
            y_actual,
            y_predicted
        )

        r2 = r2_score(
            y_actual,
            y_predicted
        )

        print("\n===== RESULTS =====")
        print(f"RMSE: {rmse:.4f}")
        print(f"MAE : {mae:.4f}")
        print(f"R²  : {r2:.4f}")

        result = pd.DataFrame({
            "dataset": dataset,
            "engine_id": test.loc[
                final_rows,
                "unit_id"
            ].values,
            "actual_RUL": y_actual.values,
            "predicted_RUL": y_predicted.values
        })

        result["error"] = (
            result["predicted_RUL"] -
            result["actual_RUL"]
        )

        all_results.append(result)

    # Combine all results
    final_results = pd.concat(
        all_results,
        ignore_index=True
    )

    output_file = (
        OUTPUT_DIR /
        "v3_all_test_predictions.csv"
    )

    final_results.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 60)
    print("ALL DATASETS TESTING COMPLETE")
    print("=" * 60)

    print("\nTotal test engines:", len(final_results))

    print("\nSaved:")
    print(output_file)