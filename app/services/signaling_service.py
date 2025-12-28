from app.db.mongodb import get_database
from app.schemas.signaling import SignalSendRequest, SignalMessage
from app.config import settings
from datetime import datetime, timedelta
from typing import List


async def send_signal(from_user: str, req: SignalSendRequest) -> bool:
    """
    Store signaling message for recipient.
    Server CANNOT read encrypted_payload - it's PGP encrypted by client.
    """
    db = get_database()

    # Normalize recipient username
    to_user = req.to_user
    if not to_user.startswith("@"):
        to_user = f"@{to_user}"
    to_user = to_user.lower()

    # Create signal document with TTL
    signal_doc = {
        "from_user": from_user,
        "to_user": to_user,
        "type": req.type,
        "encrypted_payload": req.encrypted_payload,  # Server can't read this
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow()
        + timedelta(seconds=settings.SIGNAL_EXPIRE_SECONDS),
    }

    await db.signaling.insert_one(signal_doc)
    return True


async def poll_signals(username: str) -> List[SignalMessage]:
    """
    Get pending signals for user and delete them.
    Returns PGP-encrypted payloads that only the client can decrypt.
    """
    db = get_database()

    # Find all pending signals for this user
    cursor = db.signaling.find(
        {"to_user": username},
        {"_id": 1, "from_user": 1, "type": 1, "encrypted_payload": 1, "created_at": 1},
    ).sort("created_at", 1)

    signals = await cursor.to_list(length=100)

    if signals:
        # Delete fetched signals
        signal_ids = [s["_id"] for s in signals]
        await db.signaling.delete_many({"_id": {"$in": signal_ids}})

    return [
        SignalMessage(
            from_user=s["from_user"],
            type=s["type"],
            encrypted_payload=s["encrypted_payload"],
            timestamp=s["created_at"].isoformat(),
        )
        for s in signals
    ]


async def clear_signals(username: str) -> int:
    """Clear all pending signals for/from a user"""
    db = get_database()

    result = await db.signaling.delete_many(
        {"$or": [{"to_user": username}, {"from_user": username}]}
    )
    return result.deleted_count
