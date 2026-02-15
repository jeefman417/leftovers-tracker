import os
import requests
from notion_client import Client

# 1. Setup
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# We name this 'fridge_bot' so it doesn't clash with the library name
fridge_bot = Client(auth=NOTION_TOKEN)

def get_fridge_summary():
    try:
        # Use the specific 'fridge_bot' connection
        response = fridge_bot.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "Archived", "checkbox": {"equals": False}}
        )
        results = response.get("results", [])
        
        if not results:
            return "Fridge is empty."
        
        msg = "Fridge Update:\n"
        for page in results:
            p = page.get("properties", {})
            
            # Notion Title extraction
            title_list = p.get("Food", {}).get("title", [])
            food = title_list[0].get("text", {}).get("content", "Unknown") if title_list else "Unknown"
            
            # Notion Formula extraction
            days = p.get("Days Left", {}).get("formula", {}).get("string", "N/A")
            
            msg += f"- {food}: {days}\n"
        return msg
    except Exception as e:
        return f"Notion Error: {str(e)}"

# 2. Process
summary = get_fridge_summary()
print(f"Robot output: {summary}")

# 3. Send to Phone (SLASH INCLUDED)
# Verify ntfy app is subscribed to: my-fridge-alerts-2026
requests.post(
    "https://ntfy.sh",
    data=summary,
    headers={
        "Title": "Fridge Alert",
        "Priority": "high"
    }
)
