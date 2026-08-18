import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
import joblib
import matplotlib.pyplot as plt


# ==========================================
# 1. LOAD DATA
# ==========================================

DATA_PATH = "ml/outputs/fd001_train_with_rul.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)


# ==========================================
# 2. SELECT FEATURES
# ==========================================

# Sensors with zero variation in FD001
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
]

setting_columns = [
    "setting_1",
    "setting_2",
    "setting_3"
]

# Remove constant sensors
sensor_columns = [
    sensor
    for sensor in sensor_columns
    if sensor not in constant_sensors
]

features = setting_columns + sensor_columns

print("\n===== FEATURES USED =====")

for feature in features:
    print(feature)

print("\nNumber of features:", len(features))


# ==========================================
# 3. INPUT AND TARGET
# ==========================================

X = df[features]
y = df["RUL"]

print("\nX shape:", X.shape)
print("y shape:", y.shape)


# ==========================================
# 4. TRAIN / VALIDATION SPLIT
# ==========================================

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\n===== DATA SPLIT =====")
print("Training samples:", len(X_train))
print("Validation samples:", len(X_val))


# ==========================================
# 5. XGBOOST MODEL
# ==========================================

model = XGBRegressor(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)


# ==========================================
# 6. TRAIN
# ==========================================

print("\n===== TRAINING XGBOOST =====")

model.fit(X_train, y_train)

print("Training complete!")


# ==========================================
# 7. PREDICT
# ==========================================

y_pred = model.predict(X_val)


# ==========================================
# 8. EVALUATE
# ==========================================

rmse = np.sqrt(mean_squared_error(y_val, y_pred))
mae = mean_absolute_error(y_val, y_pred)
r2 = r2_score(y_val, y_pred)

print("\n===== MODEL RESULTS =====")
print(f"RMSE: {rmse:.4f}")
print(f"MAE : {mae:.4f}")
print(f"R²  : {r2:.4f}")


# ==========================================
# 9. FEATURE IMPORTANCE
# ==========================================

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print("\n===== TOP 10 FEATURES =====")
print(importance.head(10))

importance.to_csv(
    "ml/outputs/feature_importance.csv",
    index=False
)


# ==========================================
# 10. ACTUAL VS PREDICTED GRAPH
# ==========================================

plt.figure(figsize=(8, 6))

plt.scatter(
    y_val,
    y_pred,
    alpha=0.4
)

plt.xlabel("Actual RUL")
plt.ylabel("Predicted RUL")
plt.title("Actual vs Predicted RUL - XGBoost")

min_value = min(y_val.min(), y_pred.min())
max_value = max(y_val.max(), y_pred.max())

plt.plot(
    [min_value, max_value],
    [min_value, max_value],
    linestyle="--"
)

plt.tight_layout()

plt.savefig(
    "ml/outputs/actual_vs_predicted.png",
    dpi=300
)

plt.close()


# ==========================================
# 11. SAVE MODEL
# ==========================================

joblib.dump(
    model,
    "ml/models/rul_xgboost.pkl"
)

print("\n===== FILES SAVED =====")
print("Model:")
print("ml/models/rul_xgboost.pkl")

print("\nGraph:")
print("ml/outputs/actual_vs_predicted.png")

print("\nFeature importance:")
print("ml/outputs/feature_importance.csv")