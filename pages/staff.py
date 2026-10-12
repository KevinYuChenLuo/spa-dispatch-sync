import streamlit as st
from tinydb import TinyDB
from datetime import datetime

# 1. Add initial_sidebar_state="collapsed"
st.set_page_config(
    page_title="Staff Room Display", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. Inject CSS to hide the sidebar toggle button completely
st.markdown(
    """
    <style>
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Current Room Assignments")

db = TinyDB('spa_data.json')
assignments_table = db.table('assignments')

# This fragment auto-refreshes every 1 second, making the timer tick 
# entirely hands-free for the TV monitor.
@st.fragment(run_every=1)
def live_staff_monitor():
    active_assignments = assignments_table.all()
    
    if not active_assignments:
        st.info("No active room assignments. Standby.")
        return

    # Using 3 columns for large, readable cards from across the room
    cols = st.columns(3)
    
    for index, assignment in enumerate(active_assignments):
        current_col = cols[index % 3]
        
        with current_col:
            with st.container(border=True):
                # Using larger markdown headings so it is visible from afar
                st.markdown(f"## {assignment['room']}")
                st.markdown(f"### Therapist: {assignment['therapist']}")
                
                now = datetime.now()
                start_time_obj = datetime.strptime(assignment['start_time'], "%I:%M %p")
                target_start_dt = now.replace(hour=start_time_obj.hour, minute=start_time_obj.minute, second=0, microsecond=0)
                
                time_diff = target_start_dt - now
                
                if time_diff.total_seconds() > 0:
                    minutes, seconds = divmod(int(time_diff.total_seconds()), 60)
                    # Colored text for visibility
                    st.markdown(f"#### ⏳ Starts in: :orange[{minutes}m {seconds:02d}s]")
                else:
                    st.markdown("#### 🟢 :green[Session in Progress]")
                
                st.write(f"**Duration:** {assignment['duration']}")

live_staff_monitor()