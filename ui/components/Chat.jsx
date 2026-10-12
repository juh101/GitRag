import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { sendChat } from "../api.js";

const SUGGESTIONS = [
  "What is the overall architecture?",
  "Where is the core entry point?",
  "Explain the project structure.",
  "Which files handle main logic?",
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export default function Chat({ repo, messages, setMessages, onSources, topK, temperature }) {
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false); // waiting for backend
  const [typing, setTyping] = useState(false); // typewriter animation running
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  const send = async (text) => {
    const question = text.trim();
    if (!question || !repo || busy || typing) return;

    setError(null);
    setInput("");
    setMessages((m) => [...m, { role: "user", content: question }]);
    setBusy(true);

    try {
      const res = await sendChat({
        repoId: repo.repo_id,
        question,
        topK,
        temperature,
      });
      onSources(res.sources);
      setBusy(false);

      // Same "typing" effect as the Streamlit version, done client-side
      setTyping(true);
      setMessages((m) => [...m, { role: "assistant", content: "" }]);
      const words = res.answer.split(" ");
      let shown = "";
      for (const w of words) {
        shown += (shown ? " " : "") + w;
        const snapshot = shown;
        setMessages((m) => [...m.slice(0, -1), { role: "assistant", content: snapshot }]);
        await sleep(20);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
      setTyping(false);
    }
  };

  return (
    <section>
      <div className="glass-card">
        <div className="card-header-title">🗨️ Ask Your Repository</div>
        <div className="card-header-sub">
          Ask questions to retrieve code and generate answers with Gemini.
        </div>
      </div>

      {!repo ? (
        <div className="alert alert-info">
          Please index a GitHub repository above to start asking questions.
        </div>
      ) : (
        <>
          {messages.length === 0 && (
            <>
              <div className="caption">Try asking:</div>
              <div className="suggestions">
                {SUGGESTIONS.map((s) => (
                  <button key={s} className="btn" onClick={() => send(s)}>
                    ↗ {s}
                  </button>
                ))}
              </div>
            </>
          )}

          <div className="chat-scroll">
            {messages.map((m, i) => {
              const isLast = i === messages.length - 1;
              return (
                <div key={i} className={`chat-msg ${m.role}`}>
                  <div className="avatar">{m.role === "user" ? "🧑" : "🤖"}</div>
                  <div className={`bubble ${typing && isLast ? "typing" : ""}`}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                  </div>
                </div>
              );
            })}

            {busy && (
              <div className="chat-msg assistant">
                <div className="avatar">🤖</div>
                <div className="bubble">
                  <span className="spinner" /> Retrieving sources & generating answer...
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <div className="chat-input-row">
            <textarea
              className="text-input"
              rows={1}
              placeholder="Ask a question about this repository..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
              disabled={busy || typing}
            />
            <button
              className="btn"
              onClick={() => send(input)}
              disabled={busy || typing || !input.trim()}
            >
              Send
            </button>
          </div>
        </>
      )}
    </section>
  );
}
