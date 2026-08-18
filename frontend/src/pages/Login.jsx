import { useState } from "react";
import { ArrowRight, LockKeyhole, Mail, ShieldCheck } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (event) => {
    event.preventDefault();

    // Frontend demo authentication for now.
    // Real authentication can be connected later.
    navigate("/command-center");
  };

  return (
    <div className="login-page">
      <div className="login-visual">
        <div className="login-overlay"></div>

        <div className="login-brand">
          <span>✦</span>
          AEROGUARD
        </div>

        <div className="login-visual-content">
          <p>AEROSPACE ENGINE INTELLIGENCE</p>

          <h1>
            Intelligence
            <br />
            for every
            <br />
            <span>flight.</span>
          </h1>

          <div className="login-system-status">
            <span></span>
            PREDICTIVE MAINTENANCE SYSTEM
          </div>
        </div>
      </div>

      <div className="login-panel">
        <div className="login-panel-inner">
          <div className="mobile-brand">
            <span>✦</span>
            AEROGUARD
          </div>

          <div className="login-heading">
            <p>COMMAND CENTER</p>

            <h2>Welcome back.</h2>

            <span>
              Sign in to your AeroGuard Command Center.
            </span>
          </div>

          <form onSubmit={handleLogin}>
            <label>
              WORK EMAIL
            </label>

            <div className="input-wrapper">
              <Mail size={17} />

              <input
                type="email"
                placeholder="name@aeroguard.com"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                required
              />
            </div>

            <label>
              PASSWORD
            </label>

            <div className="input-wrapper">
              <LockKeyhole size={17} />

              <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                required
              />
            </div>

            <div className="login-options">
              <label className="remember">
                <input type="checkbox" />
                Remember me
              </label>

              <button
                type="button"
                className="forgot-password"
              >
                Forgot password?
              </button>
            </div>

            <button
              type="submit"
              className="login-button"
            >
              SIGN IN

              <ArrowRight size={17} />
            </button>
          </form>

          <div className="security-note">
            <ShieldCheck size={17} />

            <span>
              Secure access to predictive maintenance
              intelligence.
            </span>
          </div>

          <div className="login-footer">
            AeroGuard • Predict • Detect • Explain • Act
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;