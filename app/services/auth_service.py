from app.db.mongodb import get_database
from app.schemas.auth import RegisterRequest, UserPublicInfo
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    encrypt_email,
)
from datetime import datetime, timedelta


async def register_user(req: RegisterRequest) -> dict:
    """
    Register new user:
    - Store hashed password
    - Store encrypted email
    - Store encrypted birthday
    - Store PGP public key (generated on client)
    """
    db = get_database()

    # Check if username exists
    existing = await db.users.find_one({"username": req.username})
    if existing:
        raise ValueError("Username already taken")

    # Create user document
    user_doc = {
        "username": req.username,
        "email_encrypted": encrypt_email(req.email),
        "birthday_encrypted": encrypt_email(req.birthday),  # Same encryption as email
        "password_hash": hash_password(req.password),
        "pgp_public_key": req.pgp_public_key,
        "is_online": False,
        "last_seen": datetime.utcnow(),
        "created_at": datetime.utcnow(),
    }

    await db.users.insert_one(user_doc)

    # Return JWT token
    token = create_access_token({"sub": req.username})
    return {"access_token": token, "token_type": "bearer", "username": req.username}


async def login_user(username: str, password: str) -> dict:
    """Authenticate user and return JWT. Accepts username or email."""
    db = get_database()

    identifier = username.strip().lower()
    user = None

    # Check if it looks like an email
    if "@" in identifier and "." in identifier and not identifier.startswith("@"):
        # It's an email - encrypt it and search
        encrypted_email = encrypt_email(identifier)
        user = await db.users.find_one({"email_encrypted": encrypted_email})
    else:
        # It's a username - normalize and search
        if not identifier.startswith("@"):
            identifier = f"@{identifier}"
        user = await db.users.find_one({"username": identifier})

    if not user or not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid credentials")

    final_username = user["username"]

    # Update online status
    await db.users.update_one(
        {"username": final_username},
        {"$set": {"is_online": True, "last_seen": datetime.utcnow()}},
    )

    token = create_access_token({"sub": final_username})
    return {"access_token": token, "token_type": "bearer", "username": final_username}


async def get_user_public(username: str) -> UserPublicInfo:
    """Get public info of a user (for key exchange)"""
    db = get_database()

    if not username.startswith("@"):
        username = f"@{username}"

    user = await db.users.find_one({"username": username.lower()})
    if not user:
        raise ValueError("User not found")

    return UserPublicInfo(
        username=user["username"],
        pgp_public_key=user["pgp_public_key"],
        is_online=user.get("is_online", False),
    )


async def search_users(query: str, limit: int = 20) -> list:
    """Search users by username prefix"""
    db = get_database()

    if not query.startswith("@"):
        query = f"@{query}"

    cursor = db.users.find(
        {"username": {"$regex": f"^{query.lower()}", "$options": "i"}},
        {"_id": 0, "username": 1, "pgp_public_key": 1, "is_online": 1},
    ).limit(limit)

    return await cursor.to_list(length=limit)


async def update_pgp_key(username: str, new_key: str) -> bool:
    """Update PGP public key (on reinstall/regenerate)"""
    db = get_database()

    result = await db.users.update_one(
        {"username": username}, {"$set": {"pgp_public_key": new_key}}
    )
    return result.modified_count > 0


async def set_user_offline(username: str):
    """Mark user as offline"""
    db = get_database()
    await db.users.update_one(
        {"username": username},
        {"$set": {"is_online": False, "last_seen": datetime.utcnow()}},
    )


import random
import string


def generate_otp() -> str:
    """Generate 6-digit OTP"""
    return "".join(random.choices(string.digits, k=6))


def get_email_hint(email: str) -> str:
    """Get email hint like 'te***@gmail.com'"""
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        hint = local + "***"
    else:
        hint = local[:2] + "***"
    return f"{hint}@{domain}"


async def request_password_reset(username: str) -> dict:
    """
    Request password reset:
    - Find user by username
    - Decrypt email
    - Generate OTP
    - Store OTP with expiry (10 mins)
    - For debug: log OTP to console
    - Return email hint
    """
    from app.utils.security import decrypt_email

    db = get_database()

    # Normalize username
    if not username.startswith("@"):
        username = f"@{username}"
    username = username.lower()

    user = await db.users.find_one({"username": username})
    if not user:
        raise ValueError("User not found")

    # Decrypt email
    email = decrypt_email(user["email_encrypted"])

    # Generate OTP
    otp = generate_otp()
    otp_expires = datetime.utcnow() + timedelta(minutes=10)

    # Store OTP in database
    await db.users.update_one(
        {"username": username},
        {"$set": {"reset_otp": otp, "reset_otp_expires": otp_expires}},
    )

    # For DEBUG: print OTP to console
    print(f"\n{'='*50}")
    print(f"🔐 PASSWORD RESET OTP for {username}")
    print(f"📧 Email: {email}")
    print(f"🔢 OTP: {otp}")
    print(f"⏰ Expires: {otp_expires}")
    print(f"{'='*50}\n")

    # TODO: In production, send email with OTP
    # await send_email(email, f"Your OTP is: {otp}")

    return {
        "message": "OTP sent to your registered email",
        "email_hint": get_email_hint(email),
    }


async def reset_password(username: str, otp: str, new_password: str) -> dict:
    """
    Reset password with OTP:
    - Verify OTP
    - Update password hash
    - Clear OTP
    """
    db = get_database()

    # Normalize username
    if not username.startswith("@"):
        username = f"@{username}"
    username = username.lower()

    user = await db.users.find_one({"username": username})
    if not user:
        raise ValueError("User not found")

    # Check OTP
    stored_otp = user.get("reset_otp")
    otp_expires = user.get("reset_otp_expires")

    if not stored_otp or not otp_expires:
        raise ValueError("No OTP requested. Please request OTP first.")

    if datetime.utcnow() > otp_expires:
        raise ValueError("OTP expired. Please request a new one.")

    if stored_otp != otp:
        raise ValueError("Invalid OTP")

    # Update password and clear OTP
    await db.users.update_one(
        {"username": username},
        {
            "$set": {"password_hash": hash_password(new_password)},
            "$unset": {"reset_otp": "", "reset_otp_expires": ""},
        },
    )

    return {"message": "Password reset successful. You can now login."}
