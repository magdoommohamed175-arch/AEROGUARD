import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowLeft,
  RefreshCw,
  Radio,
  Search,
} from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getTelemetry } from "../services/api";
import "./TelemetryExplorer.css";

function TelemetryExplorer() {
  const [dataset, setDataset] = useState("FD001");
  const [engineId, setEngineId] = useState("34");

  const [telemetry, setTelemetry] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [selectedSensors, setSelectedSensors] = useState([
    "sensor_4",
    "sensor_11",
    "sensor_13",
    "sensor_14",
  ]);

  const loadTelemetry = async () => {
    try {
      setLoading(true);
      setError("");
const data = await getTelemetry(
  dataset,
  engineId
);

const rows = Array.isArray(data)
  ? data
  : data.telemetry || data.data || data.rows || [];

setTelemetry(rows);
      
    } catch (err) {
      console.error(err);

      setError(
        "Unable to load telemetry data from AeroGuard backend."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTelemetry();
  }, []);

  const sensorNames = useMemo(() => {
    if (!telemetry.length) return [];

    return Object.keys(telemetry[0]).filter((key) =>
      key.startsWith("sensor_")
    );
  }, [telemetry]);

  const latest = telemetry[telemetry.length - 1];

  const toggleSensor = (sensor) => {
    setSelectedSensors((current) => {
      if (current.includes(sensor)) {
        return current.filter(
          (item) => item !== sensor
        );
      }

      if (current.length >= 4) {
        return current;
      }

      return [...current, sensor];
    });
  };

  return (
    <div className="telemetry-page">

      {/* SIDEBAR */}

      <aside className="telemetry-sidebar">

        <div className="telemetry-logo">
          <span>✦</span>
          AEROGUARD
        </div>

        <div className="telemetry-sidebar-title">
          COMMAND CENTER
        </div>

        <nav>

          <button
            onClick={() =>
              (window.location.href =
                "/command-center")
            }
          >
            <ArrowLeft size={17} />
            Overview
          </button>

          <button>
            <Activity size={17} />
            Engines
          </button>

          <button>
            <Radio size={17} />
            Engine Intelligence
          </button>

          <button className="active">
            <Radio size={17} />
            Telemetry
          </button>

          <button>
            <Activity size={17} />
            Timeline
          </button>

          <button>
            <Radio size={17} />
            Live Telemetry
          </button>

          <button>
            <Activity size={17} />
            Fault Investigation
          </button>

          <button>
            <Activity size={17} />
            Comparison
          </button>

        </nav>

      </aside>

      {/* MAIN */}

      <main className="telemetry-main">

        <header className="telemetry-header">

          <div>

            <p className="telemetry-eyebrow">
              AEROGUARD / TELEMETRY EXPLORER
            </p>

            <h1>
              Engine Telemetry
            </h1>

            <p>
              Explore aircraft engine sensor behaviour
              across operating cycles.
            </p>

          </div>

          <div className="telemetry-status">
            <span></span>
            BACKEND CONNECTED
          </div>

        </header>

        {/* CONTROLS */}

        <section className="telemetry-controls">

          <div className="control-group">

            <label>
              DATASET
            </label>

            <select
              value={dataset}
              onChange={(e) =>
                setDataset(e.target.value)
              }
            >
              <option value="FD001">FD001</option>
              <option value="FD002">FD002</option>
              <option value="FD003">FD003</option>
              <option value="FD004">FD004</option>
            </select>

          </div>

          <div className="control-group">

            <label>
              ENGINE
            </label>

            <input
              type="number"
              value={engineId}
              onChange={(e) =>
                setEngineId(e.target.value)
              }
            />

          </div>

          <button
            className="load-button"
            onClick={loadTelemetry}
            disabled={loading}
          >
            <RefreshCw size={16} />

            {loading
              ? "LOADING..."
              : "LOAD TELEMETRY"}
          </button>

        </section>

        {error && (
          <div className="telemetry-error">
            {error}
          </div>
        )}

        {/* SUMMARY */}

        <section className="telemetry-summary">

          <div>
            <span>DATASET</span>
            <strong>{dataset}</strong>
          </div>

          <div>
            <span>ENGINE</span>
            <strong>{engineId}</strong>
          </div>

          <div>
            <span>CYCLES</span>
            <strong>{telemetry.length}</strong>
          </div>

          <div>
            <span>LATEST CYCLE</span>
            <strong>
              {latest?.cycle ?? "--"}
            </strong>
          </div>

        </section>

        {/* MAIN CHART */}

        <section className="telemetry-card">

          <div className="telemetry-card-header">

            <div>
              <p>SENSOR TELEMETRY</p>

              <h2>
                Engine Sensor Trends
              </h2>
            </div>

            <div className="chart-info">
              <Search size={16} />
              {selectedSensors.length} sensors
            </div>

          </div>

          <div className="main-chart">

            {loading ? (
              <div className="chart-loading">
                Loading telemetry...
              </div>
            ) : (
              <ResponsiveContainer
                width="100%"
                height={420}
              >
                <LineChart data={telemetry}>

                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    dataKey="cycle"
                    fontSize={11}
                  />

                  <YAxis
                    fontSize={11}
                  />

                  <Tooltip />

                  {selectedSensors.map(
                    (sensor, index) => (
                      <Line
                        key={sensor}
                        type="monotone"
                        dataKey={sensor}
                        stroke={
                          [
                            "#0b3a82",
                            "#2f6fb3",
                            "#5c8fc5",
                            "#8aadd3",
                          ][index]
                        }
                        strokeWidth={2}
                        dot={false}
                      />
                    )
                  )}

                </LineChart>
              </ResponsiveContainer>
            )}

          </div>

        </section>

        {/* CURRENT SENSOR VALUES */}

        <section className="sensor-grid">

          {selectedSensors.map((sensor) => (

            <div
              className="sensor-card"
              key={sensor}
            >

              <div className="sensor-card-top">

                <span>
                  {sensor.replace("_", " ").toUpperCase()}
                </span>

                <Activity size={16} />

              </div>

              <strong>
                {latest?.[sensor] !== undefined
                  ? Number(
                      latest[sensor]
                    ).toFixed(2)
                  : "--"}
              </strong>

              <small>
                Latest reading · Cycle{" "}
                {latest?.cycle ?? "--"}
              </small>

            </div>

          ))}

        </section>

        {/* SENSOR SELECTOR */}

        <section className="telemetry-card">

          <div className="telemetry-card-header">

            <div>
              <p>SENSOR ANALYSIS</p>

              <h2>
                Select Sensors
              </h2>
            </div>

            <span className="sensor-limit">
              MAX 4
            </span>

          </div>

          <div className="sensor-selector">

            {sensorNames.map((sensor) => (

              <button
                key={sensor}
                className={
                  selectedSensors.includes(sensor)
                    ? "selected"
                    : ""
                }
                onClick={() =>
                  toggleSensor(sensor)
                }
              >
                <span></span>

                {sensor.replace("_", " ")}
              </button>

            ))}

          </div>

        </section>

      </main>

    </div>
  );
}

export default TelemetryExplorer;