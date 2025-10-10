from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="AI Agent Stat - MVP")

# CORS: allow all for MVP; restrict later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure storage dirs
Path("backend/storage/uploads").mkdir(parents=True, exist_ok=True)
Path("backend/storage/runs").mkdir(parents=True, exist_ok=True)
Path("backend/storage/demo").mkdir(parents=True, exist_ok=True)

# Routers
from backend.routers import parse, recommend, run, chat  # noqa
app.include_router(parse.router, prefix="/api")
app.include_router(recommend.router, prefix="/api")
app.include_router(run.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.get("/api/health")
def health():
    return {"ok": True}

# Serve static artifacts (figures/reports) under backend/
app.mount("/", StaticFiles(directory="backend", html=False), name="static")
