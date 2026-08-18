import pandas as pd
import numpy as np
import joblib

from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


# ==========================================
# 1. LOAD TRAINING DATA
# ==========================================

DATA_PATH = "ml/outputs/fd001_train_with_rul.csv"

df = pd.read_csv(DATA_PATH)

print("Original shape:", df.shape)


# ==========================================
# 2. SORT BY ENGINE AND CYCLE
# ==========================================

df = df.sort_values(
    ["unit_id", "cycle"]
).reset_index(drop=True)


# ==========================================
# 3. SELECT USEFUL SENSORS
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
# 4. CREATE TEMPORAL FEATURES
# ==========================================

print("\nCreating degradation features...")

for sensor in sensors:

    # Previous value
    df[f"{sensor}_diff"] = (
        df.groupby("unit_id")[sensor]
        .diff()
    )

    # Rolling mean
    df[f"{sensor}_rolling_mean"] = (
        df.groupby("unit_id")[sensor]
        .transform(
            lambda x: x.rolling(
                window=5,
                min_periods=1
            ).mean()
        )
    )

    # Rolling standard deviation
    df[f"{sensor}_rolling_std"] = (
        df.groupby("unit_id")[sensor]
        .transform(
            lambda x: x.rolling(
                window=5,
                min_periods=1
            ).std()
        )
    )


# Replace NaN values created by diff/std
df = df.fillna(0)


# ==========================================
# 5. CREATE FEATURE LIST
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


print("\nNumber of features:", len(features))


# ==========================================
# 6. TRAIN/VALIDATION BY ENGINE
# ==========================================

# IMPORTANT:
# Split complete engines instead of individual rows.

engine_ids = df["unit_id"].unique()

np.random.seed(42)

np.random.shuffle(engine_ids)

split = int(len(engine_ids) * 0.8)

train_engines = engine_ids[:split]
val_engines = engine_ids[split:]

train_df = df[
    df["unit_id"].isin(train_engines)
]

val_df = df[
    df["unit_id"].isin(val_engines)
]

X_train = train_df[features]
y_train = train_df["RUL"]

X_val = val_df[features]
y_val = val_df["RUL"]


print("\n===== ENGINE SPLIT =====")
print("Training engines:", len(train_engines))
print("Validation engines:", len(val_engines))


# ==========================================
# 7. XGBOOST
# ==========================================

model = XGBRegressor(
    n_estimators=700,
    max_depth=6,
    learning_rate=0.04,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)


# ==========================================
# 8. TRAIN
# ==========================================

print("\n===== TRAINING V2 =====")

model.fit(
    X_train,
    y_train
)

print("Training complete!")


# ==========================================
# 9. VALIDATION
# ==========================================

pred = model.predict(X_val)

rmse = np.sqrt(
    mean_squared_error(y_val, pred)
)

mae = mean_absolute_error(
    y_val,
    pred
)

r2 = r2_score(
    y_val,
    pred
)


print("\n===== V2 VALIDATION RESULTS =====")

print(f"RMSE: {rmse:.4f}")
print(f"MAE : {mae:.4f}")
print(f"R²  : {r2:.4f}")


# ==========================================
# 10. SAVE MODEL
# ==========================================

joblib.dump(
    model,
    "ml/models/rul_xgboost_v2.pkl"
)

print("\nModel saved:")
print("ml/models/rul_xgboost_v2.pkl")