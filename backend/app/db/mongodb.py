from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


class Mongo:
    client: AsyncIOMotorClient | None = None


mongo = Mongo()


def connect_mongodb() -> None:
    mongo.client = AsyncIOMotorClient(settings.mongodb_uri)


def close_mongodb() -> None:
    if mongo.client:
        mongo.client.close()
        mongo.client = None


def get_db():
    if not mongo.client:
        raise RuntimeError("MongoDB is not connected")
    return mongo.client[settings.mongodb_db_name]

