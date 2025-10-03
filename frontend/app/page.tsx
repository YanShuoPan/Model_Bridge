"use client";
import React, { useState } from "react";
import { apiParse, apiRecommend, apiRun } from "../lib/api";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("我想估計處理的平均因果效果（ATE）");
  const [parsed, setParsed] = useState<any>(null);
  const [recs, setRecs] = useState<any[]>([]);
  const [result, setResult] = useState<any>(null);

  async function doParse() {
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    fd.append("question", question);
    const p = await apiParse(fd);
    setParsed(p);
    const rr = await apiRecommend({ task: p.task, y_type: p.y_type, roles: p.roles });
    setRecs(rr.recommendations);
  }

  async function run(method_id: string) {
    if (!parsed) return;
    const r = await apiRun({ method_id, file_path: parsed.file_path, roles: parsed.roles });
    setResult(r);
  }

  const apiBase = process.env.NEXT_PUBLIC_API || "http://localhost:8000/api";
  const apiOrigin = typeof window === "undefined" ? "" : new URL(apiBase).origin;

  return (
    <main style={{ maxWidth: 1100, margin: "20px auto", padding: 16, fontFamily: "ui-sans-serif, system-ui" }}>
      <h1 style={{ fontSize: 28 }}>AI Agent for Statistics (MVP)</h1>

      <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
        <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
          <h2>① 上傳 CSV & 提問</h2>
          <input type="file" accept=".csv" onChange={e => setFile(e.target.files?.[0] || null)} />
          <textarea value={question} onChange={e => setQuestion(e.target.value)} style={{ width: "100%", height: 100, marginTop: 8 }} />
          <button onClick={doParse} style={{ marginTop: 8, padding: "8px 12px" }}>解析並推薦</button>
          {parsed && (
            <div style={{ marginTop: 12, fontSize: 14 }}>
              <div>task: <b>{parsed.task}</b> | y_type: <b>{parsed.y_type}</b></div>
              <div>roles: <code>{JSON.stringify(parsed.roles)}</code></div>
              <div>preview: rows={parsed.preview.n_rows}, cols={parsed.preview.n_cols}</div>
            </div>
          )}
        </div>

        <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
          <h2>② 方法推薦</h2>
          {recs.length === 0 ? <p>尚無推薦</p> :
            recs.map(r => (
              <div key={r.method_id} style={{ border: "1px solid #eee", borderRadius: 10, padding: 10, marginBottom: 8 }}>
                <div style={{ fontWeight: 600 }}>{r.name}</div>
                <div style={{ fontSize: 14, opacity: .8 }}>{r.why}</div>
                <button onClick={() => run(r.method_id)} style={{ marginTop: 6, padding: "6px 10px" }}>
                  執行此方法
                </button>
              </div>
            ))
          }
        </div>

        <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
          <h2>③ 執行結果</h2>
          {!result ? <p>尚未執行</p> : (
            <>
              <div style={{ fontSize: 14 }}>run_id: <code>{result.run_id}</code></div>
              <pre style={{ background: "#f7f7f7", padding: 8, whiteSpace: "pre-wrap" }}>
                {JSON.stringify(result.metrics, null, 2)}
              </pre>
              {result.figures?.map((p: string) => (
                <div key={p} style={{ marginBottom: 8 }}>
                  <img src={`${apiOrigin}/${p.replace("backend/","")}`} style={{ maxWidth: "100%" }} />
                </div>
              ))}
              <a href={`${apiOrigin}/${result.report_html_path.replace("backend/","")}`} target="_blank" rel="noreferrer">開啟報告（HTML）</a>
            </>
          )}
        </div>
      </section>

      <section style={{ marginTop: 24 }}>
        <h3>快速測試資料</h3>
        <p>可用後端內建的 demo CSV（先下載到本機再上傳）：</p>
        <ul>
          <li><code>http://localhost:8000/storage/demo/binary_demo.csv</code></li>
          <li><code>http://localhost:8000/storage/demo/causal_demo.csv</code></li>
        </ul>
      </section>
    </main>
  );
}
