<div align="center">

# ✈️ AEROGUARD

### AI-Powered Predictive Maintenance & Engine Health Intelligence Platform

<p>
  <strong>Predict.</strong>&nbsp;&nbsp;
  <strong>Detect.</strong>&nbsp;&nbsp;
  <strong>Explain.</strong>&nbsp;&nbsp;
  <strong>Prevent.</strong>
</p>

<br>

<img src="https://img.shields.io/badge/AI-Predictive%20Maintenance-0B3A82?style=for-the-badge&logo=artificial-intelligence&logoColor=white">
<img src="https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black">
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white">
<img src="https://img.shields.io/badge/Python-ML-3776AB?style=for-the-badge&logo=python&logoColor=white">

<br>

<img src="https://img.shields.io/badge/CatBoost-ML%20Model-FFCC00?style=flat-square">
<img src="https://img.shields.io/badge/XGBoost-ML%20Model-189FDD?style=flat-square">
<img src="https://img.shields.io/badge/Random%20Forest-ML%20Model-228B22?style=flat-square">
<img src="https://img.shields.io/badge/SHAP-Explainable%20AI-8A2BE2?style=flat-square">

<br><br>

**An end-to-end aviation predictive-maintenance platform that transforms engine telemetry into actionable maintenance intelligence.**

</div>

---

# 🚀 What is AeroGuard?

**AeroGuard** is an AI-powered predictive-maintenance platform designed to analyze aircraft engine telemetry, predict **Remaining Useful Life (RUL)**, detect abnormal behavior, evaluate engine health, explain model decisions, compare engines, and prioritize maintenance actions.

The platform combines:

- 🤖 Machine Learning
- 📊 Multivariate telemetry analytics
- 🧠 Explainable AI
- 🚨 Anomaly detection
- ❤️ Engine health scoring
- ⚠️ Risk classification
- 🔧 Maintenance intelligence
- 🌐 REST APIs
- 🖥️ Interactive React dashboard

AeroGuard is developed and evaluated using the **NASA C-MAPSS turbofan engine dataset**.

---

# 🎯 The Problem

Aircraft engines continuously generate large amounts of sensor telemetry.

Traditional maintenance workflows can depend heavily on:

