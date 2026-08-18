import { useEffect, useState } from "react";
import {
  ArrowLeft,
  BarChart3,
  Activity,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { getEngineComparison } from "../services/api";
import "./Comparison.css";

function Comparison() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [dataset, setDataset] = useState(
    searchParams.get("dataset") || "FD001"
  );

  const [engine1, setEngine1] = useState(
    searchParams.get("engine1") || "34"
  );

  const [engine2, setEngine2] = useState(
    searchParams.get("engine2") || "35"
  );

  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadComparison = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await getEngineComparison(
          dataset,
          engine1,
          engine2
        );

        setComparison(response);
      } catch (err) {
        console.error("Failed to load comparison:", err);
        setError("Unable to load engine comparison.");
      } finally {
        setLoading(false);
      }
    };

    loadComparison();
  }, [dataset, engine1, engine2]);

  if (loading) {
    return (
      <div className="comparison-loading">
        LOADING ENGINE COMPARISON...
      </div>
    );
  }

  if (error) {
    return (
      <div className="comparison-error">
        <AlertTriangle size={24} />
        <h2>Comparison unavailable</h2>
        <p>{error}</p>

        <button onClick={() => navigate("/command-center")}>
          RETURN TO COMMAND CENTER
        </button>
      </div>
    );
  }

  if (!comparison) {
    return null;
  }

  const e1 = comparison.engine_1;
  const e2 = comparison.engine_2;

  const betterEngine = comparison.better_engine;

  return (
    <div className="comparison-page">

      {/* HEADER */}

      <header className="comparison-header">

        <button
          className="comparison-back"
          onClick={() => navigate("/command-center")}
        >
          <ArrowLeft size={18} />
          COMMAND CENTER
        </button>

        <div className="comparison-title">
          <span>AEROGUARD / ENGINE COMPARISON</span>

          <h2>
            Engine {e1.engine_id}
            <small> vs </small>
            Engine {e2.engine_id}
          </h2>
        </div>

        <div className="comparison-live">
          <span></span>
          LIVE ANALYTICS
        </div>

      </header>

      <main className="comparison-content">

        {/* HERO */}

        <section className="comparison-hero">

          <div>
            <p className="comparison-eyebrow">
              PREDICTIVE ENGINE BENCHMARKING
            </p>

            <h1>
              Engine
              <br />
              <span>comparison.</span>
            </h1>
          </div>

          <p className="comparison-description">
            Compare predictive health, remaining useful life,
            anomaly behavior and maintenance risk between two
            engines in the same dataset.
          </p>

        </section>

        {/* ENGINE SELECTOR */}

        <section className="comparison-controls">

          <div>
            <label>DATASET</label>

            <select
              value={dataset}
              onChange={(e) => setDataset(e.target.value)}
            >
              <option value="FD001">FD001</option>
              <option value="FD002">FD002</option>
              <option value="FD003">FD003</option>
              <option value="FD004">FD004</option>
            </select>
          </div>

          <div>
            <label>ENGINE 01</label>

            <input
              type="number"
              value={engine1}
              onChange={(e) => setEngine1(e.target.value)}
            />
          </div>

          <div>
            <label>ENGINE 02</label>

            <input
              type="number"
              value={engine2}
              onChange={(e) => setEngine2(e.target.value)}
            />
          </div>

        </section>

        {/* BETTER ENGINE */}

        <section className="better-engine">

          <div className="better-icon">
            <CheckCircle2 size={24} />
          </div>

          <div>
            <p>COMPARISON RESULT</p>

            <h2>
              Engine {betterEngine} performs better
            </h2>

            <span>
              Based on the predictive comparison score across
              health, anomaly and maintenance indicators.
            </span>
          </div>

          <div className="comparison-score">
            <strong>
              {comparison.comparison_score[
                `engine_${betterEngine}`
              ]}
            </strong>
            <span>BETTER SCORE</span>
          </div>

        </section>

        {/* ENGINE CARDS */}

        <section className="engine-comparison-grid">

          <EngineCard
            engine={e1}
            score={
              comparison.comparison_score[
                `engine_${e1.engine_id}`
              ]
            }
            isBetter={betterEngine === e1.engine_id}
          />

          <EngineCard
            engine={e2}
            score={
              comparison.comparison_score[
                `engine_${e2.engine_id}`
              ]
            }
            isBetter={betterEngine === e2.engine_id}
          />

        </section>

        {/* METRIC COMPARISON */}

        <section className="comparison-panel">

          <div className="comparison-panel-header">

            <div>
              <p>02 / PERFORMANCE MATRIX</p>
              <h2>Predictive Health Comparison</h2>
            </div>

            <BarChart3 size={22} />

          </div>

          <ComparisonRow
            label="Predicted RUL"
            value1={`${e1.predicted_rul} cycles`}
            value2={`${e2.predicted_rul} cycles`}
          />

          <ComparisonRow
            label="Actual RUL"
            value1={`${e1.actual_rul} cycles`}
            value2={`${e2.actual_rul} cycles`}
          />

          <ComparisonRow
            label="Health Score"
            value1={`${e1.health_score} / 100`}
            value2={`${e2.health_score} / 100`}
          />

          <ComparisonRow
            label="Anomaly Score"
            value1={`${e1.anomaly_score} / 100`}
            value2={`${e2.anomaly_score} / 100`}
          />

          <ComparisonRow
            label="Priority Score"
            value1={e1.priority_score}
            value2={e2.priority_score}
          />

        </section>

        {/* SENSOR COMPARISON */}

        <section className="comparison-panel">

          <div className="comparison-panel-header">

            <div>
              <p>03 / SENSOR ANALYSIS</p>
              <h2>Top Abnormal Sensors</h2>
            </div>

            <Activity size={22} />

          </div>

          <div className="sensor-comparison-grid">

            <div className="sensor-column">

              <span>
                ENGINE {e1.engine_id}
              </span>

              {e1.top_abnormal_sensors.map(
                (sensor) => (
                  <div
                    className="sensor-item"
                    key={sensor}
                  >
                    <AlertTriangle size={15} />
                    {sensor}
                  </div>
                )
              )}

            </div>

            <div className="sensor-column">

              <span>
                ENGINE {e2.engine_id}
              </span>

              {e2.top_abnormal_sensors.map(
                (sensor) => (
                  <div
                    className="sensor-item"
                    key={sensor}
                  >
                    <AlertTriangle size={15} />
                    {sensor}
                  </div>
                )
              )}

            </div>

          </div>

        </section>

      </main>
    </div>
  );
}


