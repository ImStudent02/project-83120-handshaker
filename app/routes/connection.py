"""
Connection Routes
API endpoints for connection requests
"""

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.connection import ConnectionRequestCreate, ConnectionRequestAction
from app.services.connection_service import (
    send_connection_request,
    get_pending_requests,
    respond_to_request,
    get_connections,
    remove_connection,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/connections", tags=["Connections"])


@router.post("/request")
async def create_request(
    data: ConnectionRequestCreate, current_user: str = Depends(get_current_user)
):
    """Send a connection request to another user"""
    try:
        result = await send_connection_request(current_user, data.to_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pending")
async def get_pending(current_user: str = Depends(get_current_user)):
    """Get all pending incoming connection requests"""
    return await get_pending_requests(current_user)


@router.post("/respond")
async def respond(
    data: ConnectionRequestAction, current_user: str = Depends(get_current_user)
):
    """Accept or decline a connection request"""
    try:
        result = await respond_to_request(data.request_id, data.action, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
async def list_connections(current_user: str = Depends(get_current_user)):
    """Get all accepted connections"""
    return await get_connections(current_user)


@router.delete("/{username}")
async def delete_connection(
    username: str, current_user: str = Depends(get_current_user)
):
    """Remove a connection"""
    success = await remove_connection(current_user, username)
    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"message": "Connection removed"}
