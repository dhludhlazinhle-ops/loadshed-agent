from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["loadshed_agent"]
db.users.delete_many({})
print("Users cleared!")