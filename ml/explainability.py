import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt


# ==========================================
# 1. LOAD DATA AND MODEL
# ==========================================

DATA_PATH = "ml/outputs/fd001_train_with_rul.csv"
MODEL_PATH = "ml/models/rul_xgboost_v2.pkl"

df = pd.read_csv(DATA_PATH)

model = joblib.load(MODEL_PATH)

print("Model loaded successfully")


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


X = df[features]


# ==========================================
# 6. CREATE SHAP EXPLAINER
# ==========================================

print("Creating SHAP explainer...")

explainer = shap.TreeExplainer(model)

# Use a sample to make explanation faster
sample = X.sample(
    n=min(1000, len(X)),
    random_state=42
)

shap_values = explainer.shap_values(sample)

print("SHAP analysis complete")


# ==========================================
# 7. GLOBAL FEATURE IMPORTANCE
# ==========================================

mean_abs_shap = np.abs(shap_values).mean(axis=0)

importance = pd.DataFrame({
    "feature": features,
    "mean_abs_shap": mean_abs_shap
})

importance = importance.sort_values(
    "mean_abs_shap",
    ascending=False
)

print("\n===== TOP 15 FEATURES =====")
print(importance.head(15))


importance.to_csv(
    "ml/outputs/shap_feature_importance.csv",
    index=False
)


# ==========================================
# 8. SHAP SUMMARY PLOT
# ==========================================

plt.figure()

shap.summary_plot(
    shap_values,
    sample,
    show=False,
    max_display=15
)

plt.tight_layout()

plt.savefig(
    "ml/outputs/shap_summary.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ==========================================
# 9. SAVE TOP FEATURES
# ==========================================

top_features = importance.head(10)

print("\n===== TOP 10 EXPLANATION FEATURES =====")

for _, row in top_features.iterrows():

    print(
        f"{row['feature']}: "
        f"{row['mean_abs_shap']:.6f}"
    )


print("\n===== FILES SAVED =====")

print(
    "ml/outputs/shap_feature_importance.csv"
)

print(
    "ml/outputs/shap_summary.png"
)