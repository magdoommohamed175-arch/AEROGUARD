import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


# ==========================================
# 1. LOAD TEST DATA
# ==========================================

TEST_PATH = "data/FD001/test_FD001.txt"
RUL_PATH = "data/FD001/RUL_FD001.txt"
MODEL_PATH = "ml/models/rul_xgboost_v2.pkl"

columns = [
    "unit_id",
    "cycle",
    "setting_1",
    "setting_2",
    "setting_3"
]

for i in range(1, 22):
    columns.append(f"sensor_{i}")


test_df = pd.read_csv(
    TEST_PATH,
    sep=r"\s+",
    header=None,
    names=columns
)

true_rul = pd.read_csv(
    RUL_PATH,
    sep=r"\s+",
    header=None,
    names=["RUL"]
)


# ==========================================
# 2. SORT DATA
# ==========================================

test_df = test_df.sort_values(
    ["unit_id", "cycle"]
).reset_index(drop=True)


# ==========================================
# 3. SENSOR SELECTION
# ==========================================

constant_sensors = [
    "sensor_1",
    "sensor_5",
    "sensor_10",
    "sensor_16",
    "sensor_18",
    "sensor_19"
]

sensors = [
    f"sensor_{i}"
    for i in range(1, 22)
    if f"sensor_{i}" not in constant_sensors
]


# ==========================================
# 4. CREATE SAME FEATURES AS V2
# ==========================================

for sensor in sensors:

    test_df[f"{sensor}_diff"] = (
        test_df.groupby("unit_id")[sensor]
        .diff()
    )

    test_df[f"{sensor}_rolling_mean"] = (
        test_df.groupby("unit_id")[sensor]
        .transform(
            lambda x: x.rolling(
                window=5,
                min_periods=1
            ).mean()
        )
    )

    test_df[f"{sensor}_rolling_std"] = (
        test_df.groupby("unit_id")[sensor]
        .transform(
            lambda x: x.rolling(
                window=5,
                min_periods=1
            ).std()
        )
    )


test_df = test_df.fillna(0)


# ==========================================
# 5. FEATURE LIST
# ==========================================

settings = [
    "setting_1",
    "setting_2",
    "setting_3"
]

features = settings + ["cycle"]

for sensor in sensors:

    features.append(sensor)
    features.append(f"{sensor}_diff")
    features.append(f"{sensor}_rolling_mean")
    features.append(f"{sensor}_rolling_std")


# ==========================================
# 6. GET FINAL OBSERVATION OF EACH ENGINE
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


# ==========================================
# 8. PREDICT
# ==========================================

predicted_rul = model.predict(X_test)

actual_rul = true_rul["RUL"].values


# ==========================================
# 9. EVALUATION
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


print("\n===== V2 FINAL TEST RESULTS =====")

print(f"RMSE: {rmse:.4f}")
print(f"MAE : {mae:.4f}")
print(f"R²  : {r2:.4f}")


# ==========================================
# 10. SAVE RESULTS
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
    "ml/outputs/fd001_test_predictions_v2.csv",
    index=False
)

print("\nSaved:")
print("ml/outputs/fd001_test_predictions_v2.csv")

print("\n===== FIRST 10 =====")
print(results.head(10))