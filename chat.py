from dotenv import load_dotenv
import os
from pymongo import MongoClient
from groq import Groq
from datetime import datetime

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["loadshed_agent"]
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_schedule(area, date):
    schedule = db.schedules.find_one({"area": area, "date": date})
    if schedule:
        return schedule["outages"]
    return []

def save_task(title, time, area, date, status, conflict=None):
    db.tasks.insert_one({
        "title": title,
        "scheduled_time": time,
        "area": area,
        "date": date,
        "status": status,
        "conflict": conflict,
        "created_at": datetime.now()
    })

def ask_ai(messages):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return response.choices[0].message.content

def run_chat():
    print("=" * 50)
    print("⚡ LOAD SHED SMART — SA Productivity Agent")
    print("=" * 50)
    print("I help you plan around load shedding!")
    print("Type 'quit' to exit\n")

    area = input("What area are you in? (e.g. Benoni): ").strip()
    date = input("What date? (e.g. 2026-05-18): ").strip()

    outages = get_schedule(area, date)
    if outages:
        print(f"\n⚡ Load shedding in {area} on {date}:")
        for o in outages:
            print(f"   • {o['start']} - {o['end']}")
    else:
        print(f"\nNo load shedding found for {area} on {date}")

    conversation = [
        {
            "role": "system",
            "content": f"""You are Load Shed Smart, a helpful AI assistant for South Africans 
            dealing with load shedding. The user is in {area} on {date}.
            Load shedding times: {outages if outages else 'None scheduled'}.
            Help them plan their tasks around power outages.
            Be friendly, practical and brief. Always suggest alternative times when there's a conflict."""
        }
    ]

    print("\nChat with your agent! Ask me anything.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            print("\nStay productive, load shedding won't stop you!")
            break
        if not user_input:
            continue

        conversation.append({"role": "user", "content": user_input})
        print("Thinking...")
        response = ask_ai(conversation)
        conversation.append({"role": "assistant", "content": response})
        print(f"\nAgent: {response}\n")

run_chat()