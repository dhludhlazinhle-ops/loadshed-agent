from dotenv import load_dotenv
import os
from pymongo import MongoClient
from groq import Groq
from datetime import datetime

load_dotenv()

# Connect to MongoDB and Groq
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["loadshed_agent"]
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_loadshedding_schedule(area, date):
    schedule = db.schedules.find_one({"area": area, "date": date})
    if schedule:
        return schedule["outages"]
    return []

def check_conflict(task_time, outages):
    for outage in outages:
        start = outage["start"]
        end = outage["end"]
        if start <= task_time <= end:
            return True, start, end
    return False, None, None

def ask_ai(prompt):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def run_agent(task_name, task_time, area, date):
    print(f"\nChecking schedule for {area} on {date}...")
    outages = get_loadshedding_schedule(area, date)
    
    if not outages:
        print("No load shedding scheduled!")
        return
    
    print(f"⚡ Load shedding times: {outages}")
    has_conflict, start, end = check_conflict(task_time, outages)
    
    if has_conflict:
        print(f"Conflict! '{task_name}' at {task_time} clashes with outage {start}-{end}")
        prompt = f"""
        A South African user has a task called '{task_name}' scheduled at {task_time}.
        There is load shedding from {start} to {end} in {area}.
        Suggest 2 alternative times to do this task and explain why briefly.
        Keep your response short and practical.
        """
        suggestion = ask_ai(prompt)
        print(f"\nAI Suggestion:\n{suggestion}")
        
        db.tasks.insert_one({
            "title": task_name,
            "scheduled_time": task_time,
            "area": area,
            "date": date,
            "status": "rescheduled",
            "conflict": f"{start}-{end}",
            "created_at": datetime.now()
        })
        print("\nTask saved to database!")
    else:
        print(f"No conflict! '{task_name}' at {task_time} is safe to do!")

# Run the agent!
run_agent(
    task_name="Study for exam",
    task_time="10:30",
    area="Benoni",
    date="2026-05-18"
)