from __future__ import annotations

import hashlib
from typing import Any

from app.core.config import settings
from app.db.chroma import get_collection
from app.services.gemini import generate_answer, safe_json_from_gemini


def _row_id(keyword: str | None, proverb: str) -> str:
    raw = f"{keyword or ''}||{proverb}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()


def _normalize_row(row: dict[str, Any]) -> dict[str, str | None]:
    keyword = (row.get("keyword") or "").strip() or None
    proverb = (row.get("proverb") or "").strip()
    meaning = (row.get("meaning") or "").strip() or None
    example = (row.get("example") or "").strip() or None
    if not proverb:
        raise ValueError("proverb is required")
    return {"keyword": keyword, "proverb": proverb, "meaning": meaning, "example": example}


def _build_chroma_record(row: dict[str, str | None]) -> tuple[str, str, dict[str, Any]]:
    keyword = row["keyword"]
    proverb = row["proverb"]
    meaning = row["meaning"]
    example = row["example"]
    doc = f"keyword: {keyword or ''}\nproverb: {proverb}\nmeaning: {meaning or ''}\nexample: {example or ''}"
    metadata = {
        "keyword": keyword,
        "proverb": proverb,
        "meaning": meaning,
        "example": example,
    }
    return _row_id(keyword, proverb), doc, metadata


def add_proverb(row: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_row(row)
    proverb_id, doc, metadata = _build_chroma_record(normalized)
    col = get_collection()
    col.upsert(ids=[proverb_id], documents=[doc], metadatas=[metadata])
    return {"id": proverb_id, **normalized}


def update_proverb(proverb_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    col = get_collection()
    existing = col.get(ids=[proverb_id], include=["metadatas"])
    metadatas = existing.get("metadatas") or []
    if not metadatas or not metadatas[0]:
        raise ValueError("Proverb not found")

    current = metadatas[0]
    merged = {
        "keyword": updates.get("keyword", current.get("keyword")),
        "proverb": updates.get("proverb", current.get("proverb")),
        "meaning": updates.get("meaning", current.get("meaning")),
        "example": updates.get("example", current.get("example")),
    }
    normalized = _normalize_row(merged)
    new_id, doc, metadata = _build_chroma_record(normalized)

    if new_id != proverb_id:
        col.delete(ids=[proverb_id])

    col.upsert(ids=[new_id], documents=[doc], metadatas=[metadata])
    return {"id": new_id, **normalized}


def upsert_proverbs(rows: list[dict[str, Any]]) -> tuple[int, int]:
    """
    rows: [{keyword, proverb, meaning, example}]
    """
    col = get_collection()
    inserted = 0
    skipped = 0

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, Any]] = []

    for r in rows:
        try:
            normalized = _normalize_row(r)
        except ValueError:
            skipped += 1
            continue

        proverb_id, doc, metadata = _build_chroma_record(normalized)
        ids.append(proverb_id)
        documents.append(doc)
        metadatas.append(metadata)

    if ids:
        col.upsert(ids=ids, documents=documents, metadatas=metadatas)
        inserted = len(ids)

    return inserted, skipped


def retrieve_context(query: str, top_k: int | None = None) -> list[dict[str, Any]]:
    col = get_collection()
    k = top_k or settings.rag_top_k
    res = col.query(query_texts=[query], n_results=k, include=["metadatas", "distances"])

    metadatas = (res.get("metadatas") or [[]])[0]
    distances = (res.get("distances") or [[]])[0]

    ctx: list[dict[str, Any]] = []
    for md, dist in zip(metadatas, distances):
        if not md:
            continue
        ctx.append(
            {
                "keyword": md.get("keyword"),
                "proverb": md.get("proverb"),
                "meaning": md.get("meaning"),
                "example": md.get("example"),
                "score": float(dist) if dist is not None else None,
            }
        )
    return ctx


def rag_answer(user_question: str) -> dict[str, Any]:
    sources = retrieve_context(user_question, top_k=settings.rag_top_k)

    prompt = f"""
You are a helpful Myanmar language tutor for kids.
You MUST answer in Burmese (Myanmar).
Return ONLY valid JSON (no markdown, no extra text).

User question:
{user_question}

Retrieved proverbs (context):
{sources}

JSON schema:
{{
  "proverb": "most relevant proverb (string)",
  "meaning_simple_mm": "simple Burmese explanation for kids (string)",
  "example_mm": "simple Burmese example sentence (string)",
  "sources": [{{"keyword": "...", "proverb": "...", "meaning": "...", "example": "...", "score": 0.0}}]
}}

Rules:
- Choose the best proverb from the retrieved context.
- Keep meaning very simple.
- Use respectful Burmese and simple words.
- Include the sources array (reuse the context you got).
"""

    raw = generate_answer(prompt)
    answer = safe_json_from_gemini(raw)
    if "sources" not in answer:
        answer["sources"] = sources
    return answer
