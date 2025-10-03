export const API_BASE = process.env.NEXT_PUBLIC_API || "http://localhost:8000/api";

export async function apiParse(form: FormData) {
  const r = await fetch(`${API_BASE}/parse`, { method: "POST", body: form });
  if (!r.ok) throw new Error("parse failed");
  return r.json();
}

export async function apiRecommend(payload: any) {
  const r = await fetch(`${API_BASE}/recommend`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error("recommend failed");
  return r.json();
}

export async function apiRun(payload: any) {
  const r = await fetch(`${API_BASE}/run`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error("run failed");
  return r.json();
}
