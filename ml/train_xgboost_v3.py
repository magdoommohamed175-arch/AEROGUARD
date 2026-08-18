import pandas as pd
import numpy as np
from pathlib import Path

from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "ml" / "outputs"
MODEL_DIR = BASE_DIR / "ml" / "models"

DATASETS = ["FD001", "FD002", "FD003", "FD004"]

# Load all datasets
frames = []

for dataset in DATASETS:

    file_path = (
        OUTPUT_DIR /
        f"{dataset.lower()}_train_general_features.csv"
    )

    print(f"Loading {dataset}...")

    df = pd.read_csv(file_path)

    # Keep track of the dataset
    df["dataset_id"] = dataset

    frames.append(df)

data = pd.concat(
    frames,
    ignore_index=True
)

print("\n===== COMBINED DATA =====")
print("Shape:", data.shape)
print("Datasets:")
print(data["dataset_id"].value_counts())


# --------------------------------------------------
# FEATURES
# --------------------------------------------------

# Columns that must NOT be used as ML features
exclude_columns = [
    "unit_id",
    "RUL",
    "dataset_id"
]

features = [
    column
    for column in data.columns
    if column not in exclude_columns
]

print("\n===== FEATURES =====")
print("Number of features:", len(features))

X = data[features]
y = data["RUL"]


# --------------------------------------------------
# ENGINE-LEVEL TRAIN / VALIDATION SPLIT
# --------------------------------------------------

# Create a unique engine identifier because unit_id
# repeats across different FD datasets.
data["global_engine_id"] = (
    data["dataset_id"] + "_" +
    data["unit_id"].astype(str)
)

unique_engines = data["global_engine_id"].unique()

train_engines, validation_engines = train_test_split(
    unique_engines,
    test_size=0.20,
    random_state=42
)

train_mask = data["global_engine_id"].isin(train_engines)
validation_mask = data["global_engine_id"].isin(validation_engines)

X_train = data.loc[train_mask, features]
y_train = data.loc[train_mask, "RUL"]

X_val = data.loc[validation_mask, features]
y_val = data.loc[validation_mask, "RUL"]

print("\n===== ENGINE SPLIT =====")
print("Training engines:", len(train_engines))
print("Validation engines:", len(validation_engines))

print("Training rows:", len(X_train))
print("Validation rows:", len(X_val))


# --------------------------------------------------
# XGBOOST MODEL
# --------------------------------------------------

print("\n===== TRAINING GENERALIZED XGBOOST V3 =====")

model = XGBRegressor(
    n_estimators=500,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=4
)

model.fit(
    X_train,
    y_train,
    verbose=False
)

print("Training complete!")


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

predictions = model.predict(X_val)

rmse = np.sqrt(
    mean_squared_error(
        y_val,
        predictions
    )
)

mae = mean_absolute_error(
    y_val,
    predictions
)

r2 = r2_score(
    y_val,
    predictions
)

print("\n===== V3 VALIDATION RESULTS =====")
print(f"RMSE: {rmse:.4f}")
print(f"MAE : {mae:.4f}")
print(f"R²  : {r2:.4f}")


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

model_path = (
    MODEL_DIR /
    "rul_xgboost_v3.pkl"
)

joblib.dump(
    model,
    model_path
)

print("\nModel saved:")
print(model_path)


# --------------------------------------------------
# SAVE FEATURE IMPORTANCE
# --------------------------------------------------

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

importance_path = (
    OUTPUT_DIR /
    "v3_feature_importance.csv"
)

importance.to_csv(
    importance_path,
    index=False
)

print("\nTop 15 features:")
print(
    importance.head(15).to_string(
        index=False
    )
)

print("\nFeature importance saved:")
print(importance_path)