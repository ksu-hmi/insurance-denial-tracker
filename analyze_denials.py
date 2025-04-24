import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load credentials
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client[os.getenv("MONGO_DB")]
collection = db["denials"]

# Fetch all denial records
records = list(collection.find({}))

# Convert to DataFrame
df = pd.DataFrame(records)

# Print columns for verification
print("Columns:", df.columns)

# Optional: Drop MongoDB _id if it exists
df = df.drop(columns=["_id"], errors="ignore")

# Group and Count
print("\n🔍 DataFrame Columns:")
print(df.columns.tolist())

reason_counts = df.groupby("Denial Reason").size().reset_index(name="count")
payer_counts = df.groupby("Payer").size().reset_index(name="count")
status_counts = df.groupby("Appeal Status").size().reset_index(name="count")

# Show result
print("\n📌 Denials by Reason:\n", reason_counts)
print("\n📌 Denials by Payer:\n", payer_counts)
print("\n📌 Denials by Appeal Status:\n", status_counts)

