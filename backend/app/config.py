"""
Application Configuration & Security Settings
"""
import os
from functools import lru_cache
from dotenv import load_dotenv
from typing import List

load_dotenv()


class Settings:
    """Application settings and configuration"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    WS_SECRET_TOKEN: str = os.getenv("WS_SECRET_TOKEN", "dev-ws-token-change-in-production")
    
    # CORS Settings
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Get allowed origins based on environment"""
        if self.ENVIRONMENT == "production":
            origins_str = os.getenv("ALLOWED_ORIGINS", "")
            return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
        else:
            # Development origins
            return [
                "http://localhost:5173",
                "http://localhost:3000",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000",
            ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_CHAT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_CHAT_PER_MINUTE", "10"))
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
    GEMINI_TIMEOUT_SECONDS: int = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "20"))
    NVIDIA_TIMEOUT_SECONDS: int = int(os.getenv("NVIDIA_TIMEOUT_SECONDS", "15"))
    
    def validate_api_keys(self):
        """Validate API keys are properly configured"""
        invalid_keys = ["MASUKKAN_API_KEY_ANDA_DI_SINI", "masukkan_api_key_anda_disini", ""]
        
        if self.GEMINI_API_KEY in invalid_keys:
            raise ValueError(
                "GEMINI_API_KEY tidak valid atau belum diisi. "
                "Silakan set di file .env"
            )
        
        if len(self.GEMINI_API_KEY) < 20:
            raise ValueError(
                "GEMINI_API_KEY format tidak valid (terlalu pendek). "
                "Pastikan Anda menggunakan API key yang benar."
            )
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    settings = Settings()
    
    # Validate critical settings on startup
    try:
        settings.validate_api_keys()
    except ValueError as e:
        print(f"⚠️ Warning: {e}")
        print("⚠️ Beberapa fitur mungkin tidak berfungsi tanpa API key yang valid.")
    
    return settings


# Export settings instance
settings = get_settings()
