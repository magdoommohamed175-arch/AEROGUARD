import pandas as pd
import numpy as np
import joblib
import shap


# ==========================================
# CONFIGURATION
# ==========================================

ENGINE_ID = 20

DATA_PATH = "data/FD001/test_FD001.txt"
MODEL_PATH = "ml/models/rul_xgboost_v2.pkl"

OUTPUT_PATH = "ml/outputs/engine_explanation.csv"


# ==========================================
# 1. LOAD TEST DATA
# ==========================================

columns = [
    "unit_id",
    "cycle",
    "setting_1",
    "setting_2",
    "setting_3"
]

for i in range(1, 22):
    columns.append(f"sensor_{i}")


df = pd.read_csv(
    DATA_PATH,
    sep=r"\s+",
    header=None,
    names=columns
)


# ==========================================
# 2. SORT DATA
# ==========================================

df = df.sort_values(
    ["unit_id", "cycle"]
).reset_index(drop=True)


# ==========================================
# 3. SELECT SENSORS
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

print("Creating degradation features...")

for sensor in sensors:

    df[f"{sensor}_diff"] = (
        df.groupby("unit_id")[sensor]
        .diff()
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
    )


df = df.fillna(0)


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
# 6. GET ENGINE
# ==========================================

engine_data = df[
    df["unit_id"] == ENGINE_ID
]

if engine_data.empty:
    raise ValueError(
        f"Engine {ENGINE_ID} not found in test dataset."
    )


# Use the latest available cycle
engine_row = engine_data.tail(1)

X_engine = engine_row[features]


# ==========================================
# 7. LOAD MODEL
# ==========================================

model = joblib.load(MODEL_PATH)

print("Model loaded.")


# ==========================================
# 8. PREDICT RUL
# ==========================================

predicted_rul = model.predict(
    X_engine
)[0]

print("\n===== ENGINE PREDICTION =====")
print(f"Engine ID: {ENGINE_ID}")
print(f"Current cycle: {engine_row['cycle'].iloc[0]}")
print(f"Predicted RUL: {predicted_rul:.2f} cycles")


# ==========================================
# 9. SHAP EXPLANATION
# ==========================================

print("\nCreating SHAP explanation...")

explainer = shap.TreeExplainer(model)

shap_values = explainer.shap_values(
    X_engine
)

shap_values = np.array(shap_values).reshape(-1)

# Get feature values
feature_values = X_engine.iloc[0].values


# ==========================================
# 10. BUILD EXPLANATION TABLE
# ==========================================

explanation = pd.DataFrame({
    "feature": features,
    "feature_value": feature_values,
    "shap_value": shap_values,
    "absolute_impact": np.abs(shap_values)
})

explanation = explanation.sort_values(
    "absolute_impact",
    ascending=False
)


# ==========================================
# 11. TOP CONTRIBUTORS
# ==========================================

top = explanation.head(10)

print("\n===== TOP CONTRIBUTORS =====")

for _, row in top.iterrows():

    direction = (
        "increased predicted RUL"
        if row["shap_value"] > 0
        else "decreased predicted RUL"
    )

    print(
        f"{row['feature']}: "
        f"{row['shap_value']:.4f} "
        f"→ {direction}"
    )


# ==========================================
# 12. SAVE
# ==========================================

top.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n===== SAVED =====")
print(OUTPUT_PATH)