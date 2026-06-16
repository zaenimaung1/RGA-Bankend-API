from __future__ import annotations

from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from app.core.config import settings


class Chroma:
    client: Any | None = None
    collection: Any | None = None


chroma = Chroma()


def connect_chroma() -> None:
    chroma.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    chroma.collection = chroma.client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=embedding_fn,
    )


def get_collection():
    if not chroma.collection:
        raise RuntimeError("ChromaDB is not connected")
    return chroma.collection
