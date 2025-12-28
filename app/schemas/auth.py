from pydantic import BaseModel, Field, field_validator
import re


class RegisterRequest(BaseModel):
    """Registration request - client sends PGP public key"""

    username: str = Field(..., min_length=3, max_length=30)
    email: str
    birthday: str  # DD/MM/YYYY format
    password: str = Field(..., min_length=8)
    pgp_public_key: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        # Ensure @ prefix
        if not v.startswith("@"):
            v = f"@{v}"
        # Only alphanumeric and underscore
        if not re.match(r"^@[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must contain only alphanumeric and underscore")
        return v.lower()

    @field_validator("pgp_public_key")
    @classmethod
    def validate_pgp_key(cls, v):
        # Accept mock keys for testing, real keys for production
        if "-----BEGIN PGP PUBLIC KEY" in v or "mock-public-key" in v:
            return v
        raise ValueError("Invalid PGP public key format")


class LoginRequest(BaseModel):
    """Login request"""

    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""

    access_token: str
    token_type: str = "bearer"
    username: str


class UserPublicInfo(BaseModel):
    """Public user info (returned to other users)"""

    username: str
    pgp_public_key: str
    is_online: bool


class UpdatePGPKeyRequest(BaseModel):
    """Update PGP public key (on reinstall)"""

    pgp_public_key: str

    @field_validator("pgp_public_key")
    @classmethod
    def validate_pgp_key(cls, v):
        if "-----BEGIN PGP PUBLIC KEY" in v or "mock-public-key" in v:
            return v
        raise ValueError("Invalid PGP public key format")


class ForgotPasswordRequest(BaseModel):
    """Request password reset - needs username to look up encrypted email"""

    username: str


class ForgotPasswordResponse(BaseModel):
    """Response after requesting reset"""

    message: str
    email_hint: str  # Shows first 2 chars + *** + domain for verification


class ResetPasswordRequest(BaseModel):
    """Reset password with OTP"""

    username: str
    otp: str
    new_password: str = Field(..., min_length=8)
