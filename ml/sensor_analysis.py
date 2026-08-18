import pandas as pd

# ==========================================
# LOAD PROCESSED DATA
# ==========================================

DATA_PATH = "ml/outputs/fd001_train_with_rul.csv"

df = pd.read_csv(DATA_PATH)

print("\n===== DATA LOADED =====")
print("Shape:", df.shape)

# ==========================================
# SENSOR COLUMNS
# ==========================================

sensors = [f"sensor_{i}" for i in range(1, 22)]

# ==========================================
# SENSOR STATISTICS
# ==========================================

print("\n===== SENSOR STATISTICS =====")

stats = df[sensors].describe().T

stats["variance"] = df[sensors].var()

print(
    stats[
        ["mean", "std", "variance", "min", "max"]
    ]
)

# ==========================================
# CONSTANT SENSORS
# ==========================================

print("\n===== CONSTANT SENSORS =====")

constant_sensors = []

for sensor in sensors:
    if df[sensor].nunique() <= 1:
        constant_sensors.append(sensor)

print(constant_sensors)

# ==========================================
# LOW VARIANCE SENSORS
# ==========================================

print("\n===== LOW VARIANCE SENSORS =====")

variance = df[sensors].var()

print(
    variance.sort_values().head(10)
)

# ==========================================
# SAVE RESULTS
# ==========================================

stats.to_csv(
    "ml/outputs/sensor_statistics.csv"
)

print("\n===== SAVED =====")
print("ml/outputs/sensor_statistics.csv")