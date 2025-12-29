"""MongoDB database connection using Motor (async driver)."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings


class Database:
    """Database connection manager."""

    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    @classmethod
    async def connect_db(cls):
        """Initialize database connection on startup."""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.db = cls.client[settings.DATABASE_NAME]
        print(f"✓ Connected to MongoDB: {settings.DATABASE_NAME}")

    @classmethod
    async def close_db(cls):
        """Close database connection on shutdown."""
        if cls.client:
            cls.client.close()
            print("✓ Closed MongoDB connection")

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a collection from the database."""
        return cls.db[collection_name]


# Collection references
def get_videos_collection():
    """Get the videos collection."""
    return Database.get_collection("videos")


async def create_indexes():
    """Create database indexes for better performance."""
    videos = get_videos_collection()

    # Create indexes
    await videos.create_index("status")
    await videos.create_index("upload_timestamp")
    await videos.create_index([("upload_timestamp", -1)])  # Descending for recent first

    print("✓ Created database indexes")
