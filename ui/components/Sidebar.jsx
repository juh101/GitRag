const THEMES = ["Dark", "Light"];

export default function Sidebar({
  theme,
  setTheme,
  topK,
  setTopK,
  temperature,
  setTemperature,
  repo,
  onClear,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h3>🐙 GitHub Repository</h3>
        <strong>AI Assistant</strong>
        <p>Understand any repository using Retrieval-Augmented Generation</p>
      </div>

      <hr />
      <div className="sidebar-label">Theme</div>
      <div className="radio-group">
        {THEMES.map((t) => (
          <label key={t} className="radio">
            <input
              type="radio"
              name="theme"
              checked={theme === t}
              onChange={() => setTheme(t)}
            />
            {t}
          </label>
        ))}
      </div>

      <hr />
      <div className="sidebar-label">⚙️ RAG Hyper-Parameters</div>

      <div className="slider-block" title="Number of relevant code chunks passed to the LLM context window.">
        <div className="slider-row">
          <span>Top-K Chunks Retrieved</span>
          <span className="slider-val">{topK}</span>
        </div>
        <input
          type="range"
          min={1}
          max={10}
          step={1}
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
        />
      </div>

      <div className="slider-block" title="Lower = deterministic answers, higher = more creative explanations.">
        <div className="slider-row">
          <span>Gemini Temperature</span>
          <span className="slider-val">{temperature.toFixed(1)}</span>
        </div>
        <input
          type="range"
          min={0}
          max={1}
          step={0.1}
          value={temperature}
          onChange={(e) => setTemperature(Number(e.target.value))}
        />
      </div>

      <hr />
      <div className="sidebar-label">Repository Status</div>
      {repo ? (
        <div className="alert alert-success">
          Indexed: <strong>{repo.owner}/{repo.name}</strong>
        </div>
      ) : (
        <div className="alert alert-info">No repository indexed yet.</div>
      )}

      <hr />
      <div className="sidebar-label">Quick Actions</div>
      <button className="btn btn-block" onClick={onClear}>
        🗑️ Clear Conversation
      </button>

      <hr />
      <p className="caption">
        GitHub Repository AI Assistant uses semantic search with FAISS and Gemini to answer
        repository-specific questions.
      </p>
    </aside>
  );
}
