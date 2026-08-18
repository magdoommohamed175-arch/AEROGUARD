import pandas as pd
import numpy as np
import joblib

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


# ==========================================
# 1. PATHS
# ==========================================

TEST_PATH = "data/FD001/test_FD001.txt"
RUL_PATH = "data/FD001/RUL_FD001.txt"
MODEL_PATH = "ml/models/rul_xgboost.pkl"


# ==========================================
# 2. COLUMN NAMES
# ==========================================

columns = [
    "unit_id",
    "cycle",
    "setting_1",
    "setting_2",
    "setting_3",
]

for i in range(1, 22):
    columns.append(f"sensor_{i}")


# ==========================================
# 3. LOAD TEST DATA
# ==========================================

test_df = pd.read_csv(
    TEST_PATH,
    sep=r"\s+",
    header=None,
    names=columns
)

print("\n===== TEST DATA =====")
print("Shape:", test_df.shape)
print("Engines:", test_df["unit_id"].nunique())


# ==========================================
# 4. LOAD TRUE RUL
# ==========================================

true_rul = pd.read_csv(
    RUL_PATH,
    sep=r"\s+",
    header=None,
    names=["RUL"]
)

print("\n===== TRUE RUL =====")
print("Number of RUL values:", len(true_rul))


# ==========================================
# 5. SELECT FEATURES
# ==========================================

constant_sensors = [
    "sensor_1",
    "sensor_5",
    "sensor_10",
    "sensor_16",
    "sensor_18",
    "sensor_19"
]

sensor_columns = [
    f"sensor_{i}"
    for i in range(1, 22)
    if f"sensor_{i}" not in constant_sensors
]

setting_columns = [
    "setting_1",
    "setting_2",
    "setting_3"
]

features = setting_columns + sensor_columns


# ==========================================
# 6. GET LAST CYCLE OF EACH TEST ENGINE
# ==========================================

last_cycles = (
    test_df
    .groupby("unit_id")
    .tail(1)
    .sort_values("unit_id")
)

X_test = last_cycles[features]


# ==========================================
# 7. LOAD MODEL
# ==========================================

model = joblib.load(MODEL_PATH)

print("\n===== MODEL LOADED =====")
print(MODEL_PATH)


# ==========================================
# 8. PREDICT RUL
# ==========================================

predicted_rul = model.predict(X_test)


# ==========================================
# 9. COMPARE WITH TRUE RUL
# ==========================================

actual_rul = true_rul["RUL"].values


# ==========================================
# 10. METRICS
# ==========================================

rmse = np.sqrt(
    mean_squared_error(
        actual_rul,
        predicted_rul
    )
)

mae = mean_absolute_error(
    actual_rul,
    predicted_rul
)

r2 = r2_score(
    actual_rul,
    predicted_rul
)


print("\n===== FINAL TEST RESULTS =====")

print(f"RMSE: {rmse:.4f}")
print(f"MAE : {mae:.4f}")
print(f"R²  : {r2:.4f}")


# ==========================================
# 11. SAVE PREDICTIONS
# ==========================================

results = pd.DataFrame({
    "engine_id": last_cycles["unit_id"].values,
    "actual_RUL": actual_rul,
    "predicted_RUL": predicted_rul
})

results["error"] = (
    results["predicted_RUL"]
    - results["actual_RUL"]
)

results.to_csv(
    "ml/outputs/fd001_test_predictions.csv",
    index=False
)


print("\n===== SAVED =====")
print(
    "ml/outputs/fd001_test_predictions.csv"
)

print("\n===== FIRST 10 PREDICTIONS =====")

print(results.head(10))