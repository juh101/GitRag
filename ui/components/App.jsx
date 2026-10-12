import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import Header from "./components/Header.jsx";
import Repository from "./components/Repository.jsx";
import Chat from "./components/Chat.jsx";
import Sources from "./components/Sources.jsx";

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "Dark");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [topK, setTopK] = useState(5);
  const [temperature, setTemperature] = useState(0.2);

  const [repo, setRepo] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sources, setSources] = useState([]);

  // Equivalent of apply_theme(): CSS variables switch on [data-theme]
  useEffect(() => {
    document.documentElement.dataset.theme = theme.toLowerCase();
    localStorage.setItem("theme", theme);
  }, [theme]);

  const handleIndexed = (r) => {
    setRepo(r);
    setMessages([]);
    setSources([]);
  };

  const clearConversation = () => {
    setMessages([]);
    setSources([]);
  };

  return (
    <div className="app-shell">
      <button
        className="sidebar-toggle"
        onClick={() => setSidebarOpen((o) => !o)}
        aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
      >
        {sidebarOpen ? "«" : "»"}
      </button>

      {sidebarOpen && (
        <Sidebar
          theme={theme}
          setTheme={setTheme}
          topK={topK}
          setTopK={setTopK}
          temperature={temperature}
          setTemperature={setTemperature}
          repo={repo}
          onClear={clearConversation}
        />
      )}

      <main className="main">
        <Header />
        <Repository repo={repo} onIndexed={handleIndexed} />

        <div className="two-col">
          <Chat
            repo={repo}
            messages={messages}
            setMessages={setMessages}
            onSources={setSources}
            topK={topK}
            temperature={temperature}
          />
          <Sources sources={sources} theme={theme} />
        </div>
      </main>
    </div>
  );
}
