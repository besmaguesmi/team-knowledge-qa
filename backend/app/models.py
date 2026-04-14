from pydantic import BaseModel
from typing import List

class DocumentUpload(BaseModel):
    filename: str
    content: str  # base64 or plain text; we'll use multipart form data

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[str]  # which document chunks were used