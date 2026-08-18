import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Gauge,
  ShieldAlert,
  Wrench,
} from "lucide-react";

import {
  getEngine,
  getPrediction,
  getAnomaly,
  getMaintenance,
  getExplanation,
} from "../services/api";

import "./EngineIntelligence.css";

function EngineIntelligence() {
  const [dataset, setDataset] = useState("FD001");
  const [engineId, setEngineId] = useState("34");

  const [engine, setEngine] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [anomaly, setAnomaly] = useState(null);
  const [maintenance, setMaintenance] = useState(null);
  const [explanation, setExplanation] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadEngineData();
  }, []);

  const loadEngineData = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        engineResponse,
        predictionResponse,
        anomalyResponse,
        maintenanceResponse,
        explanationResponse,
      ] = await Promise.all([
        getEngine(dataset, engineId),
        getPrediction(dataset, engineId),
        getAnomaly(dataset, engineId),
        getMaintenance(dataset, engineId),
        getExplanation(dataset, engineId),
      ]);

      setEngine(engineResponse);
      setPrediction(predictionResponse);
      setAnomaly(anomalyResponse);
      setMaintenance(maintenanceResponse);
      setExplanation(explanationResponse);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to load engine intelligence from the AeroGuard backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleEngineChange = (event) => {
    setEngineId(event.target.value);
  };

  const handleDatasetChange = (event) => {
    setDataset(event.target.value);
  };

  if (loading) {
    return (
      <div className="engine-loading">
        <div className="engine-spinner"></div>

        <p>
          ANALYZING ENGINE TELEMETRY...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="engine-error">
        <AlertTriangle size={32} />

        <h2>Engine Intelligence Unavailable</h2>

        <p>{error}</p>

        <button onClick={loadEngineData}>
          RETRY
        </button>
      </div>
    );
  }

  return (
    <div className="engine-page">

      {/* TOP NAV */}

      <header className="engine-topbar">

        <div className="engine-brand">
          <span>✦</span>
          AEROGUARD
        </div>

        <div className="engine-breadcrumb">
          COMMAND CENTER
          <ChevronRight size={14} />
          ENGINE INTELLIGENCE
        </div>

        <div className="engine-status">
          <span></span>
          SYSTEM ONLINE
        </div>

      </header>

      {/* CONTENT */}

      <main className="engine-content">

        {/* PAGE HEADER */}

        <div className="engine-heading">

          <div>

            <div className="engine-heading-label">
              ENGINE INTELLIGENCE / PREDICTIVE ANALYTICS
            </div>

            <h1>
              Engine {engine.engine_id}
            </h1>

            <p>
              Predictive health intelligence for dataset{" "}
              <strong>{engine.dataset}</strong>.
            </p>

          </div>

          <div className="engine-controls">

            <select
              value={dataset}
              onChange={handleDatasetChange}
            >
              <option value="FD001">FD001</option>
              <option value="FD002">FD002</option>
              <option value="FD003">FD003</option>
              <option value="FD004">FD004</option>
            </select>

            <input
              type="number"
              min="1"
              value={engineId}
              onChange={handleEngineChange}
            />

            <button
              onClick={loadEngineData}
              className="analyze-button"
            >
              ANALYZE ENGINE
            </button>

          </div>

        </div>

        {/* ENGINE IDENTITY */}

        <div className="engine-identity">

          <div>
            <span>DATASET</span>
            <strong>{engine.dataset}</strong>
          </div>

          <div>
            <span>ENGINE</span>
            <strong>{engine.engine_id}</strong>
          </div>

          <div>
            <span>CURRENT CYCLE</span>
            <strong>{anomaly.cycle}</strong>
          </div>

          <div>
            <span>ACTUAL RUL</span>
            <strong>{prediction.actual_rul}</strong>
          </div>

          <div>
            <span>PREDICTION ERROR</span>
            <strong>
              {prediction.error}
            </strong>
          </div>

        </div>

        {/* KPI CARDS */}

        <section className="engine-kpi-grid">

          <KpiCard
            icon={<Clock3 />}
            label="PREDICTED RUL"
            value={engine.predicted_rul}
            suffix="cycles"
            description="Remaining useful life"
          />

          <KpiCard
            icon={<Gauge />}
            label="HEALTH SCORE"
            value={engine.health_score}
            suffix="/ 100"
            description="Current engine condition"
          />

          <KpiCard
            icon={<AlertTriangle />}
            label="ANOMALY SCORE"
            value={engine.anomaly_score}
            suffix="/ 100"
            description={engine.anomaly_status}
            warning
          />

          <KpiCard
            icon={<ShieldAlert />}
            label="RISK LEVEL"
            value={engine.risk}
            suffix=""
            description={`Priority score ${engine.priority_score}`}
            critical
          />

        </section>

        {/* STATUS + MAINTENANCE */}

        <section className="engine-info-grid">

          {/* ENGINE STATUS */}

          <div className="engine-panel">

            <PanelHeader
              icon={<Activity />}
              label="ENGINE STATUS"
              title="Current Condition"
            />

            <div className="condition-status">

              <div className="condition-indicator critical">
                <AlertTriangle size={22} />
              </div>

              <div>
                <strong>
                  {engine.risk}
                </strong>

                <span>
                  Risk classification
                </span>
              </div>

            </div>

            <div className="status-list">

              <StatusRow
                label="Anomaly Status"
                value={engine.anomaly_status}
                warning
              />

              <StatusRow
                label="Current Cycle"
                value={anomaly.cycle}
              />

              <StatusRow
                label="Top Abnormal Sensors"
                value={engine.top_abnormal_sensors}
              />

            </div>

          </div>

          {/* MAINTENANCE */}

          <div className="engine-panel maintenance-panel">

            <PanelHeader
              icon={<Wrench />}
              label="MAINTENANCE INTELLIGENCE"
              title="Recommended Action"
            />

            <div className="maintenance-priority">

              <div className="maintenance-icon">
                <ShieldAlert size={25} />
              </div>

              <div>

                <span>MAINTENANCE PRIORITY</span>

                <strong>
                  {maintenance.maintenance_priority}
                </strong>

              </div>

            </div>

            <div className="recommendation">

              <CheckCircle2 size={18} />

              <p>
                {maintenance.recommendation}
              </p>

            </div>

            <div className="priority-score-box">

              <span>PRIORITY SCORE</span>

              <strong>
                {maintenance.priority_score}
              </strong>

            </div>

          </div>

        </section>

        {/* EXPLAINABLE AI */}

        <section className="explanation-panel">

          <div className="explanation-header">

            <div>

              <div className="explanation-label">
                EXPLAINABLE AI / SHAP ANALYSIS
              </div>

              <h2>
                Why is the predicted RUL changing?
              </h2>

              <p>
                The following features have the strongest
                influence on the engine's predicted remaining
                useful life.
              </p>

            </div>

            <div className="shap-badge">
              <BrainCircuit size={17} />
              MODEL EXPLANATION
            </div>

          </div>

          <div className="explanation-list">

            {explanation.contributors.map(
              (item, index) => {

                const positive =
                  item.impact > 0;

                const maxImpact =
                  Math.max(
                    ...explanation.contributors.map(
                      (x) => Math.abs(x.impact)
                    )
                  );

                const width =
                  Math.max(
                    5,
                    (Math.abs(item.impact) /
                      maxImpact) *
                      100
                  );

                return (
                  <div
                    className="explanation-row"
                    key={`${item.feature}-${index}`}
                  >

                    <div className="feature-name">
                      {item.feature}
                    </div>

                    <div className="impact-track">

                      <div
                        className={`impact-bar ${
                          positive
                            ? "positive"
                            : "negative"
                        }`}
                        style={{
                          width: `${width}%`,
                        }}
                      ></div>

                    </div>

                    <div
                      className={`impact-value ${
                        positive
                          ? "positive-text"
                          : "negative-text"
                      }`}
                    >
                      {positive ? "+" : ""}
                      {item.impact.toFixed(2)}
                    </div>

                    <div className="impact-effect">
                      {positive
                        ? "↑ RUL"
                        : "↓ RUL"}
                    </div>

                  </div>
                );
              }
            )}

          </div>

        </section>

      </main>

    </div>
  );
}

