import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
collection = db["denials"]

# Fetch all denial records
records = list(collection.find())

# Convert to DataFrame
df = pd.DataFrame(records)

# Drop MongoDB's automatic ID field if it exists
if "_id" in df.columns:
    df.drop(columns=["_id"], inplace=True)

# Display main DataFrame
print("\n--- Denials Data ---\n")
print(df.head())

# Summary statistics
summary = {
    "Total Records": len(df),
    "Average Total Claim Cost": df["total_claim_cost"].mean(),
    "Average Denied Cost": df["denied_cost"].mean(),
    "Total Denied Cost": df["denied_cost"].sum(),
    "Denials by Payer": df["payer"].value_counts().to_dict(),
    "Denials by Reason": df["denial_reason"].value_counts().to_dict(),
    "Appeal Status Counts": df["appeal_status"].value_counts().to_dict()
}

print("\n--- Summary Statistics ---\n")
for key, value in summary.items():
    print(f"{key}: {value}")