/* =========================================================
   ENGINE CARD
========================================================= */

function EngineCard({
  engine,
  score,
  isBetter,
}) {
  return (
    <div
      className={`engine-card ${
        isBetter ? "engine-card-better" : ""
      }`}
    >

      <div className="engine-card-header">

        <div>
          <p>ENGINE</p>

          <h2>{engine.engine_id}</h2>
        </div>

        {isBetter && (
          <span className="better-badge">
            BETTER
          </span>
        )}

      </div>

      <div className="engine-card-score">

        <strong>{score}</strong>

        <span>COMPARISON SCORE</span>

      </div>

      <div className="engine-card-status">

        <div>
          <span>RISK</span>
          <strong>{engine.risk}</strong>
        </div>

        <div>
          <span>ANOMALY</span>
          <strong>{engine.anomaly_score}</strong>
        </div>

      </div>

      <div className="engine-card-maintenance">

        <span>MAINTENANCE</span>

        <strong>
          {engine.maintenance_priority}
        </strong>

      </div>

    </div>
  );
}


/* =========================================================
   COMPARISON ROW
========================================================= */

function ComparisonRow({
  label,
  value1,
  value2,
}) {
  return (
    <div className="comparison-row">

      <span>{label}</span>

      <strong>{value1}</strong>

      <strong>{value2}</strong>

    </div>
  );
}

export default Comparison;