/* =========================================================
   KPI CARD
========================================================= */

function KpiCard({
  icon,
  label,
  value,
  suffix,
  description,
  warning,
  critical,
}) {
  return (
    <div className="engine-kpi">

      <div className="kpi-top">

        <div className="kpi-icon">
          {icon}
        </div>

        <span>{label}</span>

      </div>

      <div
        className={`kpi-value ${
          warning
            ? "warning-value"
            : ""
        } ${
          critical
            ? "critical-value"
            : ""
        }`}
      >
        {value}

        <small>
          {suffix}
        </small>
      </div>

      <p>
        {description}
      </p>

    </div>
  );
}

/* =========================================================
   PANEL HEADER
========================================================= */

function PanelHeader({
  icon,
  label,
  title,
}) {
  return (
    <div className="panel-header">

      <div className="panel-icon">
        {icon}
      </div>

      <div>

        <span>{label}</span>

        <h2>{title}</h2>

      </div>

    </div>
  );
}

/* =========================================================
   STATUS ROW
========================================================= */

function StatusRow({
  label,
  value,
  warning,
}) {
  return (
    <div className="status-row">

      <span>
        {label}
      </span>

      <strong
        className={
          warning
            ? "status-warning"
            : ""
        }
      >
        {value}
      </strong>

    </div>
  );
}

export default EngineIntelligence;