from fastapi import APIRouter, Depends

from app.core.deps import get_current_user_id
from app.db.mongodb import get_db


router = APIRouter()


@router.get("/history")
async def history(limit: int = 30, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    cur = (
        db["chat_history"]
        .find({"user_id": user_id}, {"_id": 0})
        .sort("created_at", -1)
        .limit(max(1, min(limit, 200)))
    )
    items = await cur.to_list(length=max(1, min(limit, 200)))
    return {"items": list(reversed(items))}
