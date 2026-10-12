async function errorText(res) {
  try {
    const data = await res.json();
    return data.detail ?? `Request failed (${res.status})`;
  } catch {
    return `Request failed (${res.status})`;
  }
}

/**
 * Index a repo. Reads the NDJSON stream so we can show live progress steps.
 * onStep receives { type: "step", step: number, message: string }
 * Resolves to { repo_id, owner, name, stats: {files, chunks, languages}, file_paths }
 */
export async function indexRepo(repoUrl, onStep) {
  const res = await fetch("/api/repos/index", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl }),
  });
  if (!res.ok || !res.body) throw new Error(await errorText(res));

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let result = null;

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.trim()) continue;
      const evt = JSON.parse(line);
      if (evt.type === "step") onStep(evt);
      else if (evt.type === "error") throw new Error(evt.message);
      else if (evt.type === "done") result = evt.repo;
    }
  }

  if (!result) throw new Error("Indexing ended unexpectedly.");
  return result;
}

/**
 * Ask a question. Resolves to { answer: string, sources: Source[] }
 * Source = { file_path, start_line, end_line, match_pct, content, language }
 */
export async function sendChat({ repoId, question, topK, temperature }) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      repo_id: repoId,
      question,
      top_k: topK,
      temperature,
    }),
  });
  if (!res.ok) throw new Error(await errorText(res));
  return res.json();
}
