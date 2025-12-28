"""
Connection Service
Handles connection requests between users
"""

from app.db.mongodb import get_database
from datetime import datetime
from bson import ObjectId


async def send_connection_request(from_user: str, to_user: str) -> dict:
    """Send a connection request from one user to another"""
    db = get_database()

    # Check if users exist
    from_exists = await db.users.find_one({"username": from_user})
    to_exists = await db.users.find_one({"username": to_user})

    if not from_exists or not to_exists:
        raise ValueError("User not found")

    if from_user == to_user:
        raise ValueError("Cannot connect to yourself")

    # Check if request already exists
    existing = await db.connection_requests.find_one(
        {
            "$or": [
                {"from_user": from_user, "to_user": to_user},
                {"from_user": to_user, "to_user": from_user},
            ],
            "status": {"$in": ["pending", "accepted"]},
        }
    )

    if existing:
        if existing["status"] == "accepted":
            raise ValueError("Already connected")
        raise ValueError("Request already pending")

    # Create request
    request = {
        "from_user": from_user,
        "to_user": to_user,
        "status": "pending",
        "created_at": datetime.utcnow(),
    }

    result = await db.connection_requests.insert_one(request)

    return {
        "request_id": str(result.inserted_id),
        "from_user": from_user,
        "to_user": to_user,
        "status": "pending",
        "created_at": request["created_at"].isoformat(),
    }


async def get_pending_requests(username: str) -> list:
    """Get all pending requests for a user (incoming)"""
    db = get_database()

    cursor = db.connection_requests.find({"to_user": username, "status": "pending"})

    requests = []
    async for req in cursor:
        requests.append(
            {
                "request_id": str(req["_id"]),
                "from_user": req["from_user"],
                "to_user": req["to_user"],
                "status": req["status"],
                "created_at": req["created_at"].isoformat(),
            }
        )

    return requests


async def respond_to_request(request_id: str, action: str, username: str) -> dict:
    """Accept or decline a connection request"""
    db = get_database()

    if action not in ["accept", "decline"]:
        raise ValueError("Invalid action")

    # Find request
    try:
        request = await db.connection_requests.find_one(
            {"_id": ObjectId(request_id), "to_user": username, "status": "pending"}
        )
    except:
        raise ValueError("Invalid request ID")

    if not request:
        raise ValueError("Request not found or already processed")

    new_status = "accepted" if action == "accept" else "declined"

    # Update request status
    await db.connection_requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"status": new_status, "responded_at": datetime.utcnow()}},
    )

    return {
        "request_id": request_id,
        "from_user": request["from_user"],
        "to_user": request["to_user"],
        "status": new_status,
    }


async def get_connections(username: str) -> list:
    """Get all accepted connections for a user"""
    db = get_database()

    cursor = db.connection_requests.find(
        {"$or": [{"from_user": username}, {"to_user": username}], "status": "accepted"}
    )

    connections = []
    async for conn in cursor:
        # Get the other user
        other = conn["to_user"] if conn["from_user"] == username else conn["from_user"]

        # Get other user's info
        user_info = await db.users.find_one({"username": other})
        if user_info:
            connections.append(
                {
                    "username": other,
                    "pgp_public_key": user_info.get("pgp_public_key", ""),
                    "is_online": user_info.get("is_online", False),
                    "connected_at": conn.get(
                        "responded_at", conn["created_at"]
                    ).isoformat(),
                }
            )

    return connections


async def remove_connection(username: str, other_user: str) -> bool:
    """Remove a connection between users"""
    db = get_database()

    result = await db.connection_requests.delete_one(
        {
            "$or": [
                {"from_user": username, "to_user": other_user},
                {"from_user": other_user, "to_user": username},
            ],
            "status": "accepted",
        }
    )

    return result.deleted_count > 0
