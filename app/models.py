from pydantic import BaseModel
from typing import Optional, List

class QuestionRequest(BaseModel):
    """Модель запроса от пользователя"""
    query: str
    top_k: Optional[int] = 5

class Source(BaseModel):
    """Модель источника информации"""
    document: str
    page: int
    text: str

class AnswerResponse(BaseModel):
    """Модель ответа ассистента"""
    answer: str
    sources: List[Source] = []
    confidence: float = 0.0