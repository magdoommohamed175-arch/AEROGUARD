import { useEffect, useState } from "react";
import {
  ArrowLeft,
  Activity,
  Radio,
  Cpu,
  Gauge,
  Zap,
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
import { getLiveTelemetry } from "../services/api";
import "./LiveTelemetry.css";

function LiveTelemetry() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const dataset = searchParams.get("dataset") || "FD001";
  const engineId = searchParams.get("engine") || "34";

  const [telemetry, setTelemetry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadTelemetry = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await getLiveTelemetry(
          dataset,
          engineId
        );

        setTelemetry(response);
      } catch (err) {
        console.error("Failed to load live telemetry:", err);
        setError("Unable to load live telemetry.");
      } finally {
        setLoading(false);
      }
    };

    loadTelemetry();
  }, [dataset, engineId]);

  if (loading) {
    return (
      <div className="telemetry-loading">
        LOADING LIVE TELEMETRY...
      </div>
    );
  }

  if (error) {
    return (
      <div className="telemetry-error">
        {error}
      </div>
    );
  }

  if (!telemetry?.current) {
    return (
      <div className="telemetry-error">
        No telemetry data available.
      </div>
    );
  }

  const current = telemetry.current;
  const next = telemetry.simulated_next_cycle;

  const sensorData = Array.from(
    { length: 21 },
    (_, index) => {
      const sensorNumber = index + 1;
      const key = `sensor_${sensorNumber}`;

      return {
        sensor: `S${sensorNumber}`,
        current: Number(current[key]),
        next: Number(next?.[key] ?? current[key]),
      };
    }
  );

  const settings = [
    {
      label: "SETTING 01",
      value: current.setting_1,
    },
    {
      label: "SETTING 02",
      value: current.setting_2,
    },
    {
      label: "SETTING 03",
      value: current.setting_3,
    },
  ];

  return (
    <div className="telemetry-page">

      {/* HEADER */}

      <header className="telemetry-header">

        <button
          className="telemetry-back"
          onClick={() => {
            window.location.href = "/command-center";
          }}
        >
          <ArrowLeft size={17} />
          COMMAND CENTER
        </button>

        <div className="telemetry-title">
          <span>AEROGUARD / LIVE TELEMETRY</span>

          <h2>
            Engine {engineId}
            <small> / {dataset}</small>
          </h2>
        </div>

        <div className="telemetry-live">
          <span></span>
          LIVE STREAM
        </div>

      </header>

      <main className="telemetry-content">

        {/* HERO */}

        <section className="telemetry-hero">

          <div>
            <p className="telemetry-eyebrow">
              REAL-TIME ENGINE MONITORING
            </p>

            <h1>
              Live
              <br />
              <span>telemetry.</span>
            </h1>
          </div>

          <p className="telemetry-description">
            Monitor the latest engine sensor measurements and
            compare current operating conditions against the
            simulated next operating cycle.
          </p>

        </section>

        {/* METRICS */}

        <section className="telemetry-metrics">

          <MetricCard
            icon={<Radio size={18} />}
            label="CURRENT CYCLE"
            value={current.cycle}
          />

          <MetricCard
            icon={<Activity size={18} />}
            label="SENSOR CHANNELS"
            value="21"
          />

          <MetricCard
            icon={<Cpu size={18} />}
            label="NEXT SIMULATION"
            value={next?.cycle ?? "--"}
          />

          <MetricCard
            icon={<Gauge size={18} />}
            label="ENGINE STATUS"
            value="MONITORING"
          />

        </section>

        {/* SENSOR CHART */}

        <section className="telemetry-panel">

          <div className="telemetry-panel-header">

            <div>
              <p>01 / SENSOR STREAM</p>
              <h2>Engine Sensor Telemetry</h2>
            </div>

            <div className="telemetry-legend">
              <span className="legend-current"></span>
              CURRENT
              <span className="legend-next"></span>
              NEXT CYCLE
            </div>

          </div>

          <div className="telemetry-chart">

            <ResponsiveContainer
              width="100%"
              height={440}
            >
              <LineChart data={sensorData}>

                <CartesianGrid strokeDasharray="3 3" />

                <XAxis
                  dataKey="sensor"
                />

                <YAxis />

                <Tooltip />

                <Line
                  type="monotone"
                  dataKey="current"
                  name="Current"
                  stroke="#0b3a82"
                  strokeWidth={3}
                  dot={false}
                />

                <Line
                  type="monotone"
                  dataKey="next"
                  name="Next Cycle"
                  stroke="#7aa7d9"
                  strokeWidth={2}
                  strokeDasharray="6 5"
                  dot={false}
                />

              </LineChart>
            </ResponsiveContainer>

          </div>

        </section>

        {/* SENSOR GRID */}

        <section className="sensor-section">

          <div className="telemetry-panel-header">
            <div>
              <p>02 / SENSOR CHANNELS</p>
              <h2>Current Sensor Readings</h2>
            </div>
          </div>

          <div className="sensor-grid">

            {sensorData.map((sensor) => (
              <div
                className="sensor-card"
                key={sensor.sensor}
              >
                <span>{sensor.sensor}</span>

                <strong>
                  {sensor.current.toFixed(4)}
                </strong>

                <small>
                  NEXT&nbsp;&nbsp;
                  {sensor.next.toFixed(4)}
                </small>

              </div>
            ))}

          </div>

        </section>

        {/* SETTINGS */}

        <section className="settings-panel">

          <div className="telemetry-panel-header">

            <div>
              <p>03 / OPERATING CONDITIONS</p>
              <h2>Engine Settings</h2>
            </div>

            <Zap size={19} />

          </div>

          <div className="settings-grid">

            {settings.map((setting) => (
              <div
                className="setting-card"
                key={setting.label}
              >
                <span>{setting.label}</span>

                <strong>
                  {Number(setting.value).toFixed(4)}
                </strong>
              </div>
            ))}

          </div>

        </section>

        {/* NEXT CYCLE */}

        <section className="next-cycle-panel">

          <div>
            <p>NEXT CYCLE SIMULATION</p>

            <h2>
              Cycle {next?.cycle}
            </h2>

            <span>
              AeroGuard simulation estimates the next
              telemetry state from the current engine condition.
            </span>
          </div>

          <div className="next-cycle-badge">
            <span></span>
            PREDICTED
          </div>

        </section>

      </main>

    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
}) {
  return (
    <div className="telemetry-metric">

      <div className="metric-icon">
        {icon}
      </div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>

    </div>
  );
}

export default LiveTelemetry;