import streamlit as st
import notion_client
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Leftovers Tracker", page_icon="🍱", layout="wide")

# Notion API Setup
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID", "your-database-id-here")

# Initialize Notion client
try:
    if not NOTION_TOKEN:
        st.error("❌ NOTION_TOKEN not set in environment variables")
        st.stop()
    elif not (NOTION_TOKEN.startswith("secret_") or NOTION_TOKEN.startswith("ntn_")):
        st.error("❌ NOTION_TOKEN should start with 'secret_' or 'ntn_'")
        st.stop()
    else:
        notion = notion_client.Client(auth=NOTION_TOKEN)
        st.success("✅ Notion connected successfully!")
except Exception as e:
    st.error(f"❌ Notion connection failed: {str(e)}")
    st.stop()

def add_leftover(food_name, expires_days, location, added_by, notes="", photo_file=None):
    """Add new leftover to Notion database"""
    try:
        expires_date = (datetime.now() + timedelta(days=expires_days)).isoformat()
        
        # Build properties dictionary
        properties = {
            "Food": {"title": [{"text": {"content": food_name}}]},
            "Date Added": {"date": {"start": datetime.now().isoformat()}},
            "Expires": {"date": {"start": expires_date}},
            "Days Left": {"number": expires_days},
            "Status": {"select": {"name": "Fresh"}},
            "Location": {"rich_text": [{"text": {"content": location}}]},
            "Added By": {"select": {"name": added_by}},
            "Notes": {"rich_text": [{"text": {"content": notes}}]}
        }
        
        # Add photo if provided
        if photo_file is not None:
            try:
                # Upload photo to Notion
                with photo_file as file:
                    file_content = file.read()
                
                # Create file in Notion
                notion_file = notion.files.upload({
                    "purpose": "inline",
                    "file": file_content
                })
                
                # Add photo to properties
                properties["Photo"] = {"files": [{"name": photo_file.name, "type": "file", "file": {"url": notion_file["url"]}}]}
            except Exception as photo_error:
                st.warning(f"Photo upload failed: {photo_error}")
        
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties=properties
        )
        return True, "Leftover added successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_leftovers():
    """Get all leftovers from Notion"""
    try:
        # Use the correct method for current notion-client version
        response = notion.databases.query(
            **{"database_id": DATABASE_ID}
        )
        
        leftovers = []
        for item in response['results']:
            props = item.get('properties', {})
            
            # Safe property access with defaults
            food_title = props.get('Food', {}).get('title', [])
            food = food_title[0].get('text', {}).get('content', 'Unknown') if food_title else 'Unknown'
            
            expires_date = props.get('Expires', {}).get('date', {})
            expires = expires_date.get('start') if expires_date else None
            
            days_left = props.get('Days Left', {}).get('number', 0)
            
            location_text = props.get('Location', {}).get('rich_text', [])
            location = location_text[0].get('text', {}).get('content', 'Unknown') if location_text else 'Unknown'
            added_by_select = props.get('Added By', {}).get('select', {})
            added_by = added_by_select.get('name', 'Unknown') if added_by_select else 'Unknown'
            
            notes_text = props.get('Notes', {}).get('rich_text', [])
            notes = notes_text[0].get('text', {}).get('content', '') if notes_text else ''
            
            # Get photo URL if available
            photo_url = None
            if 'Photo' in props and props['Photo'].get('files'):
                photo_files = props['Photo'].get('files', [])
                if photo_files:
                    photo_url = photo_files[0].get('file', {}).get('url')
            
            if expires:
                leftovers.append({
                    'food': food,
                    'expires': expires,
                    'days_left': days_left,
                    'location': location,
                    'added_by': added_by,
                    'notes': notes,
                    'photo_url': photo_url
                })
        
        return leftovers
        
    except Exception as e:
        st.error(f"Error fetching leftovers: {str(e)}")
        return []

# Main App UI
st.title("🍱 Leftovers Tracker")
st.write("Track your leftovers and reduce food waste!")

# Add New Leftover Form
st.header("Add New Leftover")
with st.form("add_leftover"):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        food_name = st.text_input("Food Name", placeholder="e.g., Pizza, Chicken pasta")
        photo_file = st.file_uploader("Upload Photo (optional)", type=["jpg", "jpeg", "png", "gif"])
    
    with col2:
        expires_days = st.number_input("Expires in", min_value=1, max_value=7, value=3)
    
    location = st.selectbox("Location", [
        "Top shelf", "Middle shelf", "Bottom shelf", "Crisper drawer", "Door"
    ])
    
    added_by = st.selectbox("Added by", ["You", "Wife"])
    notes = st.text_area("Notes (optional)", placeholder="e.g., Half eaten, needs reheating")
    
    submitted = st.form_submit_button("Add Leftover")
    
    if submitted:
        success, message = add_leftover(food_name, expires_days, location, added_by, notes, photo_file)
        if success:
            st.success(f"✅ {message}")
            st.balloons()
        else:
            st.error(f"❌ {message}")

# Current Leftovers Display - ROBUST VERSION
st.header("Current Leftovers")
leftovers = get_leftovers()

if leftovers:
    for item in leftovers:
        try:
            days_left = item.get('days_left', 0)
            if days_left <= 1:
                status_text = f"⚠️ Expires in {days_left} day!"
                color = "red"
            elif days_left <= 3:
                status_text = f"⚠️ Expires in {days_left} days!"
                color = "orange"
            else:
                status_text = f"✅ Expires in {days_left} days"
                color = "green"
            
            # Display photo if available
            if item.get('photo_url'):
                try:
                    st.image(item['photo_url'], width=150, caption=item.get('food', 'Unknown'))
                except:
                    st.write("⚠️ Could not display photo")
            
            # Display item info with safe defaults
            food = item.get('food', 'Unknown')
            location = item.get('location', 'Unknown')
            added_by = item.get('added_by', 'Unknown')
            expires = item.get('expires', 'Unknown')
            notes = item.get('notes', '')
            
            st.markdown(f"""
            <div style="color: {color}; font-weight: bold; padding: 10px; border-radius: 5px; margin: 10px 0;">
            🍕 **{food}** | 📍 {location} | 👤 {added_by}  
            {status_text} | 📅 {expires[:10] if expires else 'Unknown'} | 📝 {notes}
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as display_error:
            st.warning(f"Error displaying item: {display_error}")
# Display a fallback version
            st.write(f"🍕 **Item**: {item.get('food', 'Unknown')} | 📅 {item.get('expires', 'Unknown')}")
else:
    st.info("🎯 Add your first leftover above to get started!")

# Statistics
st.header("📊 Waste Reduction Stats")
col1, col2, col3 = st.columns(3)

with col1:
    total_items = len(leftovers)
    st.metric("Total Items", total_items)

with col2:
    expiring_count = len([item for item in leftovers if item.get('days_left', 0) <= 2])
    st.metric("Expiring Soon", expiring_count)

with col3:
    estimated_savings = total_items * 5
    st.metric("Est. Savings", f"${estimated_savings}")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Check this app daily to stay on top of your leftovers!")
