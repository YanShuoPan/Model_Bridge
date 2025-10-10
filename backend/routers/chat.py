"""
對話式統計諮詢 API
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.chat_service import (
    generate_chat_response,
    get_example_questions,
    get_method_details
)

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    question: str


class MethodRequest(BaseModel):
    method_id: str


@router.post("/chat")
def chat_endpoint(req: ChatRequest):
    """
    對話式諮詢端點
    使用者提問 → GPT 分析 → 推薦方法
    """
    response = generate_chat_response(req.question)
    return response


@router.get("/chat/examples")
def get_examples():
    """
    取得範例問題列表
    """
    return {"examples": get_example_questions()}


@router.get("/chat/methods/{method_id}")
def get_method(method_id: str):
    """
    取得特定統計方法的詳細資訊
    """
    method = get_method_details(method_id)
    if not method:
        return {"error": "Method not found"}
    return method
