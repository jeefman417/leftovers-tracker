import os
import requests
import notion_client

# 1. Setup
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
my_notion = notion_client.Client(auth=NOTION_TOKEN)

def get_fridge_summary():
    try:
        response = my_notion.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "Archived", "checkbox": {"equals": False}}
        )
        results = response.get("results", [])
        
        if not results:
            return "Fridge is empty."
        
        msg = "Fridge Update:\n"
        for page in results:
            p = page.get("properties", {})
            title_content = p.get("Food", {}).get("title", [])
            # Safe text extraction
            food = title_content[0].get("text", {}).get("content", "Unknown") if title_content else "Unknown"
            days = p.get("Days Left", {}).get("formula", {}).get("string", "N/A")
            msg += f"- {food}: {days}\n"
        return msg
    except Exception as e:
        return f"Notion Error: {str(e)}"

# 2. Process
summary = get_fridge_summary()
print(f"Robot output: {summary}")

# 3. Send (Clean URL, Clean Headers, Clean Body)
requests.post(
    "https://ntfy.sh",
    data=summary,
    headers={
        "Title": "Fridge Alert",
        "Priority": "high"
    }
)
