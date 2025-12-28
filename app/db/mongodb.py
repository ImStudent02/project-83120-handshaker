from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings


class MongoDB:
    """MongoDB connection manager"""

    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


db = MongoDB()


async def connect_db():
    """Initialize database connection and indexes"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.DATABASE_NAME]

    # Create indexes
    await db.db.users.create_index("username", unique=True)

    # TTL index for auto-expiring signals
    await db.db.signaling.create_index("expires_at", expireAfterSeconds=0)
    await db.db.signaling.create_index("to_user")

    print(f"Connected to MongoDB: {settings.DATABASE_NAME}")


async def close_db():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db.db
