from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.runner import run_method

router = APIRouter(tags=["run"])

class RunIn(BaseModel):
    method_id: str
    file_path: str
    roles: dict
    params: dict | None = None

@router.post("/run")
def run_endpoint(p: RunIn):
    result = run_method(p.method_id, p.file_path, p.roles, p.params or {})
    return result
