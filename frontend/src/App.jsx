import { useState } from "react";
import "./App.css";

const DEFAULT_REPOSITORY = "data/real_repos/flask";
const DEFAULT_COMMIT = "d8eaaba8";

function App() {
  const [repository, setRepository] = useState(DEFAULT_REPOSITORY);
  const [commit, setCommit] = useState(DEFAULT_COMMIT);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyzeCommit() {
    const trimmedRepository = repository.trim();
    const trimmedCommit = commit.trim();

    if (!trimmedRepository || !trimmedCommit) {
      setError("Repository and commit SHA are required.");
      return;
    }

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
          repository: trimmedRepository,
          commit: trimmedCommit,
        }),
      });

      const contentType =
        response.headers.get("content-type") || "";

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

  function handleSubmit(event) {
    event.preventDefault();
    analyzeCommit();
  }

  function handleReset() {
    setRepository(DEFAULT_REPOSITORY);
    setCommit(DEFAULT_COMMIT);
    setResult(null);
    setError("");
  }

  const probability = result
    ? Math.max(
        0,
        Math.min(100, result.risk_probability * 100)
      )
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

  const riskLevel = result?.risk_level || "";

  return (
    <div className="app">
      <header className="header">
        <div>
          <div className="brand">
            <span
              className="brand-mark"
              aria-hidden="true"
            >
              IG
            </span>

            <span>ImpactGraph AI</span>
          </div>

          <p className="subtitle">
            ML-powered software change risk analysis
          </p>
        </div>

        <div
          className="status"
          aria-label="API status"
        >
          <span
            className="status-dot"
            aria-hidden="true"
          />
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
            dependency impact, and a trained Random Forest
            model.
          </p>
        </section>

        {/* ANALYSIS FORM */}
        <section className="analysis-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">
                ANALYSIS INPUT
              </p>

              <h2>Analyze a commit</h2>

              <p>
                Enter a local repository and commit SHA.
              </p>
            </div>
          </div>

          <form
            onSubmit={handleSubmit}
            noValidate
          >
            <div className="form-grid">
              <label htmlFor="repository">
                <span>Repository</span>

                <input
                  id="repository"
                  value={repository}
                  onChange={(event) =>
                    setRepository(event.target.value)
                  }
                  placeholder={DEFAULT_REPOSITORY}
                  autoComplete="off"
                  spellCheck="false"
                  disabled={loading}
                />
              </label>

              <label htmlFor="commit">
                <span>Commit SHA</span>

                <input
                  id="commit"
                  value={commit}
                  onChange={(event) =>
                    setCommit(event.target.value)
                  }
                  placeholder={DEFAULT_COMMIT}
                  autoComplete="off"
                  spellCheck="false"
                  disabled={loading}
                />
              </label>
            </div>

            <div className="form-actions">
              <button
                type="submit"
                className="analyze-button"
                disabled={
                  loading ||
                  !repository.trim() ||
                  !commit.trim()
                }
              >
                {loading ? (
                  <>
                    <span
                      className="button-spinner"
                      aria-hidden="true"
                    />
                    Analyzing...
                  </>
                ) : (
                  "Analyze Commit →"
                )}
              </button>

              {(result || error) && !loading && (
                <button
                  type="button"
                  className="reset-button"
                  onClick={handleReset}
                >
                  Reset
                </button>
              )}
            </div>
          </form>

          {error && (
            <div
              className="error-box"
              role="alert"
            >
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
                  Commit{" "}
                  <code>
                    {result.commit.slice(0, 12)}
                  </code>
                </h2>

                <p className="result-meta">
                  Repository:{" "}
                  <span>{repository.trim()}</span>
                  {" · "}
                  Parent:{" "}
                  <span>
                    {result.old_commit?.slice(0, 12)}
                  </span>
                </p>
              </div>

              <div
                className={`risk-badge ${String(
                  riskLevel
                ).toLowerCase()}`}
              >
                {riskLevel} RISK
              </div>
            </section>

            {/* SUMMARY */}
            <section className="metrics-grid">
              <div className="metric-card">
                <span>Risk Probability</span>

                <strong>
                  {probability.toFixed(2)}%
                </strong>

                <div className="metric-progress">
                  <div
                    className="metric-progress-fill"
                    style={{
                      width: `${probability}%`,
                    }}
                  />
                </div>
              </div>

              <div className="metric-card">
                <span>Files Changed</span>

                <strong>
                  {result.changed_files.length}
                </strong>

                <small>
                  analyzed files
                </small>
              </div>

              <div className="metric-card">
                <span>Direct Impact</span>

                <strong>
                  {totalDirectImpact}
                </strong>

                <small>
                  direct dependents
                </small>
              </div>

              <div className="metric-card">
                <span>Indirect Impact</span>

                <strong>
                  {totalIndirectImpact}
                </strong>

                <small>
                  downstream dependents
                </small>
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

                <span className="panel-count">
                  {sortedPredictions.length} files
                </span>
              </div>

              <div className="file-list">
                {sortedPredictions.map(
                  (prediction) => {
                    const fileRisk = Math.max(
                      0,
                      Math.min(
                        100,
                        prediction.probability * 100
                      )
                    );

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
                              +
                              {features.lines_added ||
                                0}{" "}
                              added
                            </span>

                            <span>
                              -
                              {features.lines_deleted ||
                                0}{" "}
                              deleted
                            </span>

                            <span>
                              {features.direct_impacts ||
                                0}{" "}
                              direct
                            </span>

                            <span>
                              {features.indirect_impacts ||
                                0}{" "}
                              indirect
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

                  <p className="panel-description">
                    Relative contribution of each model
                    feature to the prediction.
                  </p>
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
            <div
              className="empty-icon"
              aria-hidden="true"
            >
              ◈
            </div>

            <h2>Ready to analyze</h2>

            <p>
              Enter a repository and commit above
              to generate a risk assessment.
            </p>

            <div className="demo-hint">
              Demo commit:{" "}
              <code>{DEFAULT_COMMIT}</code>
            </div>
          </section>
        )}
      </main>

      <footer>
        <span>ImpactGraph AI</span>

        <span>
          Dependency-aware ML risk prediction
        </span>
      </footer>
    </div>
  );
}

export default App;