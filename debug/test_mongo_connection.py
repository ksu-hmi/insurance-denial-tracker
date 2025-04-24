from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Get the URI from environment variable
uri = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(uri)

try:
    client.server_info()
    print("✅ Connected to MongoDB!")
except Exception as e:
    print("❌ Failed to connect:", e)



