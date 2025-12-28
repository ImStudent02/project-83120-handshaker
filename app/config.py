from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration - easily replaceable via .env"""
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "project83120"
    
    # JWT Authentication
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Email encryption (server-side only)
    EMAIL_ENCRYPTION_KEY: str = "32-byte-key-for-email-encryption!"
    
    # STUN/TURN - easily replaceable
    STUN_SERVERS: str = "stun:stun.l.google.com:19302,stun:stun1.l.google.com:19302"
    TURN_SERVERS: str = ""
    TURN_USERNAME: str = ""
    TURN_CREDENTIAL: str = ""
    
    # Signaling
    SIGNAL_EXPIRE_SECONDS: int = 60  # Auto-delete signals after 60s
    
    @property
    def stun_list(self) -> List[str]:
        return [s.strip() for s in self.STUN_SERVERS.split(",") if s.strip()]
    
    @property
    def turn_list(self) -> List[dict]:
        if not self.TURN_SERVERS:
            return []
        return [
            {
                "urls": s.strip(),
                "username": self.TURN_USERNAME,
                "credential": self.TURN_CREDENTIAL
            }
            for s in self.TURN_SERVERS.split(",") if s.strip()
        ]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
