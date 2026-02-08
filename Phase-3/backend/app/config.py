"""
Phase III Configuration Settings.

Extends Phase II settings with OpenAI and MCP configurations.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "Todo AI Chatbot API"
    VERSION: str = "1.0.0"
    
    # =========================================================================
    # Database settings (same as Phase II)
    # =========================================================================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_POOL_TIMEOUT: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))

    # =========================================================================
    # JWT settings (same as Phase II)
    # =========================================================================
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # =========================================================================
    # OpenAI settings (NEW for Phase III)
    # =========================================================================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)

    # =========================================================================
    # MCP Server settings (NEW for Phase III)
    # =========================================================================
    MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "TodoMCPServer")
    MCP_SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "1.0.0")

    # =========================================================================
    # Chat settings (NEW for Phase III)
    # =========================================================================
    MAX_CONTEXT_MESSAGES: int = int(os.getenv("MAX_CONTEXT_MESSAGES", "10"))
    MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
    CHAT_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("CHAT_RATE_LIMIT_PER_MINUTE", "60"))

    # =========================================================================
    # Application settings
    # =========================================================================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # =========================================================================
    # CORS settings
    # =========================================================================
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

    def get_allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string or JSON list."""
        raw = (os.getenv("ALLOWED_ORIGINS") or self.ALLOWED_ORIGINS or "").strip()
        if not raw:
            return []
        if raw.startswith('['):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed]
            except Exception:
                pass
        return [s.strip() for s in raw.split(',') if s.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
