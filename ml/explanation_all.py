import pandas as pd
import numpy as np
import joblib
import shap

from pathlib import Path


# ============================================================
# AEROGUARD - GENERAL SHAP EXPLANATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "ml" / "models"
OUTPUT_DIR = BASE_DIR / "ml" / "outputs"

DATASETS = [
    "FD001",
    "FD002",
    "FD003",
    "FD004"
]

SENSORS = [
    f"sensor_{i}"
    for i in range(1, 22)
]

COLUMNS = (
    ["unit_id", "cycle", "setting_1", "setting_2", "setting_3"]
    + SENSORS
)


# ============================================================
# FEATURE ENGINEERING
# SAME AS V3 TEST PIPELINE
# ============================================================

def create_features(df):

    df = df.copy()

    df = df.sort_values(
        ["unit_id", "cycle"]
    ).reset_index(drop=True)

    for sensor in SENSORS:

        # Difference from previous cycle
        df[f"{sensor}_diff"] = (
            df.groupby("unit_id")[sensor]
            .diff()
            .fillna(0)
        )

        # 5-cycle rolling mean
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


# ============================================================
# LOAD TEST DATA
# ============================================================

def load_test_dataset(dataset):

    test_file = (
        DATA_DIR /
        dataset /
        f"test_{dataset}.txt"
    )

    test = pd.read_csv(
        test_file,
        sep=r"\s+",
        header=None,
        names=COLUMNS
    )

    return test


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AEROGUARD GENERAL SHAP EXPLAINABILITY")
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    model_path = (
        MODEL_DIR /
        "rul_xgboost_v3.pkl"
    )

    print("\nLoading V3 XGBoost model...")

    model = joblib.load(
        model_path
    )

    print("Model loaded successfully.")

    # --------------------------------------------------------
    # CREATE SHAP EXPLAINER
    # --------------------------------------------------------

    print("\nCreating SHAP TreeExplainer...")

    explainer = shap.TreeExplainer(
        model
    )

    print("SHAP explainer created.")

    all_explanations = []

    # ========================================================
    # PROCESS EACH DATASET
    # ========================================================

    for dataset in DATASETS:

        print("\n" + "=" * 60)
        print(f"EXPLAINING {dataset}")
        print("=" * 60)

        # ----------------------------------------------------
        # LOAD
        # ----------------------------------------------------

        test = load_test_dataset(
            dataset
        )

        print(
            "Raw test shape:",
            test.shape
        )

        print(
            "Test engines:",
            test["unit_id"].nunique()
        )

        # ----------------------------------------------------
        # FEATURE ENGINEERING
        # ----------------------------------------------------

        print(
            "Creating degradation features..."
        )

        test = create_features(
            test
        )

        # ----------------------------------------------------
        # SELECT FINAL OBSERVATION
        # OF EACH ENGINE
        # ----------------------------------------------------

        final_rows = (
            test.groupby("unit_id")["cycle"]
            .idxmax()
        )

        final_test = test.loc[
            final_rows
        ].copy()

        # ----------------------------------------------------
        # CREATE MODEL FEATURES
        # SAME AS V3 TEST SCRIPT
        # ----------------------------------------------------

        exclude_columns = [
            "unit_id",
            "last_cycle",
            "actual_RUL"
        ]

        # These columns don't exist in this script,
        # so only select actual model columns.
        features = [
            column
            for column in final_test.columns
            if column not in [
                "unit_id"
            ]
        ]

        X_test = final_test[
            features
        ]

        # ----------------------------------------------------
        # ENSURE EXACT MODEL FEATURE ORDER
        # ----------------------------------------------------

        model_features = (
            model.get_booster()
            .feature_names
        )

        if model_features is not None:

            missing_features = [
                feature
                for feature in model_features
                if feature not in X_test.columns
            ]

            if missing_features:

                raise ValueError(
                    "Missing model features: "
                    + str(missing_features)
                )

            X_test = X_test[
                model_features
            ]

        # ----------------------------------------------------
        # PREDICTIONS
        # ----------------------------------------------------

        predictions = model.predict(
            X_test
        )

        # ----------------------------------------------------
        # SHAP VALUES
        # ----------------------------------------------------

        print(
            "Calculating SHAP values..."
        )

        shap_values = explainer.shap_values(
            X_test
        )

        shap_values = np.asarray(
            shap_values
        )

        # ----------------------------------------------------
        # CREATE EXPLANATION FOR
        # EVERY ENGINE
        # ----------------------------------------------------

        for row_index in range(
            len(final_test)
        ):

            engine_id = int(
                final_test.iloc[
                    row_index
                ]["unit_id"]
            )

            predicted_rul = float(
                predictions[row_index]
            )

            engine_shap = shap_values[
                row_index
            ]

            # Sort by absolute SHAP impact
            ranking = np.argsort(
                np.abs(engine_shap)
            )[::-1]

            # Keep top 10 contributors
            top_n = 10

            for rank, feature_index in enumerate(
                ranking[:top_n],
                start=1
            ):

                feature_name = (
                    X_test.columns[
                        feature_index
                    ]
                )

                impact = float(
                    engine_shap[
                        feature_index
                    ]
                )

                all_explanations.append({

                    "dataset": dataset,

                    "engine_id": engine_id,

                    "predicted_RUL": round(
                        predicted_rul,
                        4
                    ),

                    "rank": rank,

                    "feature": feature_name,

                    "shap_value": round(
                        impact,
                        4
                    ),

                    "absolute_impact": round(
                        abs(impact),
                        4
                    ),

                    "effect": (
                        "increased predicted RUL"
                        if impact > 0
                        else
                        "decreased predicted RUL"
                    )
                })

        print(
            f"Generated explanations for "
            f"{len(final_test)} engines."
        )

    # ========================================================
    # SAVE
    # ========================================================

    final_explanations = pd.DataFrame(
        all_explanations
    )

    output_file = (
        OUTPUT_DIR /
        "explanations_all.csv"
    )

    final_explanations.to_csv(
        output_file,
        index=False
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 60)
    print("SHAP EXPLANATION COMPLETE")
    print("=" * 60)

    print(
        "Total engines:",
        final_explanations[
            ["dataset", "engine_id"]
        ].drop_duplicates().shape[0]
    )

    print(
        "Total explanation records:",
        len(final_explanations)
    )

    print("\nDataset distribution:")

    print(
        final_explanations[
            ["dataset", "engine_id"]
        ]
        .drop_duplicates()
        ["dataset"]
        .value_counts()
    )

    print("\nSaved:")
    print(output_file)

    # ========================================================
    # SAMPLE
    # ========================================================

    print("\n===== SAMPLE ENGINE EXPLANATION =====")

    sample = final_explanations[
        (final_explanations["dataset"] == "FD001") &
        (final_explanations["engine_id"] == 20)
    ]

    print(
        sample[
            [
                "feature",
                "shap_value",
                "effect"
            ]
        ].to_string(
            index=False
        )
    )