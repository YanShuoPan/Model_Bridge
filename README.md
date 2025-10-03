# AI Agent for Statistics — Simplified Single-User MVP

This bundle includes:
- **Backend**: FastAPI (parse → recommend → run), logistic regression, DR-ATE (CBPS-like)
- **Frontend**: Minimal Next.js page (single page, inline styles)
- **Deploy**: Render (backend) & Vercel (frontend) templates
- **Demos**: `binary_demo.csv`, `causal_demo.csv`

## Quickstart (Local)

### 1) Backend
```bash
python -m venv .venv && source .venv/bin/activate  # (Windows) .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
# Health: http://localhost:8000/api/health
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

> If you run backend on a different host/port, set `NEXT_PUBLIC_API` in `frontend/.env.local`:
```
NEXT_PUBLIC_API=http://<your-api-host>/api
```

---

## Deploy (URLs you will get)

- **Backend (Render)** → after deploy you'll get something like:  
  `https://<your-api-name>.onrender.com`  
  API base becomes: `https://<your-api-name>.onrender.com/api`

- **Frontend (Vercel)** → after deploy you'll get something like:  
  `https://<your-frontend>.vercel.app`

In Vercel, set Environment Variable:
```
NEXT_PUBLIC_API=https://<your-api-name>.onrender.com/api
```

### Render (Backend) — Option A: render.yaml
1. Push this repo to GitHub.
2. In Render: **New +** → **Blueprint** → select your repo. It will read `render.yaml`.
3. After deploy, visit `/api/health` to check health.

### Render (Backend) — Option B: manually create a Web Service
- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port 10000`
- Port: 10000 (Render sets `PORT` env; the start command can read `$PORT` if needed)
- Add environment variable `PORT` if required, or change start to:  
  `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Vercel (Frontend)
1. Import project from GitHub.
2. In Project → Settings → Environment Variables, add:
   - `NEXT_PUBLIC_API=https://<your-api-name>.onrender.com/api`
3. Deploy. Your site will be at `https://<your-frontend>.vercel.app`

---

## ngrok / Cloudflare Tunnel (temporary public URLs)
To expose local backend:
```bash
ngrok http 8000
# You'll get HTTPS URL like https://abcd-...ngrok-free.app
# Then in frontend .env.local:
NEXT_PUBLIC_API=https://abcd-...ngrok-free.app/api
```

---

## Project structure
```
ai-agent-stat/
├─ backend/
├─ frontend/
├─ render.yaml
├─ vercel.json
├─ requirements.txt
└─ README.md
```

---

## Demo CSVs
- `backend/storage/demo/binary_demo.csv` → columns: `y`, plus toy features
- `backend/storage/demo/causal_demo.csv` → columns: `treatment`, `y`, `x1..`

Upload one of them in the UI and try:
- For binary classification → pick Logistic Regression
- For causal ATE → pick DR-ATE (CBPS-like)
