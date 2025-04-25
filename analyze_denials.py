import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["insurance_denials"]
collection = db["denials"]

data = list(collection.find())
df = pd.DataFrame(data)

# Remove MongoDB ObjectID if it exists
if "_id" in df.columns:
    df = df.drop(columns=["_id"])

print("\n🔍 DataFrame Columns:")
print(df.columns)

# Basic summaries
if not df.empty:
    if "Denial Reason" in df.columns:
        print("\n📊 Denials by Reason:")
        print(df["Denial Reason"].value_counts())

    if "Patient Name" in df.columns:
        print("\n🧍 Denials by Patient:")
        print(df["Patient Name"].value_counts())

    if "Denied Cost" in df.columns:
        df["Denied Cost"] = pd.to_numeric(df["Denied Cost"], errors="coerce")
        print("\n💸 Total Denied Amount:", df["Denied Cost"].sum())

    if "Total Claim Cost" in df.columns:
        df["Total Claim Cost"] = pd.to_numeric(df["Total Claim Cost"], errors="coerce")
        print("\n💰 Average Total Claim Cost:", df["Total Claim Cost"].mean())
else:
    print("\n⚠️ No data available to analyze.")


