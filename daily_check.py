import os
import requests
import notion_client

# 1. Setup Notion
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Using a unique variable name to avoid the 'DatabasesEndpoint' error
my_notion_connection = notion_client.Client(auth=NOTION_TOKEN)

def get_fridge_summary():
    try:
        response = my_notion_connection.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "Archived", "checkbox": {"equals": False}}
        )
        results = response.get("results", [])
        
        if not results:
            return "Fridge is empty! No leftovers to worry about today."
        
        msg = "Morning Fridge Update:\n"
        for page in results:
            p = page.get("properties", {})
            
            # Safe Title Extraction (Notion titles are lists)
            title_list = p.get("Food", {}).get("title", [])
            food = title_list[0].get("text", {}).get("content", "Unknown") if title_list else "Unknown"
            
            # Safe Formula Extraction
            days = p.get("Days Left", {}).get("formula", {}).get("string", "N/A")
            
            msg += f"- {food}: {days}\n"
        return msg
    except Exception as e:
        return f"Error checking fridge: {str(e)}"

# 2. Get the message
summary_message = get_fridge_summary()

# 3. Send to Phone (Fixed URL with absolute path)
# I typed the full URL here manually to ensure the slash is included
final_url = "https://ntfy.sh"

requests.post(
    final_url,
    data=summary_message.encode('utf-8'),
    headers={
        "Title": "Fridge Alert",
        "Priority": "high"
    }
)
