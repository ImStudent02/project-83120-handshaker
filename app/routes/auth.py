from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserPublicInfo,
    UpdatePGPKeyRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
)
from app.services import auth_service
from app.utils.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    """
    Register new user with PGP public key.
    - Client generates PGP keypair locally
    - Uploads public key to server
    - Private key stays on device
    """
    try:
        return await auth_service.register_user(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Authenticate and get JWT token"""
    try:
        return await auth_service.login_user(req.username, req.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    """Mark user as offline"""
    await auth_service.set_user_offline(current_user)
    return {"message": "Logged out"}


@router.put("/pgp-key")
async def update_pgp_key(
    req: UpdatePGPKeyRequest, current_user: str = Depends(get_current_user)
):
    """
    Update PGP public key.
    Use this after reinstall when client regenerates keypair.
    """
    success = await auth_service.update_pgp_key(current_user, req.pgp_public_key)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "PGP key updated"}


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(req: ForgotPasswordRequest):
    """
    Request password reset.
    - Generates OTP and sends to registered email
    - For DEBUG: OTP is printed to server console
    - Returns email hint for verification
    """
    try:
        return await auth_service.request_password_reset(req.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    """
    Reset password with OTP.
    - Verify OTP
    - Update to new password
    """
    try:
        return await auth_service.reset_password(
            req.username, req.otp, req.new_password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
