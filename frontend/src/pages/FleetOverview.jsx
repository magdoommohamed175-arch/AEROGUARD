import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  AlertTriangle,
  BarChart3,
  Bell,
  BrainCircuit,
  ChevronRight,
  Clock3,
  Gauge,
  LayoutDashboard,
  Radio,
  Search,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Activity,
} from "lucide-react";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

import {
  getFleetSummary,
  getFleetTopPriority,
} from "../services/api";

import "./FleetOverview.css";

function FleetOverview() {
  const navigate = useNavigate();

  const [summary, setSummary] = useState(null);
  const [priorityData, setPriorityData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadFleetData();
  }, []);

  const loadFleetData = async () => {
    try {
      setLoading(true);
      setError("");

      const [summaryResponse, priorityResponse] =
        await Promise.all([
          getFleetSummary(),
          getFleetTopPriority(),
        ]);

      setSummary(summaryResponse);
      setPriorityData(priorityResponse.engines || []);
    } catch (err) {
      console.error("Fleet data error:", err);

      setError(
        "Unable to connect to the AeroGuard backend."
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>

        <p>
          CONNECTING TO AEROGUARD INTELLIGENCE...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <AlertTriangle size={30} />

        <h2>Backend Connection Failed</h2>

        <p>{error}</p>

        <button onClick={loadFleetData}>
          RETRY CONNECTION
        </button>
      </div>
    );
  }

  const riskData = [
    {
      name: "Low",
      value: summary.risk_distribution.LOW,
      className: "risk-low",
    },
    {
      name: "Medium",
      value: summary.risk_distribution.MEDIUM,
      className: "risk-medium",
    },
    {
      name: "High",
      value: summary.risk_distribution.HIGH,
      className: "risk-high",
    },
    {
      name: "Critical",
      value: summary.risk_distribution.CRITICAL,
      className: "risk-critical",
    },
  ];

  return (
    <div className="dashboard">

      {/* SIDEBAR */}

      <aside className="dashboard-sidebar">

        <div className="dashboard-logo">
          <span>✦</span>
          AEROGUARD
        </div>

        <div className="sidebar-section-title">
          COMMAND CENTER
        </div>

        <nav className="sidebar-nav">

          <SidebarItem
            icon={<LayoutDashboard size={18} />}
            label="Overview"
            active
          />

          
          {/* ENGINE INTELLIGENCE */}

<SidebarItem
  icon={<BrainCircuit size={18} />}
  label="Engine Intelligence"
  onClick={() => {
    window.location.href = "/engine-intelligence";
  }}
/>

<SidebarItem
  icon={<Radio size={18} />}
  label="Telemetry"
  onClick={() => {
    window.location.href = "/telemetry";
  }}
/>

<SidebarItem
  icon={<Clock3 size={18} />}
  label="Timeline"
  onClick={() => {
    window.location.href = "/timeline";
  }}
/>

<SidebarItem
  icon={<Activity size={18} />}
  label="Live Telemetry"
  onClick={() => {
    window.location.href = "/live-telemetry";
  }}
/>

<SidebarItem
  icon={<AlertTriangle size={18} />}
  label="Fault Investigation"
  onClick={() => {
    window.location.href =
      "/fault-investigation?dataset=FD001&engine=34";
  }}
/>

<SidebarItem
  icon={<BarChart3 size={18} />}
  label="Comparison"
  onClick={() => {
    window.location.href =
      "/comparison?dataset=FD001&engine1=34&engine2=35";
  }}
/>

        </nav>

        <div className="sidebar-bottom">

          <SidebarItem
            icon={<Settings size={18} />}
            label="Settings"
          />

          <div className="system-status">

            <span></span>

            <div>
              <strong>System Online</strong>
              <small>FastAPI connected</small>
            </div>

          </div>

        </div>

      </aside>

      {/* MAIN AREA */}

      <main className="dashboard-main">

        {/* TOP BAR */}

        <header className="dashboard-topbar">

          <div className="breadcrumb">
            AEROGUARD
            <ChevronRight size={14} />
            <strong>FLEET OVERVIEW</strong>
          </div>

          <div className="topbar-actions">

            <button className="icon-button">
              <Search size={18} />
            </button>

            <button className="icon-button notification">
              <Bell size={18} />
              <span></span>
            </button>

            <div className="user-profile">

              <div className="avatar">
                RK
              </div>

              <div>
                <strong>Engineer</strong>
                <small>Operations</small>
              </div>

            </div>

          </div>

        </header>

        {/* CONTENT */}

        <div className="dashboard-content">

          <div className="page-heading">

            <div>

              <p className="dashboard-eyebrow">
                COMMAND CENTER / FLEET INTELLIGENCE
              </p>

              <h1>
                Fleet Overview
              </h1>

              <p>
                Real-time predictive maintenance intelligence
                across the AeroGuard engine fleet.
              </p>

            </div>

            <button
              className="refresh-button"
              onClick={loadFleetData}
            >
              <Activity size={16} />
              REFRESH DATA
            </button>

          </div>

          {/* STAT CARDS */}

          <div className="stat-grid">

            <StatCard
              icon={<Gauge size={20} />}
              label="TOTAL ENGINES"
              value={summary.total_engines}
              suffix=""
              description="Engines monitored"
            />

            <StatCard
              icon={<Clock3 size={20} />}
              label="AVERAGE PREDICTED RUL"
              value={summary.average_predicted_rul}
              suffix=" cycles"
              description="Remaining useful life"
            />

            <StatCard
              icon={<ShieldCheck size={20} />}
              label="AVERAGE HEALTH"
              value={summary.average_health_score}
              suffix=" / 100"
              description="Fleet health score"
            />

            <StatCard
              icon={<AlertTriangle size={20} />}
              label="AVERAGE ANOMALY"
              value={summary.average_anomaly_score}
              suffix=" / 100"
              description="Anomaly score"
            />

          </div>

          {/* ANALYTICS */}

          <div className="analytics-grid">

            {/* RISK DISTRIBUTION */}

            <section className="dashboard-card">

              <div className="card-header">

                <div>
                  <p>FLEET RISK</p>
                  <h2>Risk Distribution</h2>
                </div>

                <SlidersHorizontal size={18} />

              </div>

              <div className="risk-chart">

                <ResponsiveContainer
                  width="100%"
                  height={280}
                >

                  <PieChart>

                    <Pie
                      data={riskData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={72}
                      outerRadius={105}
                      paddingAngle={3}
                    >

                      {riskData.map((item) => (
                        <Cell
                          key={item.name}
                          className={item.className}
                        />
                      ))}

                    </Pie>

                    <Tooltip />

                  </PieChart>

                </ResponsiveContainer>

                <div className="risk-center">

                  <strong>
                    {summary.total_engines}
                  </strong>

                  <span>
                    ENGINES
                  </span>

                </div>

              </div>

              <div className="risk-legend">

                {riskData.map((item) => (

                  <div
                    className="risk-legend-item"
                    key={item.name}
                  >

                    <span
                      className={`legend-dot ${item.className}`}
                    ></span>

                    <span>
                      {item.name}
                    </span>

                    <strong>
                      {item.value}
                    </strong>

                  </div>

                ))}

              </div>

            </section>

            {/* MAINTENANCE DISTRIBUTION */}

            <section className="dashboard-card">

              <div className="card-header">

                <div>
                  <p>MAINTENANCE STATUS</p>
                  <h2>Maintenance Distribution</h2>
                </div>

                <ShieldCheck size={18} />

              </div>

              <div className="maintenance-chart">

                <ResponsiveContainer
                  width="100%"
                  height={330}
                >

                  <BarChart
                    data={[
                      {
                        name: "Monitor",
                        value:
                          summary
                            .maintenance_distribution[
                            "CONTINUE MONITORING"
                          ],
                      },

                      {
                        name: "Close",
                        value:
                          summary
                            .maintenance_distribution[
                            "MONITOR CLOSELY"
                          ],
                      },

                      {
                        name: "Schedule",
                        value:
                          summary
                            .maintenance_distribution[
                            "SCHEDULE MAINTENANCE"
                          ],
                      },

                      {
                        name: "Immediate",
                        value:
                          summary
                            .maintenance_distribution[
                            "IMMEDIATE INSPECTION"
                          ],
                      },
                    ]}
                    margin={{
                      top: 20,
                      right: 10,
                      left: -15,
                      bottom: 0,
                    }}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="name"
                      fontSize={11}
                    />

                    <YAxis fontSize={11} />

                    <Tooltip />

                    <Bar
                      dataKey="value"
                      fill="#0b3a82"
                      radius={[
                        4,
                        4,
                        0,
                        0,
                      ]}
                    />

                  </BarChart>

                </ResponsiveContainer>

              </div>

            </section>

          </div>

          {/* PRIORITY ENGINES */}

          <section className="dashboard-card priority-card">

            <div className="card-header">

              <div>

                <p>
                  MAINTENANCE INTELLIGENCE
                </p>

                <h2>
                  Top Priority Engines
                </h2>

              </div>

              <div className="priority-count">
                {priorityData.length} PRIORITY ENGINES
              </div>

            </div>

            <div className="table-wrapper">

              <table className="priority-table">

                <thead>

                  <tr>
                    <th>ENGINE</th>
                    <th>DATASET</th>
                    <th>RUL</th>
                    <th>HEALTH</th>
                    <th>ANOMALY</th>
                    <th>RISK</th>
                    <th>PRIORITY</th>
                    <th>ACTION</th>
                  </tr>

                </thead>

                <tbody>

                  {priorityData.map((engine) => (

                    <tr
                      key={`${engine.dataset}-${engine.engine_id}`}
                    >

                      <td>

                        <strong>
                          Engine {engine.engine_id}
                        </strong>

                      </td>

                      <td>

                        <span className="dataset-badge">
                          {engine.dataset}
                        </span>

                      </td>

                      <td>

                        <strong>
                          {engine.predicted_rul}
                        </strong>

                        <small>
                          {" "}cycles
                        </small>

                      </td>

                      <td>
                        {engine.health_score}
                      </td>

                      <td>
                        {engine.anomaly_score}
                      </td>

                      <td>

                        <RiskBadge
                          risk={engine.risk}
                        />

                      </td>

                      <td>

                        <strong className="priority-score">
                          {engine.priority_score}
                        </strong>

                      </td>

                      <td>

                        <span className="maintenance-action">
                          {engine.maintenance_priority}
                        </span>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          </section>

        </div>

      </main>

    </div>
  );
}

/* =========================================================
   SIDEBAR ITEM
========================================================= */

function SidebarItem({
  icon,
  label,
  active = false,
  onClick,
}) {
  return (
    <button
      className={`sidebar-item ${
        active ? "active" : ""
      }`}
      onClick={onClick}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}
/* =========================================================
   STAT CARD
========================================================= */

function StatCard({
  icon,
  label,
  value,
  suffix,
  description,
}) {
  return (
    <div className="stat-card">

      <div className="stat-card-top">

        <div className="stat-icon">
          {icon}
        </div>

        <span>
          {label}
        </span>

      </div>

      <div className="stat-value">

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
   RISK BADGE
========================================================= */

function RiskBadge({ risk }) {
  return (
    <span
      className={`risk-badge risk-${risk.toLowerCase()}`}
    >
      {risk}
    </span>
  );
}

export default FleetOverview;