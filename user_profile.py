from dotenv import load_dotenv
import os
from pymongo import MongoClient
from groq import Groq
from datetime import datetime
import json

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["loadshed_agent"]
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CONFIG_FILE = "user_config.json"

def save_config(username):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"username": username}, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def get_user(username):
    return db.users.find_one({"username": username})

def save_user(username, area):
    db.users.update_one(
        {"username": username},
        {"$set": {
            "username": username,
            "area": area,
            "updated_at": datetime.now()
        }},
        upsert=True
    )
    print(f"Location saved: {area}")

def get_schedule(area, date):
    schedule = db.schedules.find_one({"area": area, "date": date})
    if schedule:
        return schedule["outages"], schedule["stage"]
    return [], None

def ask_ai(messages):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return response.choices[0].message.content

def morning_briefing(username, area, date):
    outages, stage = get_schedule(area, date)
    print("\n" + "=" * 50)
    print(f"GOOD MORNING {username.title()}!")
    print("LOAD SHED SMART DAILY BRIEFING")
    print("=" * 50)
    print(f"Area: {area}")
    print(f"Date: {date}")

    if not outages:
        print("No load shedding today! Full power all day!")
        print("Make the most of it!\n")
    else:
        print(f"Stage {stage} load shedding today!")
        print("Power OFF during:")
        for o in outages:
            print(f"   - {o['start']} - {o['end']}")
        prompt = f"""Give a short 2 sentence morning briefing for {username} in {area}
        South Africa. Load shedding stage {stage} today at these times: {outages}.
        Address them by first name. Be warm, practical and encouraging. Very brief!"""
        briefing = ask_ai([{"role": "user", "content": prompt}])
        print(f"\n{briefing}")
    print("=" * 50 + "\n")

def run_smart_agent():
    print("\n" + "=" * 50)
    print("LOAD SHED SMART - SA Productivity Agent")
    print("=" * 50)

    config = load_config()

    if config:
        username = config["username"]
        user = get_user(username)
        if user:
            area = user["area"]
            print(f"\nWelcome back {username.title()}!")
            print(f"Your area: {area}\n")
        else:
            area = input("What area are you in?: ").strip()
            save_user(username, area)
    else:
        print("\nWelcome to Load Shed Smart!")
        username = input("What is your name?: ").strip()
        area = input("What area are you in?: ").strip()
        save_config(username)
        save_user(username, area)
        print(f"\nAll set {username.title()}! I will remember you from now on.")

    date = datetime.now().strftime("%Y-%m-%d")
    morning_briefing(username, area, date)

    conversation = [
        {
            "role": "system",
            "content": f"""You are Load Shed Smart, a helpful AI for South Africans
            dealing with load shedding. The user's name is {username},
            they live in {area}. Today is {date}.
            Load shedding schedule: {get_schedule(area, date)}.
            Greet them by name naturally. Help plan tasks around power outages.
            Be friendly, warm and brief."""
        }
    ]

    print("Chat with Load Shed Smart\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            print(f"\nHave a productive day {username.title()}!")
            break

        if "change location" in user_input.lower():
            new_area = input("Enter your new area: ").strip()
            if new_area.lower() == "quit" or not new_area:
                print("Invalid area. Location not changed.")
            else:
                save_user(username, new_area)
                area = new_area
                print(f"Location updated to {area}!")
            continue

        if "change name" in user_input.lower():
            new_name = input("Enter your new name: ").strip()
            if new_name.lower() == "quit" or not new_name:
                print("Invalid name. Name not changed.")
            else:
                save_config(new_name)
                save_user(new_name, area)
                username = new_name
                print(f"Name updated to {username.title()}!")
            continue

        if not user_input:
            continue

        conversation.append({"role": "user", "content": user_input})
        print("Thinking...")
        response = ask_ai(conversation)
        conversation.append({"role": "assistant", "content": response})
        print(f"\nAgent: {response}\n")

run_smart_agent()