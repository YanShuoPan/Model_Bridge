from fastapi import APIRouter, UploadFile, File, Form
from backend.services.parser import parse_question_and_csv

router = APIRouter(tags=["parse"])

@router.post("/parse")
async def parse_endpoint(
    question: str = Form(...),
    file: UploadFile = File(...)
):
    return parse_question_and_csv(question, file)
