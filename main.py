import streamlit as st
from tinydb import TinyDB, Query
from datetime import datetime


# --- 1. THE DATA SETUP ---
db = TinyDB('spa_data.json')
therapists_table = db.table('therapists')
assignments_table = db.table('assignments')
presets_table = db.table('presets')

rooms = ["Room 1", "Room 2", "Room 3", "Room 4"]
time_slots = ["30 minutes", "60 minutes", "90 minutes", "120 minutes"]

def get_active_therapists():
    return [person['name'] for person in therapists_table.all()]

active_therapists = get_active_therapists()

# --- 2. MANAGE STAFF UI ---
st.title("Front Desk Dispatch")

tab_staff, tab_presets = st.tabs(["Manage Individual Staff", "Shift Presets"])

with tab_staff:
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("Add Therapist Name")
        if st.button("Add to Shift"):
            if new_name and new_name not in active_therapists:
                therapists_table.insert({'name': new_name})
                st.rerun()
                
    with col2:
        name_to_remove = st.selectbox("Remove from Shift", active_therapists)
        if st.button("Remove"):
            if name_to_remove:
                TherapistQuery = Query()
                therapists_table.remove(TherapistQuery.name == name_to_remove)
                st.rerun()

with tab_presets:
    col3, col4 = st.columns(2)
    with col3:
        st.write("**Save Current Shift**")
        preset_name = st.text_input("Preset Name (e.g., 'Morning Shift')")
        if st.button("Save as Preset"):
            if preset_name and active_therapists:
                PresetQuery = Query()
                presets_table.upsert({'name': preset_name, 'staff': active_therapists}, PresetQuery.name == preset_name)
                st.success(f"Preset '{preset_name}' saved!")
            elif not active_therapists:
                st.error("No active therapists to save.")
                
    with col4:
        st.write("**Load a Preset**")
        saved_presets = [p['name'] for p in presets_table.all()]
        if saved_presets:
            selected_preset = st.selectbox("Choose Preset", saved_presets)
            if st.button("Load Staff from Preset"):
                PresetQuery = Query()
                preset_data = presets_table.search(PresetQuery.name == selected_preset)[0]
                therapists_table.truncate()
                for staff_name in preset_data['staff']:
                    therapists_table.insert({'name': staff_name})
                st.rerun()
        else:
            st.info("No presets saved yet.")

# --- 3. DISPATCH UI ---
st.divider()
st.subheader("Assign Room")

# Fetch active assignments early so we can check who is currently busy
active_assignments = assignments_table.all()
assigned_therapists = [assignment['therapist'] for assignment in active_assignments]

# Filter out therapists who are already assigned to a room
available_therapists = [t for t in active_therapists if t not in assigned_therapists]

if not active_therapists:
    st.warning("Please add therapists or load a preset using the tabs above.")
elif not available_therapists:
    st.error("All therapists on shift are currently assigned to a room.")
else:
    with st.form("dispatch_form"):
        # The dropdown now only shows available therapists
        selected_therapist = st.selectbox("Select Therapist", available_therapists)
        selected_room = st.selectbox("Select Room", rooms)
        selected_start_time = st.time_input("Session Start Time")
        selected_duration = st.selectbox("Duration", time_slots)
        
        submitted = st.form_submit_button("Assign to Room")
        
        if submitted:
            assignment_data = {
                "therapist": selected_therapist,
                "room": selected_room,
                "start_time": selected_start_time.strftime("%I:%M %p"),
                "duration": selected_duration,
                "dispatch_time": datetime.now().strftime("%I:%M %p")
            }
            assignments_table.insert(assignment_data)
            st.rerun() # Instantly refreshes to remove the therapist from the available list

st.divider()
st.subheader("Current Active Rooms")

# The fragment decorator isolates this function and reruns it every 1 second
@st.fragment(run_every=1)
def live_active_rooms():
    active_assignments = assignments_table.all()
    
    if not active_assignments:
        st.info("No active room assignments.")
        return # Stops the function here if there are no assignments

    # Changed from 4 columns to 3 to make the cards wider
    cols = st.columns(3)
    
    for index, assignment in enumerate(active_assignments):
        current_col = cols[index % 3]
        
        with current_col:
            with st.container(border=True):
                st.markdown(f"### {assignment['room']}")
                st.write(f"**Therapist:** {assignment['therapist']}")
                
                # --- LIVE COUNTDOWN TIMER ---
                now = datetime.now()
                start_time_obj = datetime.strptime(assignment['start_time'], "%I:%M %p")
                target_start_dt = now.replace(hour=start_time_obj.hour, minute=start_time_obj.minute, second=0, microsecond=0)
                
                time_diff = target_start_dt - now
                
                if time_diff.total_seconds() > 0:
                    minutes, seconds = divmod(int(time_diff.total_seconds()), 60)
                    # The :02d ensures seconds always show two digits (e.g., 05s)
                    st.write(f"**Starts in:** {minutes}m {seconds:02d}s")
                else:
                    st.write("**Session in Progress**")
                
                st.write(f"**Duration:** {assignment['duration']}")
                
                if st.button("Finish", key=f"clear_{assignment.doc_id}"):
                    assignments_table.remove(doc_ids=[assignment.doc_id])
                    st.rerun()

# Call the function so it actually displays on the page
live_active_rooms()