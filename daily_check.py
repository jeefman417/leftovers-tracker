import os
import requests
from notion_client import Client

# 1. Setup Notion
# Using 'bot_client' to avoid any naming conflicts with the library
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
bot_client = Client(auth=NOTION_TOKEN)

def get_fridge_summary():
    try:
        # Query for items that are NOT archived
        response = bot_client.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "Archived", "checkbox": {"equals": False}}
        )
        results = response.get("results", [])
        
        if not results:
            return "Your fridge is currently empty! No leftovers to track."
        
        msg = "🍱 Morning Fridge Update:\n"
        for page in results:
            p = page.get("properties", {})
            
            # Extract Food Name (Handling the Notion list structure)
            title_list = p.get("Food", {}).get("title", [])
            food = title_list[0].get("text", {}).get("content", "Unknown") if title_list else "Unknown Food"
            
            # Extract Days Left (From your Notion formula)
            days = p.get("Days Left", {}).get("formula", {}).get("string", "N/A")
            
            msg += f"- {food}: {days}\n"
        return msg
    except Exception as e:
        return f"Error checking Notion: {str(e)}"

# 2. Generate the message
summary = get_fridge_summary()

# 3. Print to GitHub Logs (for debugging)
print("--- ROBOT OUTPUT ---")
print(summary)

# 4. Send to Phone via ntfy.sh
# Note: Emojis are safe in the body (data), but kept out of the Title/Headers
topic = "my-fridge-alerts-2026" 
url = f"https://ntfy.sh/{topic}"

try:
    requests.post(
        url,
        data=summary.encode('utf-8'),
        headers={
            "Title": "Fridge Alert",
            "Priority": "high"
        }
    )
    print("--- NOTIFICATION SENT ---")
except Exception as e:
    print(f"--- FAILED TO SEND NOTIFICATION: {e} ---")
