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

    theme.render_breakroom_grid(active_assignments)

live_staff_monitor()