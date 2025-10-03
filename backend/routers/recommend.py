from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.recommender import recommend_methods

router = APIRouter(tags=["recommend"])

class RecIn(BaseModel):
    task: str
    y_type: str
    roles: dict

@router.post("/recommend")
def recommend_endpoint(p: RecIn):
    return {"recommendations": recommend_methods(p.task, p.y_type, p.roles)}
