import { useEffect, useState } from "react";
import {
  ArrowLeft,
  AlertTriangle,
  Activity,
  ShieldAlert,
  Wrench,
} from "lucide-react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { getFaultInvestigation } from "../services/api";
import "./FaultInvestigation.css";

function FaultInvestigation() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const dataset = searchParams.get("dataset") || "FD001";
  const engineId = searchParams.get("engine") || "34";

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadInvestigation = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await getFaultInvestigation(
          dataset,
          engineId
        );

        setData(response);
      } catch (err) {
        console.error(
          "Failed to load fault investigation:",
          err
        );

        setError(
          "Unable to load fault investigation data."
        );
      } finally {
        setLoading(false);
      }
    };

    loadInvestigation();
  }, [dataset, engineId]);

  if (loading) {
    return (
      <div className="fault-loading">
        LOADING FAULT INVESTIGATION...
      </div>
    );
  }

  if (error) {
    return (
      <div className="fault-error">
        {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="fault-error">
        No fault investigation data available.
      </div>
    );
  }

  return (
    <div className="fault-page">

      {/* HEADER */}

      <header className="fault-header">

        <button
          className="fault-back"
          onClick={() => navigate("/command-center")}
        >
          <ArrowLeft size={17} />
          COMMAND CENTER
        </button>

        <div className="fault-title">
          <span>
            AEROGUARD / FAULT INVESTIGATION
          </span>

          <h2>
            Engine {engineId}
            <small> / {dataset}</small>
          </h2>
        </div>

        <div className="fault-status">
          <span></span>
          INVESTIGATION ACTIVE
        </div>

      </header>

      <main className="fault-content">

        {/* HERO */}

        <section className="fault-hero">

          <div>
            <p className="fault-eyebrow">
              AI-POWERED FAILURE ANALYSIS
            </p>

            <h1>
              Investigate
              <br />
              <span>engine risk.</span>
            </h1>
          </div>

          <p className="fault-description">
            AeroGuard combines anomaly detection,
            remaining useful life prediction and
            explainable AI to identify the factors
            contributing to abnormal engine behavior.
          </p>

        </section>

        {/* OVERVIEW */}

        <section className="fault-metrics">

          <Metric
            icon={<Activity size={18} />}
            label="PREDICTED RUL"
            value={`${Number(data.predicted_rul).toFixed(2)} cycles`}
          />

          <Metric
            icon={<ShieldAlert size={18} />}
            label="HEALTH SCORE"
            value={Number(data.health_score).toFixed(2)}
          />

          <Metric
            icon={<AlertTriangle size={18} />}
            label="ANOMALY SCORE"
            value={Number(data.anomaly_score).toFixed(2)}
          />

          <Metric
            icon={<Wrench size={18} />}
            label="PRIORITY SCORE"
            value={Number(data.priority_score).toFixed(2)}
          />

        </section>

        {/* RISK */}

        <section className="fault-risk-panel">

          <div className="fault-risk-icon">
            <AlertTriangle size={24} />
          </div>

          <div>
            <p>RISK ASSESSMENT</p>

            <h2>{data.risk}</h2>

            <span>
              Anomaly status: {data.anomaly_status}
            </span>
          </div>

          <div className="fault-maintenance">
            <p>MAINTENANCE PRIORITY</p>

            <strong>
              {data.maintenance_priority}
            </strong>
          </div>

        </section>

        {/* ABNORMAL SENSORS */}

        <section className="fault-panel">

          <div className="fault-panel-header">
            <div>
              <p>01 / ABNORMAL BEHAVIOR</p>
              <h2>Top Abnormal Sensors</h2>
            </div>
          </div>

          <div className="sensor-list">

            {data.top_abnormal_sensors.map(
              (sensor) => (
                <div
                  className="fault-sensor"
                  key={sensor}
                >
                  <AlertTriangle size={17} />
                  <strong>{sensor}</strong>
                  <span>ABNORMAL</span>
                </div>
              )
            )}

          </div>

        </section>

        {/* CONTRIBUTORS */}

        <section className="fault-panel">

          <div className="fault-panel-header">
            <div>
              <p>02 / EXPLAINABLE AI</p>
              <h2>Why Is This Engine At Risk?</h2>
            </div>

            <span className="shap-label">
              SHAP CONTRIBUTORS
            </span>
          </div>

          <div className="contributors">

            {data.contributors.map(
              (item, index) => {

                const negative =
                  Number(item.impact) < 0;

                return (
                  <div
                    className="contributor"
                    key={`${item.feature}-${index}`}
                  >

                    <div className="contributor-feature">
                      <strong>
                        {item.feature}
                      </strong>

                      <span>
                        {item.effect}
                      </span>
                    </div>

                    <div
                      className={`impact ${
                        negative
                          ? "negative"
                          : "positive"
                      }`}
                    >
                      {negative ? "↓" : "↑"}{" "}
                      {Math.abs(
                        Number(item.impact)
                      ).toFixed(2)}
                    </div>

                  </div>
                );
              }
            )}

          </div>

        </section>

        {/* RECOMMENDATION */}

        <section className="fault-recommendation">

          <div className="recommendation-icon">
            <Wrench size={22} />
          </div>

          <div>
            <p>MAINTENANCE RECOMMENDATION</p>

            <h2>
              {data.maintenance_priority}
            </h2>

            <span>
              {data.maintenance_recommendation}
            </span>
          </div>

        </section>

      </main>
    </div>
  );
}

function Metric({ icon, label, value }) {
  return (
    <div className="fault-metric">

      <div className="fault-metric-icon">
        {icon}
      </div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>

    </div>
  );
}

export default FaultInvestigation;