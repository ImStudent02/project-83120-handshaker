from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConnectionRequest(BaseModel):
    """Connection request between users"""

    from_user: str
    to_user: str
    status: str = "pending"  # pending, accepted, declined
    created_at: datetime = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class ConnectionRequestCreate(BaseModel):
    """Request to create a connection"""

    to_user: str


class ConnectionRequestResponse(BaseModel):
    """Response for connection request"""

    request_id: str
    from_user: str
    to_user: str
    status: str
    created_at: str


class ConnectionRequestAction(BaseModel):
    """Accept or decline a request"""

    request_id: str
    action: str  # "accept" or "decline"
