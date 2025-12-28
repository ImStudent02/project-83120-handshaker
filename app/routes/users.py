from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas.auth import UserPublicInfo
from app.services import auth_service
from app.utils.security import get_current_user
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/search", response_model=List[UserPublicInfo])
async def search_users(
    q: str = Query(..., min_length=1, description="Search query (username prefix)"),
    current_user: str = Depends(get_current_user),
):
    """
    Search users by username.
    Returns list of users with their PGP public keys.
    """
    users = await auth_service.search_users(q)
    return [
        UserPublicInfo(
            username=u["username"],
            pgp_public_key=u["pgp_public_key"],
            is_online=u.get("is_online", False),
        )
        for u in users
        if u["username"] != current_user  # Exclude self
    ]


@router.get("/{username}", response_model=UserPublicInfo)
async def get_user(username: str, current_user: str = Depends(get_current_user)):
    """
    Get user's public info including PGP public key.
    Used for encrypting messages to this user.
    """
    try:
        return await auth_service.get_user_public(username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
