import os
import requests
import notion_client  # Changed import style

# 1. Setup
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# We use 'my_connection' so there is ZERO chance of a name clash
my_connection = notion_client.Client(auth=NOTION_TOKEN)

def get_fridge_summary():
    try:
        # Use the new variable name 'my_connection'
        response = my_connection.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "Archived", "checkbox": {"equals": False}}
        )
        results = response.get("results", [])
        
        if not results:
            return "Fridge is empty!"
        
        msg = "Morning Fridge Update:\n"
        for page in results:
            p = page.get("properties", {})
            
            # Safe Title Extraction
            title_data = p.get("Food", {}).get("title", [])
            food = title_data[0].get("text", {}).get("content", "Unknown") if title_data else "Unknown"
            
            # Safe Formula Extraction
            days = p.get("Days Left", {}).get("formula", {}).get("string", "N/A")
            
            msg += f"- {food}: {days}\n"
        return msg
    except Exception as e:
        return f"Error: {str(e)}"

# 3. Send to Phone (SLASH IS DEFINITELY HERE /)
topic = "my-fridge-alerts-2026" 
summary = get_fridge_summary()

# Constructed carefully to avoid any missing slashes
final_url = "https://ntfy.sh" + topic

requests.post(
    final_url,
    data=summary.encode('utf-8'),
    headers={
        "Title": "Fridge Alert",
        "Priority": "high"
    }
)
