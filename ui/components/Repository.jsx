import { useState } from "react";
import { indexRepo } from "../api.js";

const TOTAL_STEPS = 4;
const GITHUB_PATH =
  "M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z";

export default function Repository({ repo, onIndexed }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [stepMsg, setStepMsg] = useState(null);
  const [step, setStep] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showAllFiles, setShowAllFiles] = useState(false);

  const handleIndex = async () => {
    if (!url.trim()) {
      setError("Please enter a valid GitHub repository URL.");
      return;
    }
    setError(null);
    setSuccess(null);
    setLoading(true);
    setStep(1);
    setStepMsg("Starting...");
    try {
      const r = await indexRepo(url.trim(), (e) => {
        setStep(e.step);
        setStepMsg(e.message);
      });
      setStep(TOTAL_STEPS);
      setSuccess(`Successfully indexed ${r.owner}/${r.name}!`);
      setStepMsg(null);
      onIndexed(r);
      setTimeout(() => setSuccess(null), 2500);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStepMsg(null);
    } finally {
      setLoading(false);
    }
  };

  const files = repo?.file_paths ?? [];
  const visibleFiles = showAllFiles ? files : files.slice(0, 15);

  return (
    <section>
      <div className="glass-card">
        <div className="card-header-title">📁 Repository Indexing</div>
        <div className="card-header-sub">
          Enter a public GitHub URL to clone, chunk, and index the codebase.
        </div>
      </div>

      <div className="repo-input-row">
        <input
          className="text-input"
          type="text"
          placeholder="https://github.com/pallets/markupsafe"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && handleIndex()}
          disabled={loading}
        />
        <button className="btn" onClick={handleIndex} disabled={loading}>
          {loading ? "Indexing..." : "⚡ Index Repo"}
        </button>
      </div>

      {stepMsg && (
        <div className="alert alert-info">
          🔄 Step {step}/{TOTAL_STEPS}: {stepMsg}
        </div>
      )}
      {success && <div className="alert alert-success">✅ Step 4/4: {success}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {repo && (
        <>
          <div className="metrics-row">
            <div className="repo-main-card">
              <div className="repo-title-text">
                <svg height="22" viewBox="0 0 16 16" width="22" fill="currentColor">
                  <path d={GITHUB_PATH} />
                </svg>
                <span>{repo.owner} / {repo.name}</span>
                <span className="repo-badge-indexed">Indexed</span>
              </div>
            </div>
            <Metric icon="📄" value={repo.stats.files} label="Files" />
            <Metric icon="📦" value={repo.stats.chunks} label="Chunks" />
            <Metric icon="💻" value={repo.stats.languages} label="Languages" />
          </div>

          <details className="expander">
            <summary>🌳 Inspect Parsed File Structure</summary>
            <div className="expander-body">
              {files.length === 0 && <div className="caption">No file details available.</div>}
              {visibleFiles.map((p) => (
                <div key={p} className="file-line">📄 {p}</div>
              ))}
              {files.length > 15 && (
                <button className="link-btn" onClick={() => setShowAllFiles((s) => !s)}>
                  {showAllFiles ? "Show less" : `... and ${files.length - 15} more files. Show all`}
                </button>
              )}
            </div>
          </details>
        </>
      )}
    </section>
  );
}

function Metric({ icon, value, label }) {
  return (
    <div className="metric-card-box">
      <div className="metric-card-val">{icon} {value}</div>
      <div className="metric-card-lbl">{label}</div>
    </div>
  );
}
