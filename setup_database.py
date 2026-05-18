from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["loadshed_agent"]

# Collection 1 — Tasks
db.tasks.insert_one({
    "title": "Study for exam",
    "priority": "high",
    "duration_hours": 2,
    "requires_electricity": True,
    "status": "pending",
    "scheduled_time": "14:00",
    "date": "2026-05-18",
    "area": "Benoni",
    "created_at": datetime.now()
})

# Collection 2 — Load Shedding Schedules
db.schedules.insert_one({
    "area": "Benoni",
    "stage": 2,
    "date": "2026-05-18",
    "outages": [
        {"start": "10:00", "end": "12:30"},
        {"start": "18:00", "end": "20:30"}
    ]
})

# Collection 3 — Productivity Stats
db.stats.insert_one({
    "area": "Benoni",
    "date": "2026-05-18",
    "hours_lost": 5,
    "tasks_completed": 3,
    "tasks_missed": 2,
    "created_at": datetime.now()
})

# Benoni schedule
db.schedules.insert_one({
    "area": "Benoni",
    "stage": 2,
    "date": "2026-05-19",
    "outages": [
        {"start": "06:00", "end": "08:30"},
        {"start": "14:00", "end": "16:30"},
        {"start": "22:00", "end": "00:30"}
    ]
})

# Kwa-Thema schedule
db.schedules.insert_one({
    "area": "Kwa-Thema",
    "stage": 2,
    "date": "2026-05-19",
    "outages": [
        {"start": "06:00", "end": "08:30"},
        {"start": "14:00", "end": "16:30"},
        {"start": "22:00", "end": "00:30"}
    ]
})

# ext2 schedule
db.schedules.insert_one({
    "area": "ext2",
    "stage": 3,
    "date": "2026-05-19",
    "outages": [
        {"start": "08:00", "end": "10:30"},
        {"start": "16:00", "end": "18:30"}
    ]
})

print("Tasks collection created!")
print("Schedules collection created!")
print("Stats collection created!")
print("Database setup complete!")