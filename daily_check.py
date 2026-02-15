import os
from notion_client import Client

# Initialize Notion
notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def get_fridge_summary():
    results = notion.databases.query(
        database_id=DATABASE_ID,
        filter={"property": "Archived", "checkbox": {"equals": False}}
    ).get("results")
    
    if not results:
        return "🧊 Fridge is empty! No leftovers to worry about today."
    
    msg = "🍱 Morning Fridge Update:\n"
    for page in results:
        p = page["properties"]
        food = p["Food"]["title"][0]["text"]["content"]
        days = p["Days Left"]["formula"]["string"]
        status = p["Status"]["formula"]["string"]
        msg += f"- {food}: {status} ({days})\n"
    return msg

# Code to send 'msg' to your notification service goes here
