from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class SourceItem(BaseModel):
    keyword: str | None = None
    proverb: str
    meaning: str | None = None
    example: str | None = None
    score: float | None = None


class ChatAnswer(BaseModel):
    proverb: str
    meaning_simple_mm: str
    example_mm: str
    sources: list[SourceItem] = []


class ChatResponse(BaseModel):
    answer: ChatAnswer


class HistoryItem(BaseModel):
    user_message: str
    assistant_message: dict
    created_at: datetime

