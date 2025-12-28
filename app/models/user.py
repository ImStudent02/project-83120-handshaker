from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserInDB(BaseModel):
    """User document stored in MongoDB"""

    username: str  # @unique_id format
    email_encrypted: str  # AES encrypted (server can't read)
    birthday_encrypted: str  # AES encrypted (for key recovery)
    password_hash: str  # Argon2 hash
    pgp_public_key: str  # PGP public key (for encryption)
    is_online: bool = False
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
