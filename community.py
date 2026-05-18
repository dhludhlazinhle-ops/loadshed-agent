from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime
import json

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["loadshed_agent"]

CONFIG_FILE = "user_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def get_user(username):
    return db.users.find_one({"username": username})

def post_report(username, area, message, report_type):
    db.community.insert_one({
        "username": username,
        "area": area,
        "message": message,
        "type": report_type,
        "status": "active",
        "votes": 0,
        "created_at": datetime.now()
    })
    print(f"\nReport posted successfully!")
    print(f"Your {area} community will see this.")

def get_community_reports(area):
    reports = list(db.community.find(
        {"area": area, "status": "active"},
        sort=[("created_at", -1)],
        limit=10
    ))
    return reports

def mark_resolved(report_id):
    from bson import ObjectId
    db.community.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": {"status": "resolved"}}
    )
    print("Report marked as resolved!")

def display_reports(area):
    reports = get_community_reports(area)
    print("\n" + "=" * 50)
    print(f"COMMUNITY BOARD - {area.upper()}")
    print("=" * 50)

    if not reports:
        print("No active reports in your area. All clear!")
    else:
        print(f"{len(reports)} active report(s):\n")
        for i, r in enumerate(reports, 1):
            time = r["created_at"].strftime("%H:%M")
            date = r["created_at"].strftime("%Y-%m-%d")
            print(f"{i}. [{r['type'].upper()}] {r['message']}")
            print(f"   Posted by: {r['username'].title()} at {time} on {date}")
            print(f"   Status: {r['status']}")
            print()
    print("=" * 50)

def run_community_board():
    config = load_config()

    if not config:
        print("Please run user_profile.py first to set up your profile!")
        return

    username = config["username"]
    user = get_user(username)

    if not user:
        print("User profile not found. Please run user_profile.py first!")
        return

    area = user["area"]

    print("\n" + "=" * 50)
    print(f"COMMUNITY BOARD - {area.upper()}")
    print(f"Logged in as: {username.title()}")
    print("=" * 50)

    while True:
        print("\nWhat would you like to do?")
        print("1. View community reports")
        print("2. Report cable theft")
        print("3. Report transformer fault")
        print("4. Report unplanned outage")
        print("5. Post councillor update")
        print("6. Report power restored")
        print("7. Exit")

        choice = input("\nEnter choice (1-7): ").strip()

        if choice == "1":
            display_reports(area)

        elif choice == "2":
            display_reports(area)
            location = input("Where exactly? (e.g. near Masimini section): ").strip()
            if location:
                post_report(
                    username,
                    area,
                    f"Cable theft reported near {location}",
                    "cable_theft"
                )

        elif choice == "3":
            location = input("Where is the transformer fault?: ").strip()
            if location:
                post_report(
                    username,
                    area,
                    f"Transformer fault at {location}",
                    "transformer_fault"
                )

        elif choice == "4":
            details = input("Describe the outage: ").strip()
            if details:
                post_report(username, area, details, "unplanned_outage")

        elif choice == "5":
            update = input("Enter your official update: ").strip()
            if update:
                post_report(
                    username,
                    area,
                    f"[OFFICIAL] {update}",
                    "councillor_update"
                )

        elif choice == "6":
            section = input("Which section has power restored?: ").strip()
            if section:
                post_report(
                    username,
                    area,
                    f"Power restored in {section}",
                    "power_restored"
                )

        elif choice == "7":
            print(f"\nStay safe {username.title()}!")
            break

        else:
            print("Invalid choice. Please enter 1-7.")

run_community_board()