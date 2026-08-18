import pandas as pd

# ==========================================
# 1. LOAD DATASET
# ==========================================

DATA_PATH = "data/FD001/train_FD001.txt"

columns = [
    "unit_id",
    "cycle",
    "setting_1",
    "setting_2",
    "setting_3",
]

for i in range(1, 22):
    columns.append(f"sensor_{i}")

df = pd.read_csv(
    DATA_PATH,
    sep=r"\s+",
    header=None,
    names=columns
)

print("\n===== DATASET LOADED =====")
print("Shape:", df.shape)

print("\n===== NUMBER OF ENGINES =====")
print(df["unit_id"].nunique())

# ==========================================
# 2. GENERATE RUL
# ==========================================

max_cycle = df.groupby("unit_id")["cycle"].transform("max")

df["RUL"] = max_cycle - df["cycle"]

# ==========================================
# 3. CHECK RUL
# ==========================================

print("\n===== RUL SAMPLE =====")
print(
    df[
        ["unit_id", "cycle", "RUL"]
    ].head(20)
)

print("\n===== RUL STATISTICS =====")
print(df["RUL"].describe())

print("\n===== LAST 5 ROWS OF ENGINE 1 =====")
print(
    df[df["unit_id"] == 1][
        ["unit_id", "cycle", "RUL"]
    ].tail()
)

# ==========================================
# 4. SAVE PROCESSED DATA
# ==========================================

df.to_csv(
    "ml/outputs/fd001_train_with_rul.csv",
    index=False
)

print("\n===== SAVED =====")
print("ml/outputs/fd001_train_with_rul.csv")