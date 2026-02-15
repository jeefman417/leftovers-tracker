import os
import requests
from notion_client import Client

# 1. Setup Notion
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=NOTION_TOKEN)

# 2. Query the Fridge
def get_fridge_summary():
    try:
        results = notion.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "Archived", "checkbox": {"equals": False}}
        ).get("results")
        
        if not results:
            return "🧊 Your fridge is empty! No leftovers to worry about today."
        
        msg = "🍱 Morning Fridge Update:\n"
        for page in results:
            p = page["properties"]
            # Get Food Name
            food = p["Food"]["title"][0]["text"]["content"] if p["Food"]["title"] else "Unknown"
            # Get Days Left (this is the formula we built)
            days = p["Days Left"]["formula"]["string"] if "Days Left" in p else "N/A"
            msg += f"- {food}: {days}\n"
        return msg
    except Exception as e:
        return f"❌ Error checking fridge: {str(e)}"

# 3. Send to Phone via ntfy.sh (FREE)
# Replace 'my-fridge-alerts-2026' with something very unique to you!
topic = "my-fridge-alerts-2026" 
summary = get_fridge_summary()

requests.post(f"https://ntfy.sh/{topic}",
    data=summary.encode('utf-8'),
    headers={
        "Title": "Fridge Alert 🧊",
        "Priority": "high",
        "Tags": "plate_with_cutlery"
    }
)
