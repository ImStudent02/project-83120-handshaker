from fastapi import APIRouter, Depends
from app.schemas.signaling import (
    SignalSendRequest,
    SignalPollResponse,
    ICEServersResponse,
)
from app.services import signaling_service
from app.utils.security import get_current_user
from app.config import settings

router = APIRouter(prefix="/signaling", tags=["Signaling"])


@router.post("/send")
async def send_signal(
    req: SignalSendRequest, current_user: str = Depends(get_current_user)
):
    """
    Send signaling message (offer/answer/ICE) to another user.

    The encrypted_payload is PGP-encrypted by the client.
    Server CANNOT read it - just relays to recipient.
    """
    await signaling_service.send_signal(current_user, req)
    return {"message": "Signal sent"}


@router.get("/poll", response_model=SignalPollResponse)
async def poll_signals(current_user: str = Depends(get_current_user)):
    """
    Poll for pending signaling messages.

    Returns PGP-encrypted payloads that only the client can decrypt.
    Messages are deleted after fetching.
    """
    messages = await signaling_service.poll_signals(current_user)
    return SignalPollResponse(messages=messages)


@router.delete("/clear")
async def clear_signals(current_user: str = Depends(get_current_user)):
    """Clear all pending signals for current user"""
    count = await signaling_service.clear_signals(current_user)
    return {"deleted": count}


@router.get("/ice-servers", response_model=ICEServersResponse)
async def get_ice_servers(current_user: str = Depends(get_current_user)):
    """
    Get configured STUN/TURN servers for WebRTC.
    Easily replaceable via server config.
    """
    return ICEServersResponse(
        stun_servers=settings.stun_list, turn_servers=settings.turn_list
    )
