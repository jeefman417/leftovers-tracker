import os
import requests
import notion_client

# 1. Setup Notion
# Using 'notion_bot' to avoid the DatabasesEndpoint error
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
notion_bot = notion_client.Client(auth=NOTION_TOKEN)

def get_fridge_summary():
    try:
        response = notion_bot.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "Archived", "checkbox": {"equals": False}}
        )
        results = response.get("results", [])
        
        if not results:
            return "Fridge is empty! No leftovers to track."
        
        msg = "Morning Fridge Update:\n"
        for page in results:
            p = page.get("properties", {})
            # Extract Food Name
            title_list = p.get("Food", {}).get("title", [])
            food = title_list[0].get("text", {}).get("content", "Unknown") if title_list else "Unknown"
            # Extract Days Left
            days = p.get("Days Left", {}).get("formula", {}).get("string", "N/A")
            msg += f"- {food}: {days}\n"
        return msg
    except Exception as e:
        return f"Notion Error: {str(e)}"

# 2. Get Data
summary = get_fridge_summary()
print(f"Robot output: {summary}")

# 3. Send to Phone (HARD-CODED URL WITH SLASH)
requests.post(
    "https://ntfy.sh",
    data=summary.encode('utf-8'),
    headers={
        "Title": "Fridge Alert",
        "Priority": "high"
    }
)
