from dotenv import load_dotenv
import os
from pymongo import MongoClient
from groq import Groq
from datetime import datetime

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["loadshed_agent"]
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_morning_briefing(area, date):
    print("\n" + "=" * 50)
    print("GOOD MORNING — LOAD SHED SMART BRIEFING")
    print("=" * 50)
    print(f"Area: {area}")
    print(f"Date: {date}\n")

    # Get today's load shedding
    schedule = db.schedules.find_one({"area": area, "date": date})
    
    if not schedule:
        print("Great news! No load shedding scheduled today!")
        print("You have a full day of power. Make it count!\n")
        return

    outages = schedule["outages"]
    stage = schedule["stage"]
    
    print(f"Stage {stage} load shedding today!")
    print("Power will be OFF during these times:")
    for o in outages:
        print(f"   • {o['start']} - {o['end']}")

    # Get today's tasks
    tasks = list(db.tasks.find({"area": area, "date": date}))
    
    conflicts = []
    safe_tasks = []
    
    for task in tasks:
        task_time = task.get("scheduled_time", "")
        for o in outages:
            if o["start"] <= task_time <= o["end"]:
                conflicts.append(task)
                break
        else:
            safe_tasks.append(task)

    # Show conflicts
    if conflicts:
        print(f"\n{len(conflicts)} task(s) affected by load shedding:")
        for task in conflicts:
            print(f"   {task['title']} at {task['scheduled_time']}")
    
    if safe_tasks:
        print(f"\n{len(safe_tasks)} task(s) safe to do:")
        for task in safe_tasks:
            print(f"   ✓ {task['title']} at {task['scheduled_time']}")

    # Ask AI for full briefing
    prompt = f"""
    Good morning! Give a helpful 3-sentence morning briefing for someone in {area}.
    Today is {date}. Load shedding stage {stage} is scheduled.
    Power will be off at these times: {outages}.
    These tasks are affected: {[t['title'] for t in conflicts]}.
    Be encouraging, practical and South African in tone.
    End with one productivity tip for load shedding days.
    """
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    print(f"\nYour AI Briefing:\n")
    print(response.choices[0].message.content)
    print("\n" + "=" * 50)

# Run morning briefing
today = datetime.now().strftime("%Y-%m-%d")
get_morning_briefing("Kwa-Thema", "2026-05-19")