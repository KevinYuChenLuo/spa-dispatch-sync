import streamlit as st
from tinydb import TinyDB
from datetime import datetime, timedelta
import theme

st.set_page_config(
    page_title="Break Room Monitor", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

theme.apply_theme()

st.title("Current Room Assignments")

db = TinyDB('spa_data.json')
assignments_table = db.table('assignments')

@st.fragment(run_every=1)
def live_staff_monitor():
    active_assignments = assignments_table.all()
    
    if not active_assignments:
        st.info("No active room assignments. Standby.")
        return

    cols = st.columns(3)
    now = datetime.now()
    
    for index, assignment in enumerate(active_assignments):
        start_time_obj = datetime.strptime(assignment['start_time'], "%I:%M %p")
        target_start_dt = now.replace(hour=start_time_obj.hour, minute=start_time_obj.minute, second=0, microsecond=0)
        
        duration_minutes = int(assignment['duration'].split()[0])
        target_end_dt = target_start_dt + timedelta(minutes=duration_minutes)
        
        time_until_start = (target_start_dt - now).total_seconds()
        time_until_end = (target_end_dt - now).total_seconds()
        
        if time_until_end <= 0:
            assignments_table.remove(doc_ids=[assignment.doc_id])
            st.rerun()
            
        current_col = cols[index % 3]
        
        with current_col:
            end_time_str = target_end_dt.strftime("%I:%M %p")
            schedule_str = f"{assignment['start_time']} - {end_time_str}"
            
            if time_until_start > 0:
                minutes, seconds = divmod(int(time_until_start), 60)
                is_in_progress = False
                timer_str = f"{minutes}m {seconds:02d}s"
            else:
                minutes, seconds = divmod(int(time_until_end), 60)
                is_in_progress = True
                timer_str = f"{minutes}m {seconds:02d}s"
            
            theme.render_room_card(
                room=assignment['room'],
                therapist=assignment['therapist'],
                schedule_str=schedule_str,
                is_in_progress=is_in_progress,
                timer_str=timer_str,
                duration=assignment['duration'],
                large=True
            )

live_staff_monitor()