```text
Fixed Maintenance Schedules
          +
Manual Inspection
          +
Reactive Fault Detection
          +
Large Sensor Datasets.
    💡 Our Solution
┌──────────────────────────────┐
│     ENGINE SENSOR DATA       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│    DATA PREPROCESSING        │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│    FEATURE ENGINEERING       │
└──────────────┬───────────────┘
               ↓
       ┌───────┴────────┐
       ↓       ↓        ↓
   CatBoost XGBoost Random Forest
       └───────┬────────┘
               ↓
       ┌───────────────┐
       │ RUL PREDICTION│
       └───────┬───────┘
               ↓
    ┌──────────┼──────────┐
    ↓          ↓          ↓
 Health     Anomaly      Risk
 Score      Score       Level
    └──────────┼──────────┘
               ↓
       ┌───────────────┐
       │   SHAP / XAI  │
       └───────┬───────┘
               ↓
       ┌───────────────┐
       │  MAINTENANCE  │
       │ INTELLIGENCE  │
       └───────────────┘
🧠 Machine Learning Engine

AeroGuard uses three complementary tree-based models.

<div align="center">
🟡 CatBoost

Gradient Boosting

Builds decision trees sequentially to progressively improve predictions.

🔵 XGBoost

Optimized Gradient Boosting

Builds trees sequentially while aggressively reducing prediction error.

🟢 Random Forest

Bagging Ensemble

Combines predictions from many independent decision trees.
🏠 01 — Command Center

The central fleet dashboard provides:

Fleet overview
Risk distribution
Maintenance distribution
Priority engine ranking
Engine health information
Operational navigation

The goal is to give maintenance teams a single high-level operational view.

🧠 02 — Engine Intelligence

Engine Intelligence provides detailed predictive analytics for an individual engine.

Displays
Dataset
Engine ID
Current Cycle
Actual RUL
Predicted RUL
Prediction Error
Health Score
Anomaly Score
Risk Level
Priority Score
Engine Status
Abnormal Sensors
Maintenance Recommendation
SHAP Explanation
Example
╔══════════════════════════════════╗
║          ENGINE 34                ║
╠══════════════════════════════════╣
║ Predicted RUL       6.62 cycles  ║
║ Actual RUL          7.00 cycles  ║
║ Prediction Error   -0.38         ║
║ Health Score        4.99 / 100   ║
║ Anomaly Score      96.25 / 100   ║
║ Risk                CRITICAL      ║
║ Priority Score     95.19         ║
╚══════════════════════════════════╝
📊 03 — Telemetry Explorer

Telemetry Explorer provides historical sensor analysis.

The user selects:

Dataset
   ↓
Engine
   ↓
Sensors

The system then visualizes sensor behavior across operating cycles.

Chart
X-axis → Operating Cycle


Y-axis → Sensor Measurement

Up to four sensors are displayed simultaneously for a clean visualization.

Important

The four-sensor visualization is not a limitation of the underlying telemetry.

The system can work with the broader sensor information while displaying a smaller number of signals at once to prevent visual clutter.

📡 04 — Live Telemetry

Live Telemetry focuses on the current engine state.

It displays:

Current cycle
Sensor channel count
Current sensor measurements
Simulated next-cycle measurements
Current vs next-cycle comparison
CURRENT ENGINE
      ↓
CURRENT SENSOR VALUES
      ↓
SIMULATED NEXT CYCLE
      ↓
CURRENT vs NEXT

The graph dynamically changes according to the selected engine and the values returned by the backend.

📈 05 — Degradation Timeline

The Degradation Timeline shows how engine behavior evolves throughout its operating life.

Cycle 1
   ↓
Cycle 20
   ↓
Cycle 40
   ↓
Cycle 80
   ↓
Cycle 120
   ↓
Current State

This allows engineers to understand the historical degradation pattern rather than only looking at the current prediction.

🚨 06 — Fault Investigation

Fault Investigation brings the major analytical signals together.

Provides
Predicted RUL
Actual RUL
Anomaly score
Anomaly status
Health score
Risk
Priority score
Maintenance priority
Maintenance recommendation
Top abnormal sensors
SHAP contributors
Example
ENGINE 34


Predicted RUL       6.62 cycles
Actual RUL          7.00 cycles


Anomaly Score       96.25
Anomaly Status      WARNING


Health Score        4.99
Risk                CRITICAL


Priority Score      95.19


Top Abnormal Sensors
• sensor_4
• sensor_11
• sensor_14


Maintenance
→ IMMEDIATE INSPECTION
⚖️ 07 — Engine Comparison

AeroGuard can compare two engines using multiple indicators.

Comparison factors
Predicted RUL
Health score
Anomaly score
Risk
Priority score
Maintenance priority
Abnormal sensors

Example:

ENGINE 34
Comparison Score → 0


ENGINE 35
Comparison Score → 4


Better Engine → ENGINE 35

The comparison score is a backend decision metric, not a replacement for the actual RUL or health score.

🔧 08 — Maintenance Intelligence

AeroGuard converts analytical outputs into actionable maintenance information.

Instead of displaying only:

RUL = 6.62 cycles

the platform can translate this into:

RISK
CRITICAL


PRIORITY
IMMEDIATE INSPECTION

This connects:

ML Prediction
      ↓
Engine Condition
      ↓
Risk Assessment
      ↓
Maintenance Decision
🏗️ System Architecture
                         AEROGUARD
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Engine Telemetry    │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ FastAPI Backend     │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ ML Pipeline         │
                  └──────────┬──────────┘
                             ↓
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
          CatBoost        XGBoost      Random Forest
              └──────────────┼──────────────┘
                             ↓
                     Weighted Ensemble
                             ↓
                        RUL Prediction
                             ↓
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
           Health         Anomaly          Risk
              └──────────────┼──────────────┘
                             ↓
                         SHAP / XAI
                             ↓
                  Maintenance Intelligence
                             ↓
                    React Frontend
                             ↓
                    AeroGuard Dashboard
🛠️ AeroGuard — Tech Stack
🎨 Frontend
React.js — UI development
JavaScript (ES6+) — application logic
React Router — page navigation
Recharts — telemetry, risk, and analytics visualization
Lucide React — interface icons
CSS3 — responsive dashboard styling
Vite — frontend development/build tooling
⚙️ Backend
Python — backend & ML ecosystem
FastAPI — REST API development
Uvicorn — ASGI server
REST APIs — frontend ↔ backend communication
🤖 Machine Learning
Scikit-learn — ML pipeline and evaluation
CatBoost — gradient boosting RUL model
XGBoost — gradient boosting RUL model
Random Forest — ensemble regression model
SHAP — Explainable AI / feature contribution analysis
Pandas — data processing
NumPy — numerical computation
📊 Data & Analytics
NASA C-MAPSS — turbofan engine degradation dataset
Multivariate sensor telemetry
Feature Engineering
RUL Prediction
Anomaly Detection
Health Scoring
Risk Classification
Maintenance Prioritization
🔧 Development & Tools
Git — version control
GitHub — source-code hosting
Jupyter Notebook — ML experimentation and analysis
VS Code — development environment

