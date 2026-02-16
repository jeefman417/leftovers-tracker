import os
import requests
from notion_client import Client

# 1. Setup
token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")
po_user = os.getenv("PUSHOVER_USER_KEY")
po_token = os.getenv("PUSHOVER_API_TOKEN")

client = Client(auth=token)

# 2. Raw Request (Bypassing the 'databases' attribute entirely)
# This hits the endpoint directly to avoid the 'DatabasesEndpoint' error
response = client.request(
    path=f"databases/{db_id}/query",
    method="POST",
    body={
        "filter": {"property": "Archived", "checkbox": {"equals": False}}
    }
)
results = response.get("results", [])

# 3. Build Message
if not results:
    msg = "Fridge is empty!"
else:
    msg = "🍱 Fridge Update:\n"
    for page in results:
        p = page["properties"]
        # Safe extraction for Notion's list-based title structure
        food_list = p.get("Food", {}).get("title", [])
        food = food_list[0]["text"]["content"] if food_list else "Unknown"
        
        # Safe extraction for formula string
        days = p.get("Days Left", {}).get("formula", {}).get("string", "N/A")
        msg += f"- {food}: {days}\n"

print(f"Final Message: {msg}")

# 4. Send to Pushover
requests.post("https://api.pushover.net", data={
    "token": po_token,
    "user": po_user,
    "message": msg,
    "title": "Fridge Alert",
    "priority": 1
})
