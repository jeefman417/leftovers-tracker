import os
import requests
from notion_client import Client

# 1. Setup
token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")
po_user = os.getenv("PUSHOVER_USER_KEY")
po_token = os.getenv("PUSHOVER_API_TOKEN")

# Initialize the client
notion = Client(auth=token)

# 2. Query (Using the keyword-only argument style)
try:
    response = notion.databases.query(
        database_id=db_id,
        filter={
            "property": "Archived",
            "checkbox": {
                "equals": False
            }
        }
    )
    results = response.get("results", [])

    if not results:
        msg = "Fridge is empty! No leftovers to track."
    else:
        msg = "🍱 Fridge Update:\n"
        for page in results:
            p = page.get("properties", {})
            
            # Safe extraction for Title
            food_title_list = p.get("Food", {}).get("title", [])
            food = food_title_list[0].get("text", {}).get("content", "Unknown") if food_title_list else "Unknown"
            
            # Safe extraction for Formula
            days = p.get("Days Left", {}).get("formula", {}).get("string", "N/A")
            
            msg += f"- {food}: {days}\n"

except Exception as e:
    msg = f"❌ Notion Error: {str(e)}"

print(f"Final Message: {msg}")

# 3. Send to Pushover
requests.post("https://api.pushover.net", data={
    "token": po_token,
    "user": po_user,
    "message": msg,
    "title": "Fridge Alert 🧊",
    "priority": 1
})
