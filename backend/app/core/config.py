from typing import Any, List, Union, Optional
from pydantic import AnyHttpUrl, BeforeValidator, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


def parse_cors(v: Any) -> List[str]:
    """
    Parses CORS origins from a list, string, or JSON array.
    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        import json
        try:
            return json.loads(v) if isinstance(v, str) else v
        except json.JSONDecodeError:
            raise ValueError(f"Invalid CORS JSON string format: {v}")
    return v


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "AI Career Copilot"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS configuration
    BACKEND_CORS_ORIGINS: Annotated[
        List[str], BeforeValidator(parse_cors)
    ] = []

    # Security configuration
    SECRET_KEY: str = "9a15f01eef4428df127267035418b766860d2d348a27d2c3cf8bdc6d3284ff35"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520

    # API Keys for LLM providers
    GEMINI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None


    # Database configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "career_copilot"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, values: Any) -> Any:
        if isinstance(v, str) and v:
            return v
        
        # Access elements from the dynamic values dict/settings representation
        # Pydantic v2 validation context retrieves raw settings fields
        data = values.data
        postgres_user = data.get("POSTGRES_USER")
        postgres_password = data.get("POSTGRES_PASSWORD")
        postgres_server = data.get("POSTGRES_SERVER")
        postgres_port = data.get("POSTGRES_PORT")
        postgres_db = data.get("POSTGRES_DB")

        return f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}:{postgres_port}/{postgres_db}"


settings = Settings()
