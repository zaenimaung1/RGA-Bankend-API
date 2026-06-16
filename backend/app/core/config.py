from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Myanmar Proverbs AI Tutor"
    environment: str = "local"
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    mongodb_uri: str
    mongodb_db_name: str = "mm_proverbs_ai"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24 * 7

    gemini_api_key: str
    gemini_model: str = "gemini-flash-latest"

    chroma_persist_dir: str = "./chroma_data"
    chroma_collection_name: str = "proverbs"

    rag_top_k: int = 5

    # If set, this email is assigned admin role on register.
    admin_email: str = ""

    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()

