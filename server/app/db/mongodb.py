from pymongo import AsyncMongoClient

class DatabaseManager:
    def __init__(self):
        self.client: AsyncMongoClient = None
        self.db = None

    async def connect_to_mongo(self, uri: str, db_name: str):
        self.client = AsyncMongoClient(uri, maxPoolSize=10, minPoolSize=10)
        self.db = self.client[db_name]
        print("Connected to MongoDB")

    async def close_mongo_connection(self):
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")

# Global instance to be used across the app
db_manager = DatabaseManager()