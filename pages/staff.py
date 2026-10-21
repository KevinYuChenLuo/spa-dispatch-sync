import streamlit as st
from tinydb import TinyDB
import theme

st.set_page_config(
    page_title="Break Room Monitor", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

theme.apply_theme(compact_top=True)

st.title("Current Room Assignments")

db = TinyDB('spa_data.json')
assignments_table = db.table('assignments')

@st.fragment(run_every=2)
def live_staff_monitor():
    active_assignments = assignments_table.all()
    
    if not active_assignments:
        st.info("No active room assignments. Standby.")
        return

    total_cards = len(active_assignments)
    # Use 3 columns for up to 6 cards, or 4 columns for 7-10+ cards
    num_cols = 4 if total_cards > 6 else 3
    cols = st.columns(num_cols)
    
    for index, assignment in enumerate(active_assignments):
        current_col = cols[index % num_cols]
        
        with current_col:
            theme.render_room_card(
                room=assignment['room'],
                therapist=assignment['therapist'],
                notes=assignment.get('notes', ''),
                large=True,
                total_cards=total_cards
            )

live_staff_monitor()