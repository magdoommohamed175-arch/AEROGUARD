import { useEffect, useState } from "react";
import {
  ArrowLeft,
  Activity,
  AlertTriangle,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useNavigate, useSearchParams } from "react-router-dom";
import { getDegradation } from "../services/api";
import "./DegradationTimeline.css";

function DegradationTimeline() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [dataset, setDataset] = useState(
    searchParams.get("dataset") || "FD001"
  );

  const [engineId, setEngineId] = useState(
    searchParams.get("engine") || "34"
  );

  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDegradation = async () => {
      try {
        setLoading(true);
        setError("");
const response = await getDegradation(
  dataset,
  engineId
);

console.log("DEGRADATION API RESPONSE:", response);

// Backend returns an object containing the timeline array
let timelineData = [];

if (Array.isArray(response)) {
  timelineData = response;
} else if (Array.isArray(response?.data)) {
  timelineData = response.data;
} else if (Array.isArray(response?.history)) {
  timelineData = response.history;
} else if (Array.isArray(response?.degradation)) {
  timelineData = response.degradation;
} else {
  // Find the first array inside the response object
  const arrayValue = Object.values(response || {}).find(
    (value) => Array.isArray(value)
  );

  if (arrayValue) {
    timelineData = arrayValue;
  }
}

console.log("TIMELINE DATA:", timelineData);

setData(timelineData);
       
      } catch (err) {
        console.error("Failed to load degradation data:", err);
        setError("Unable to load degradation data.");
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    loadDegradation();
  }, [dataset, engineId]);

  const firstPoint = data.length > 0 ? data[0] : null;
  const latestPoint =
    data.length > 0 ? data[data.length - 1] : null;

  const startCycle = firstPoint?.cycle ?? "--";
  const currentCycle = latestPoint?.cycle ?? "--";
  const estimatedRul =
    latestPoint?.estimated_rul != null
      ? Number(latestPoint.estimated_rul).toFixed(2)
      : "--";

  const healthScore =
    latestPoint?.health_score != null
      ? Number(latestPoint.health_score).toFixed(2)
      : "--";

  const degradationStatus =
    latestPoint?.degradation_status ||
    latestPoint?.status ||
    "UNKNOWN";

  const chartData = data.map((item) => ({
    cycle: Number(item.cycle),
    health_score: Number(item.health_score),
    estimated_rul: Number(item.estimated_rul),
    anomaly_score: Number(item.anomaly_score),
  }));

  return (
    <div className="degradation-page">

      {/* TOP BAR */}
      <header className="degradation-header">

        <button
          className="back-button"
          onClick={() => navigate("/command-center")}
        >
          <ArrowLeft size={18} />
          COMMAND CENTER
        </button>

        <div className="degradation-title">
          <span>AEROGUARD / DEGRADATION INTELLIGENCE</span>

          <h2>
            Engine {engineId}
            <small> / {dataset}</small>
          </h2>
        </div>

        <div className="live-status">
          <span></span>
          LIVE ANALYTICS
        </div>

      </header>

      <main className="degradation-content">

        {/* HERO */}
        <section className="degradation-hero">

          <div>
            <p className="section-eyebrow">
              ENGINE HEALTH TIMELINE
            </p>

            <h1>
              Degradation
              <br />
              <span>over operating</span>
              <br />
              cycles.
            </h1>
          </div>

          <p className="hero-description">
            AeroGuard tracks engine health, estimated remaining
            useful life and anomaly behavior across the complete
            operating cycle history.
          </p>

        </section>

        {/* STATS */}
        <section className="timeline-stats">

          <div className="timeline-stat">
            <span>START CYCLE</span>
            <strong>{startCycle}</strong>
          </div>

          <div className="timeline-stat">
            <span>CURRENT CYCLE</span>
            <strong>{currentCycle}</strong>
          </div>

          <div className="timeline-stat">
            <span>ESTIMATED RUL</span>
            <strong>
              {estimatedRul}
              {estimatedRul !== "--" && (
                <small> cycles</small>
              )}
            </strong>
          </div>

          <div className="timeline-stat">
            <span>HEALTH SCORE</span>
            <strong>
              {healthScore}
              {healthScore !== "--" && (
                <small> / 100</small>
              )}
            </strong>
          </div>

        </section>

        {/* LOADING */}
        {loading && (
          <div className="timeline-message">
            Loading degradation analytics...
          </div>
        )}

        {/* ERROR */}
        {!loading && error && (
          <div className="timeline-error">
            <AlertTriangle size={20} />
            {error}
          </div>
        )}

        {/* NO DATA */}
        {!loading && !error && chartData.length === 0 && (
          <div className="timeline-message">
            No degradation data available.
          </div>
        )}

        {/* HEALTH SCORE */}
        {!loading && chartData.length > 0 && (
          <section className="chart-card">

            <div className="chart-header">
              <div>
                <p>01 / HEALTH DEGRADATION</p>
                <h2>Engine Health Score</h2>
              </div>

              <span className="chart-label">
                <Activity size={16} />
                HEALTH SCORE
              </span>
            </div>

            <div className="chart-container">

              <ResponsiveContainer
                width="100%"
                height={420}
              >
                <LineChart data={chartData}>

                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis
                    dataKey="cycle"
                    label={{
                      value: "Operating Cycle",
                      position: "insideBottom",
                      offset: -5,
                    }}
                  />

                  <YAxis
                    domain={[0, 100]}
                    label={{
                      value: "Health Score",
                      angle: -90,
                      position: "insideLeft",
                    }}
                  />

                  <Tooltip />

                  <Line
                    type="monotone"
                    dataKey="health_score"
                    name="Health Score"
                    stroke="#1554a6"
                    strokeWidth={3}
                    dot={false}
                  />

                </LineChart>
              </ResponsiveContainer>

            </div>

          </section>
        )}

        {/* RUL */}
        {!loading && chartData.length > 0 && (
          <section className="chart-card">

            <div className="chart-header">
              <div>
                <p>02 / REMAINING USEFUL LIFE</p>
                <h2>Estimated RUL</h2>
              </div>

              <span className="chart-label">
                RUL / CYCLES
              </span>
            </div>

            <div className="chart-container">

              <ResponsiveContainer
                width="100%"
                height={420}
              >
                <LineChart data={chartData}>

                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis
                    dataKey="cycle"
                    label={{
                      value: "Operating Cycle",
                      position: "insideBottom",
                      offset: -5,
                    }}
                  />

                  <YAxis
                    label={{
                      value: "Estimated RUL",
                      angle: -90,
                      position: "insideLeft",
                    }}
                  />

                  <Tooltip />

                  <Line
                    type="monotone"
                    dataKey="estimated_rul"
                    name="Estimated RUL"
                    stroke="#1554a6"
                    strokeWidth={3}
                    dot={false}
                  />

                </LineChart>
              </ResponsiveContainer>

            </div>

          </section>
        )}

        {/* STATUS */}
        {!loading && latestPoint && (
          <section className="degradation-status">

            <div className="status-icon">
              <AlertTriangle size={24} />
            </div>

            <div>
              <p>CURRENT DEGRADATION STATUS</p>

              <h2>
                {degradationStatus}
              </h2>

              <span>
                Current engine condition is evaluated using
                health score, anomaly behavior and estimated
                remaining useful life.
              </span>
            </div>

          </section>
        )}

      </main>
    </div>
  );
}

export default DegradationTimeline;