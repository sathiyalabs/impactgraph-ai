import { useState } from "react";
import "./App.css";

function App() {
  const [repository, setRepository] = useState("data/real_repos/flask");
  const [commit, setCommit] = useState("2a8a38b0");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyzeCommit() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repository: repository.trim(),
          commit: commit.trim(),
        }),
      });

      const contentType = response.headers.get("content-type") || "";

      let data;

      if (contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        throw new Error(
          text || `Server returned HTTP ${response.status}.`
        );
      }

      if (!response.ok) {
        throw new Error(
          data?.error || "Prediction request failed."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to the backend."
      );
    } finally {
      setLoading(false);
    }
  }

  const probability = result
    ? result.risk_probability * 100
    : 0;

  const totalDirectImpact = result
    ? result.predictions.reduce(
        (sum, item) =>
          sum + (item.features?.direct_impacts || 0),
        0
      )
    : 0;

  const totalIndirectImpact = result
    ? result.predictions.reduce(
        (sum, item) =>
          sum + (item.features?.indirect_impacts || 0),
        0
      )
    : 0;

  const sortedPredictions = result
    ? [...result.predictions].sort(
        (a, b) => b.probability - a.probability
      )
    : [];

  const sortedFeatureImportance = result
    ? [...result.feature_importance].sort(
        (a, b) => b[1] - a[1]
      )
    : [];

  return (
    <div className="app">
      <header className="header">
        <div>
          <div className="brand">
            <span className="brand-mark">IG</span>
            <span>ImpactGraph AI</span>
          </div>

          <p className="subtitle">
            ML-powered software change risk analysis
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          API Ready
        </div>
      </header>

      <main className="container">
        {/* HERO */}
        <section className="hero">
          <p className="eyebrow">
            COMMIT RISK ANALYSIS
          </p>

          <h1>
            Understand the risk
            <br />
            <span>before the code ships.</span>
          </h1>

          <p className="hero-text">
            Analyze a Git commit using code-change metrics,
            dependency impact, and a trained Random Forest model.
          </p>
        </section>

        {/* ANALYSIS FORM */}
        <section className="analysis-card">
          <div className="card-heading">
            <div>
              <h2>Analyze a commit</h2>

              <p>
                Enter a local repository and commit SHA.
              </p>
            </div>
          </div>

          <div className="form-grid">
            <label>
              <span>Repository</span>

              <input
                value={repository}
                onChange={(event) =>
                  setRepository(event.target.value)
                }
                placeholder="data/real_repos/flask"
                disabled={loading}
              />
            </label>

            <label>
              <span>Commit</span>

              <input
                value={commit}
                onChange={(event) =>
                  setCommit(event.target.value)
                }
                placeholder="2a8a38b0"
                disabled={loading}
              />
            </label>
          </div>

          <button
            type="button"
            className="analyze-button"
            onClick={analyzeCommit}
            disabled={
              loading ||
              !repository.trim() ||
              !commit.trim()
            }
          >
            {loading
              ? "Analyzing..."
              : "Analyze Commit →"}
          </button>

          {error && (
            <div className="error-box">
              <strong>Analysis failed</strong>

              <span>{error}</span>
            </div>
          )}
        </section>

        {/* RESULTS */}
        {result && (
          <>
            {/* RESULT HEADER */}
            <section className="result-header">
              <div>
                <p className="eyebrow">
                  ANALYSIS RESULT
                </p>

                <h2>
                  Commit {result.commit.slice(0, 12)}
                </h2>
              </div>

              <div
                className={`risk-badge ${String(
                  result.risk_level
                ).toLowerCase()}`}
              >
                {result.risk_level} RISK
              </div>
            </section>

            {/* SUMMARY METRICS */}
            <section className="metrics-grid">
              <div className="metric-card">
                <span>Risk Probability</span>

                <strong>
                  {probability.toFixed(2)}%
                </strong>
              </div>

              <div className="metric-card">
                <span>Files Changed</span>

                <strong>
                  {result.changed_files.length}
                </strong>
              </div>

              <div className="metric-card">
                <span>Direct Impact</span>

                <strong>
                  {totalDirectImpact}
                </strong>
              </div>

              <div className="metric-card">
                <span>Indirect Impact</span>

                <strong>
                  {totalIndirectImpact}
                </strong>
              </div>
            </section>

            {/* FILE ANALYSIS */}
            <section className="panel">
              <div className="panel-title">
                <div>
                  <p className="eyebrow">
                    FILE ANALYSIS
                  </p>

                  <h2>
                    File-level predictions
                  </h2>
                </div>
              </div>

              <div className="file-list">
                {sortedPredictions.map(
                  (prediction) => {
                    const fileRisk =
                      prediction.probability * 100;

                    const features =
                      prediction.features || {};

                    return (
                      <div
                        className="file-row"
                        key={prediction.file}
                      >
                        <div className="file-main">
                          <div className="file-name">
                            {prediction.file}
                          </div>

                          <div className="file-details">
                            <span>
                              +{features.lines_added || 0} added
                            </span>

                            <span>
                              -{features.lines_deleted || 0} deleted
                            </span>

                            <span>
                              {features.direct_impacts || 0} direct
                            </span>

                            <span>
                              {features.indirect_impacts || 0} indirect
                            </span>
                          </div>
                        </div>

                        <div className="file-risk">
                          <div className="risk-number">
                            {fileRisk.toFixed(2)}%
                          </div>

                          <div className="risk-label">
                            predicted risk
                          </div>
                        </div>
                      </div>
                    );
                  }
                )}
              </div>
            </section>

            {/* MODEL EXPLANATION */}
            <section className="panel">
              <div className="panel-title">
                <div>
                  <p className="eyebrow">
                    MODEL EXPLANATION
                  </p>

                  <h2>
                    Feature importance
                  </h2>
                </div>
              </div>

              <div className="importance-list">
                {sortedFeatureImportance.map(
                  ([feature, importance]) => {
                    const percentage =
                      Number(importance) * 100;

                    return (
                      <div
                        className="importance-row"
                        key={feature}
                      >
                        <div className="importance-label">
                          <span>
                            {feature}
                          </span>

                          <strong>
                            {percentage.toFixed(2)}%
                          </strong>
                        </div>

                        <div className="bar">
                          <div
                            className="bar-fill"
                            style={{
                              width: `${Math.min(
                                percentage,
                                100
                              )}%`,
                            }}
                          />
                        </div>
                      </div>
                    );
                  }
                )}
              </div>
            </section>
          </>
        )}

        {/* EMPTY STATE */}
        {!result && !loading && !error && (
          <section className="empty-state">
            <div className="empty-icon">
              ◈
            </div>

            <h2>
              Ready to analyze
            </h2>

            <p>
              Enter a repository and commit above
              to generate a risk assessment.
            </p>
          </section>
        )}
      </main>

      <footer>
        <span>
          ImpactGraph AI
        </span>

        <span>
          Dependency-aware ML risk prediction
        </span>
      </footer>
    </div>
  );
}

export default App;