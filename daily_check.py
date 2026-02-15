import os
import requests
from notion_client import Client

# 1. Setup
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Renamed to 'client_notion' to be totally unique
client_notion = Client(auth=NOTION_TOKEN)

def get_fridge_summary():
    try:
        response = client_notion.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "Archived", "checkbox": {"equals": False}}
        )
        results = response.get("results", [])
        
        if not results:
            return "Fridge is empty! No leftovers to worry about today."
        
        msg = "Morning Fridge Update:\n"
        for page in results:
            p = page.get("properties", {})
            
            # Extract Food Name
            title_list = p.get("Food", {}).get("title", [])
            food = title_list[0]["text"]["content"] if title_list else "Unknown"
            
            # Extract Days Left
            days = p.get("Days Left", {}).get("formula", {}).get("string", "N/A")
            
            msg += f"- {food}: {days}\n"
        return msg
    except Exception as e:
        return f"Error checking fridge: {str(e)}"

# 3. Send to Phone
topic = "my-fridge-alerts-2026" 
summary = get_fridge_summary()

# THE URL (WITH SLASH)
url = f"https://ntfy.sh/{topic}"

# HEADERS (NO EMOJIS ALLOWED HERE)
headers = {
    "Title": "Fridge Alert",
    "Priority": "high"
}

# SENDING (DATA USES UTF-8 FOR EMOJIS IN THE BODY)
requests.post(url, data=summary.encode('utf-8'), headers=headers)
