from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class SignalingMessage(BaseModel):
    """
    Signaling message for WebRTC handshake.
    Server CANNOT read the payload - it's PGP encrypted by sender.
    """

    from_user: str  # @sender username
    to_user: str  # @receiver username
    type: Literal["offer", "answer", "ice"]
    encrypted_payload: str  # PGP-encrypted WebRTC data
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # TTL - auto-deleted after this
