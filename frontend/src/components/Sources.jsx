import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark, oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";

export default function Sources({ sources, theme }) {
  return (
    <section>
      <div className="glass-card">
        <div className="card-header-title">📘 Sources</div>
        <div className="card-header-sub">Retrieved code snippets for the answer.</div>
      </div>

      {sources.length === 0 ? (
        <div className="alert alert-info">No sources retrieved yet.</div>
      ) : (
        <div className="sources-scroll">
          {sources.map((s, idx) => {
            const lang = s.language && s.language !== "unknown" ? s.language : "python";
            return (
              <div key={`${s.file_path}-${idx}`}>
                <div className="source-item-card">
                  <div className="source-item-header">
                    <span className="source-item-file">📄 {s.file_path}</span>
                    <span className="source-item-match">{s.match_pct}% match</span>
                  </div>
                  <div className="source-item-lines">
                    Lines {s.start_line} - {s.end_line} | Lang: <code>{s.language}</code>
                  </div>
                </div>
                <details className="expander">
                  <summary>Inspect Snippet ({s.file_path})</summary>
                  <SyntaxHighlighter
                    language={lang}
                    style={theme === "Dark" ? oneDark : oneLight}
                    customStyle={{ margin: 0, borderRadius: 8, fontSize: "0.8rem" }}
                    showLineNumbers
                    startingLineNumber={s.start_line}
                  >
                    {s.content}
                  </SyntaxHighlighter>
                </details>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
