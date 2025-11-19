from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.recommender import recommend_methods, recommend_methods_by_domains

router = APIRouter(tags=["recommend"])

class RecIn(BaseModel):
    task: str
    y_type: str
    roles: dict
    question: Optional[str] = ""
    df_info: Optional[dict] = None

class DomainRecIn(BaseModel):
    question: str
    df_info: Optional[dict] = None
    top_n: Optional[int] = 5

@router.post("/recommend")
def recommend_endpoint(p: RecIn):
    """
    傳統推薦方式（基於規則與任務類型）
    保留此 API 以維持向後兼容
    """
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

@router.post("/recommend/by-domains")
def recommend_by_domains_endpoint(p: DomainRecIn):
    """
    新的多領域推薦方式（基於 GPT 領域識別 + 領域匹配）

    Args:
        question: 使用者研究問題
        df_info: 數據資訊（選填），包含 n_rows, n_cols, columns 等
        top_n: 返回前 N 個推薦方法（預設 5）

    Returns:
        {
            "question_domains": {...},  # 問題涉及的領域及分數
            "recommended_methods": [...],  # 推薦的方法列表（按匹配度排序）
            "reasoning": "...",  # GPT 分析的推薦理由
            "primary_domain": "...",  # 主要領域
            "total_methods_evaluated": int,  # 評估的方法總數
            "total_matched": int  # 匹配到的方法數
        }
    """
    try:
        result = recommend_methods_by_domains(
            question=p.question,
            df_info=p.df_info,
            top_n=p.top_n,
            use_gpt_identification=True
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "question_domains": {},
            "recommended_methods": [],
            "reasoning": f"推薦失敗: {str(e)}"
        }
