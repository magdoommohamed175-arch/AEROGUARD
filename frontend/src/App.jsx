import "./App.css";
import heroVideo from "./assets/videos/aeroguard-hero.mp4";

import {
  BrowserRouter,
  Routes,
  Route,
  useNavigate,
} from "react-router-dom";

import Login from "./pages/Login";
import FleetOverview from "./pages/FleetOverview";
import EngineIntelligence from "./pages/EngineIntelligence";
import TelemetryExplorer from "./pages/TelemetryExplorer";
import DegradationTimeline from "./pages/DegradationTimeline";
import LiveTelemetry from "./pages/LiveTelemetry";
import FaultInvestigation from "./pages/FaultInvestigation";
import Comparison from "./pages/Comparison";

/* =========================================================
   MAIN APP / ROUTER
========================================================= */

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* LANDING PAGE */}
        <Route path="/" element={<Landing />} />

        {/* LOGIN */}
        <Route path="/login" element={<Login />} />

        {/* COMMAND CENTER / FLEET OVERVIEW */}
        <Route
          path="/command-center"
          element={<FleetOverview />}
        />

        {/* ENGINE INTELLIGENCE */}
        <Route
          path="/engine-intelligence"
          element={<EngineIntelligence />}
        />
        <Route
  path="/telemetry"
  element={<TelemetryExplorer />}
/>
<Route
  path="/timeline"
  element={<DegradationTimeline />}
/>
<Route
  path="/live-telemetry"
  element={<LiveTelemetry />}
/>
<Route
  path="/fault-investigation"
  element={<FaultInvestigation />}
/>
<Route
  path="/comparison"
  element={<Comparison />}
/>
      </Routes>
    </BrowserRouter>
  );
}

/* =========================================================
   LANDING PAGE
========================================================= */

