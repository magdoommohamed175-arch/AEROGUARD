import pandas as pd

# ==========================================
# LOAD V2 PREDICTIONS
# ==========================================

INPUT_PATH = "ml/outputs/fd001_test_predictions_v2.csv"

df = pd.read_csv(INPUT_PATH)

print("Loaded predictions:", df.shape)


# ==========================================
# HEALTH SCORE
# ==========================================

def calculate_health_score(rul):

    if rul >= 50:
        # 50+ RUL maps to 70-100
        score = 70 + ((rul - 50) / 75) * 30

    elif rul >= 20:
        # 20-50 RUL maps to 30-70
        score = 30 + ((rul - 20) / 30) * 40

    else:
        # 0-20 RUL maps to 0-30
        score = (rul / 20) * 30

    return max(0, min(100, score))


df["health_score"] = (
    df["predicted_RUL"]
    .apply(calculate_health_score)
    .round(2)
)


# ==========================================
# RISK LEVEL
# ==========================================

def get_risk(rul):

    if rul > 50:
        return "LOW"

    elif rul >= 20:
        return "MEDIUM"

    else:
        return "HIGH"


df["risk_level"] = df["predicted_RUL"].apply(get_risk)


# ==========================================
# MAINTENANCE ACTION
# ==========================================

def get_action(risk):

    if risk == "LOW":
        return "Continue monitoring"

    elif risk == "MEDIUM":
        return "Schedule inspection"

    else:
        return "Immediate maintenance review"


df["maintenance_action"] = (
    df["risk_level"].apply(get_action)
)


# ==========================================
# SAVE
# ==========================================

output = "ml/outputs/engine_health_assessment.csv"

df.to_csv(
    output,
    index=False
)


# ==========================================
# DISPLAY
# ==========================================

print("\n===== ENGINE HEALTH ASSESSMENT =====")

print(
    df[
        [
            "engine_id",
            "predicted_RUL",
            "health_score",
            "risk_level",
            "maintenance_action"
        ]
    ].head(20)
)

print("\n===== RISK DISTRIBUTION =====")

print(
    df["risk_level"].value_counts()
)

print("\nSaved:")
print(output)