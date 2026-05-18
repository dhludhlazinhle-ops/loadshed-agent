from dotenv import load_dotenv
import os
from pymongo import MongoClient
from groq import Groq

load_dotenv()

# Test MongoDB
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["loadshed_agent"]
print("MongoDB connected!")

# Test Groq AI
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
response = groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say hello to Load Shed Smart!"}]
)
print("AI connected!")
print(response.choices[0].message.content)