from pydantic import BaseModel
from typing import Literal, List


class SignalSendRequest(BaseModel):
    """Send signaling message (PGP-encrypted by client)"""

    to_user: str  # @receiver username
    type: Literal["offer", "answer", "ice"]
    encrypted_payload: str  # Server can't read this


class SignalMessage(BaseModel):
    """Signaling message returned to client"""

    from_user: str
    type: Literal["offer", "answer", "ice"]
    encrypted_payload: str
    timestamp: str


class SignalPollResponse(BaseModel):
    """Response for polling signals"""

    messages: List[SignalMessage]


class ICEServersResponse(BaseModel):
    """Return configured STUN/TURN servers"""

    stun_servers: List[str]
    turn_servers: List[dict]