function Landing() {
  const navigate = useNavigate();

  return (
    <div className="app">

      {/* =================================================
          NAVBAR
      ================================================= */}

      <header className="navbar">

        <div className="logo">
          <span className="logo-mark">✦</span>
          AEROGUARD
        </div>

        <nav>
          <a href="#platform">Platform</a>
          <a href="#technology">Technology</a>
          <a href="#solutions">Solutions</a>
          <a href="#safety">Safety</a>
          <a href="#about">About</a>
        </nav>

        {/* SIGN IN → LOGIN */}
        <button
          className="nav-button"
          onClick={() => navigate("/login")}
        >
          SIGN IN
        </button>

      </header>

      <main>

        {/* =================================================
            FULL SCREEN VIDEO HERO
        ================================================= */}

        <section className="hero hero-video-section">

          <video
            className="hero-background-video"
            src={heroVideo}
            autoPlay
            muted
            loop
            playsInline
          />

          <div className="hero-video-overlay"></div>

          <div className="hero-grid-lines"></div>

          <div className="hero-content">

            <div className="hero-system-status">
              <span></span>
              AEROGUARD INTELLIGENCE SYSTEM
            </div>

            <p className="eyebrow">
              AEROSPACE ENGINE INTELLIGENCE
            </p>

            <h1>
              Predict the future
              <br />
              of <span>engine health.</span>
            </h1>

            <p className="hero-description">
              AeroGuard transforms aircraft telemetry into predictive
              maintenance intelligence — helping teams predict degradation,
              detect anomalies, explain AI decisions and prioritize action.
            </p>

            <div className="hero-actions">

              {/* EXPLORE PLATFORM */}
              <button
                className="primary-button"
                onClick={() =>
                  document
                    .getElementById("platform")
                    ?.scrollIntoView({
                      behavior: "smooth",
                    })
                }
              >
                EXPLORE PLATFORM
                <span>→</span>
              </button>

              {/* COMMAND CENTER → LOGIN */}
              <button
                className="secondary-button"
                onClick={() => navigate("/login")}
              >
                COMMAND CENTER
              </button>

            </div>

            <div className="hero-scroll">
              <span></span>
              SCROLL TO EXPLORE
            </div>

          </div>
        </section>

        {/* =================================================
            TRUST STRIP
        ================================================= */}

        <section className="trust-strip">
          <span>AI-POWERED CONDITION MONITORING</span>
          <span>•</span>
          <span>PREDICTIVE MAINTENANCE</span>
          <span>•</span>
          <span>EXPLAINABLE AI</span>
          <span>•</span>
          <span>FLEET INTELLIGENCE</span>
        </section>

        {/* =================================================
            PROBLEM
        ================================================= */}

        <section className="section problem-section">

          <div className="section-label">
            01 / THE CHALLENGE
          </div>

          <div className="two-column">

            <h2>
              Aircraft generate
              <br />
              <span>millions of signals.</span>
            </h2>

            <div>

              <p className="large-text">
                The challenge isn't collecting telemetry. It's turning
                telemetry into decisions before degradation becomes an
                operational problem.
              </p>

              <div className="process-line">
                <span>TELEMETRY</span>
                <b>→</b>
                <span>INTELLIGENCE</span>
                <b>→</b>
                <span>ACTION</span>
              </div>

            </div>

          </div>
        </section>

        {/* =================================================
            PLATFORM
        ================================================= */}

        <section
          className="section platform-section"
          id="platform"
        >

          <div className="section-label">
            02 / PLATFORM
          </div>

          <div className="section-heading">

            <h2>
              From raw telemetry
              <br />
              to <span>maintenance intelligence.</span>
            </h2>

            <p>
              One platform connecting prediction, detection,
              explanation and maintenance prioritization.
            </p>

          </div>

          <div className="feature-grid">

            <Feature
              number="01"
              title="Predict"
              description="Estimate Remaining Useful Life using XGBoost-based engine health prediction."
            />

            <Feature
              number="02"
              title="Detect"
              description="Identify abnormal engine behavior and sensor patterns."
            />

            <Feature
              number="03"
              title="Explain"
              description="Understand which features are influencing every AI prediction."
            />

            <Feature
              number="04"
              title="Act"
              description="Convert engine health intelligence into maintenance priorities."
            />

          </div>

        </section>

        {/* =================================================
            WORKFLOW
        ================================================= */}

        <section className="section workflow-section">

          <div className="section-label">
            03 / HOW IT WORKS
          </div>

          <div className="workflow">

            <WorkflowStep
              number="01"
              title="Telemetry"
            />

            <div className="arrow">→</div>

            <WorkflowStep
              number="02"
              title="Feature Engineering"
            />

            <div className="arrow">→</div>

            <WorkflowStep
              number="03"
              title="AI Analytics"
            />

            <div className="arrow">→</div>

            <WorkflowStep
              number="04"
              title="Risk Assessment"
            />

            <div className="arrow">→</div>

            <WorkflowStep
              number="05"
              title="Maintenance Action"
            />

          </div>

        </section>

        {/* =================================================
            CAPABILITIES
        ================================================= */}

        <section
          className="section capabilities-section"
          id="solutions"
        >

          <div className="section-label">
            04 / CAPABILITIES
          </div>

          <div className="section-heading">

            <h2>
              One intelligence layer.
              <br />
              <span>Ten operational capabilities.</span>
            </h2>

          </div>

          <div className="capability-grid">

            {[
              ["01", "Fleet Health Intelligence"],
              ["02", "RUL Prediction"],
              ["03", "Anomaly Detection"],
              ["04", "Explainable AI"],
              ["05", "Maintenance Priority"],
              ["06", "Telemetry Explorer"],
              ["07", "Degradation Timeline"],
              ["08", "Live Telemetry Simulation"],
              ["09", "Fault Investigation"],
              ["10", "Engine Comparison"],
            ].map(([number, title]) => (

              <div
                className="capability"
                key={number}
              >
                <span>{number}</span>

                <strong>{title}</strong>

                <b>↗</b>
              </div>

            ))}

          </div>

        </section>

        {/* =================================================
            TECHNOLOGY
        ================================================= */}

        <section
          className="section technology-section"
          id="technology"
        >

          <div className="section-label">
            05 / TECHNOLOGY
          </div>

          <div className="technology-layout">

            <div>

              <h2>
                Engineering-grade
                <br />
                <span>AI infrastructure.</span>
              </h2>

              <p>
                AeroGuard combines machine learning, anomaly
                detection and explainability into a unified
                predictive maintenance architecture.
              </p>

            </div>

            <div className="tech-stack">

              {[
                "XGBoost",
                "Isolation Forest",
                "SHAP",
                "Python",
                "Pandas",
                "NumPy",
                "FastAPI",
                "React",
              ].map((tech) => (

                <div key={tech}>
                  {tech}
                </div>

              ))}

            </div>

          </div>

        </section>

        {/* =================================================
            SAFETY
        ================================================= */}

        <section
          className="section safety-section"
          id="safety"
        >

          <div className="section-label">
            06 / SAFETY & RELIABILITY
          </div>

          <div className="safety-box">

            <div>
              <span className="status-dot"></span>
              DECISION SUPPORT SYSTEM
            </div>

            <h2>
              AI that assists
              <br />
              <span>
                engineers — not replaces them.
              </span>
            </h2>

            <p>
              AeroGuard provides predictive maintenance
              intelligence while keeping qualified maintenance
              personnel in control of operational decisions.
            </p>

          </div>

        </section>

        {/* =================================================
            CTA
        ================================================= */}

        <section className="cta-section">

          <p className="eyebrow">
            AEROGUARD COMMAND CENTER
          </p>

          <h2>
            Turn engine data
            <br />
            into <span>action.</span>
          </h2>

          <button
            className="primary-button"
            onClick={() => navigate("/login")}
          >
            ENTER COMMAND CENTER
            <span>→</span>
          </button>

        </section>

      </main>

      {/* =================================================
          FOOTER
      ================================================= */}

      <footer id="about">

        <div className="footer-logo">
          AEROGUARD
        </div>

        <p>
          AI-powered aircraft engine health intelligence.
        </p>

        <div className="footer-bottom">

          <span>
            © 2026 AeroGuard
          </span>

          <span>
            Predict • Detect • Explain • Act
          </span>

        </div>

      </footer>

    </div>
  );
}

/* =========================================================
   FEATURE COMPONENT
========================================================= */

function Feature({
  number,
  title,
  description,
}) {
  return (
    <div className="feature-card">

      <span>{number}</span>

      <h3>{title}</h3>

      <p>{description}</p>

      <div className="feature-arrow">
        ↗
      </div>

    </div>
  );
}

/* =========================================================
   WORKFLOW COMPONENT
========================================================= */

function WorkflowStep({
  number,
  title,
}) {
  return (
    <div className="workflow-step">

      <span>{number}</span>

      <strong>{title}</strong>

    </div>
  );
}

export default App;