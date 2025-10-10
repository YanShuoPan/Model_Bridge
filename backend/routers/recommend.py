from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.recommender import recommend_methods

router = APIRouter(tags=["recommend"])

class RecIn(BaseModel):
    task: str
    y_type: str
    roles: dict
    question: Optional[str] = ""
    df_info: Optional[dict] = None

@router.post("/recommend")
def recommend_endpoint(p: RecIn):
    return {
        "recommendations": recommend_methods(
            task=p.task,
            y_type=p.y_type,
            roles=p.roles,
            question=p.question,
            df_info=p.df_info,
            use_gpt=True
        )
    }
