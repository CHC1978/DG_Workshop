"""應用程式配置"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """應用程式設定"""

    # 應用程式基本設定
    APP_NAME: str = "Marine Equipment QR System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 安全性設定
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Token 過期時間 (分鐘)
    # 生產環境建議使用更短的過期時間以降低 token 被竊取的風險
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 從 30 分鐘縮短至 15 分鐘
    TEMP_TOKEN_EXPIRE_MINUTES: int = 3     # 從 5 分鐘縮短至 3 分鐘 (2FA 驗證用)

    # 資料庫設定
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/marine_equipment.db"

    # CORS 設定
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # QR Code 設定
    QR_CODE_DOMAIN: str = "localhost:5173"  # QR code URL domain (可設為固定 IP)
    QR_CODE_PROTOCOL: str = "http"  # http or https

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


# 建立全域設定實例
settings = Settings()
