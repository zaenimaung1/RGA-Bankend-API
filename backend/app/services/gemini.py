from __future__ import annotations

from typing import Any

import google.generativeai as genai

from app.core.config import settings


def configure_gemini() -> None:
    genai.configure(api_key=settings.gemini_api_key)


def generate_answer(prompt: str) -> str:
    model = genai.GenerativeModel(settings.gemini_model)
    resp = model.generate_content(prompt)
    text = getattr(resp, "text", None)
    if not text:
        raise RuntimeError("Gemini generation returned empty text")
    return text.strip()


def safe_json_from_gemini(text: str) -> dict[str, Any]:
    """
    Gemini might wrap JSON in markdown fences.
    We keep MVP-simple parsing: find first '{' and last '}'.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Gemini did not return JSON")
    import json

    return json.loads(text[start : end + 1])

