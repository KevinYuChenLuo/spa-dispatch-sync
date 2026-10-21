import streamlit as st
from tinydb import TinyDB, Query
from datetime import datetime, timedelta
import theme

# Must be the first Streamlit command
st.set_page_config(page_title="Front Desk Dispatch", layout="wide")
theme.apply_theme()

# --- 1. THE DATA SETUP ---
db = TinyDB('spa_data.json')
therapists_table = db.table('therapists')
assignments_table = db.table('assignments')
presets_table = db.table('presets')

rooms = ["Room 1 (Double Bed)", "Room 2", "Room 3 (Double Bed)", "Room 4", "Room 5", "Room 6", "Room 7", "Room 8", "Room 9", "Room 10"]
time_slots = ["30 minutes", "60 minutes", "90 minutes", "120 minutes"]

def get_active_therapists():
    return [person['name'] for person in therapists_table.all()]

active_therapists = get_active_therapists()

# --- 2. MANAGE STAFF UI ---
st.title("Healing Place - Front Desk Dispatch")

active_assignments = assignments_table.all()
assigned_therapists = [assignment['therapist'] for assignment in active_assignments]
available_therapists = [t for t in active_therapists if t not in assigned_therapists]

tab_staff, tab_presets = st.tabs(["Manage Individual Staff", "Shift Presets"])

selected_preset_name = None

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

    st.divider()
    st.subheader("Therapists on Current Shift")
    if active_therapists:
        on_shift_str = ", ".join(active_therapists)
        st.write(f"**On Shift:** {on_shift_str}")
        
        if available_therapists:
            avail_str = ", ".join(available_therapists)
            st.write(f"**Available for Dispatch:** {avail_str}")
        else:
            st.info("All therapists on shift are currently in a session.")
    else:
        st.info("No therapists currently on shift.")

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
        st.markdown("#### Load a Preset")
        saved_presets = presets_table.all()
        
        if saved_presets:
            preset_names = [p['name'] for p in saved_presets]
            selected_preset_name = st.selectbox("Choose Preset", preset_names)
            
            # Create two side-by-side columns for the Load and Delete buttons
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button("Load Therapists"):
                    PresetQuery = Query()
                    preset_data = presets_table.get(PresetQuery.name == selected_preset_name)
                    if preset_data:
                        therapists_table.truncate()
                        for therapist_name in preset_data['staff']:
                            therapists_table.insert({'name': therapist_name})
                        st.rerun()
                        
            with btn_col2:
                if st.button("Delete Preset"):
                    PresetQuery = Query()
                    presets_table.remove(PresetQuery.name == selected_preset_name)
                    st.rerun()
        else:
            st.info("No saved presets yet.")

    # --- 2.5 SELECTED PRESET THERAPISTS ROW (Now inside tab_presets) ---
    st.divider()
    if selected_preset_name:
        PresetQuery = Query()
        current_preset = presets_table.get(PresetQuery.name == selected_preset_name)
        st.subheader(f"Therapists in '{selected_preset_name}' Preset")
        if current_preset and current_preset.get('staff'):
            staff_list_str = ", ".join(current_preset['staff'])
            st.write(f"**Included Staff:** {staff_list_str}")
        else:
            st.info("No therapists saved in this preset.")
    else:
        st.subheader("Therapists in Selected Preset")
        st.info("No preset currently selected.")

# --- POP-UP DIALOG FOR ROOM CONFLICTS ---
@st.dialog("Room Unavailable")
def room_conflict_popup(room_name, therapist_name, start_str, end_str):
    st.write(f"**{room_name}** is not available during this time slot.")
    st.write(f"It is currently assigned to **{therapist_name}** from **{start_str} to {end_str}**.")
    if st.button("OK"):
        st.rerun()

# --- 3. DISPATCH UI ---
st.divider()
st.subheader("Assign Room")

active_assignments = assignments_table.all()
assigned_therapists = [assignment['therapist'] for assignment in active_assignments]
available_therapists = [t for t in active_therapists if t not in assigned_therapists]

if not active_therapists:
    st.warning("Please add therapists or load a preset using the tabs above.")
elif not available_therapists:
    st.error("All therapists on shift are currently assigned to a room.")
else:
    with st.form("dispatch_form"):
        selected_therapist = st.selectbox("Select Therapist", available_therapists)
        selected_room = st.selectbox("Select Room", rooms)
        selected_start_time = st.time_input("Session Start Time")
        selected_duration = st.selectbox("Duration", time_slots)
        
        submitted = st.form_submit_button("Assign to Room")
        
        if submitted:
            now = datetime.now()
            
            # Calculate proposed start and end times
            new_start_dt = now.replace(
                hour=selected_start_time.hour, 
                minute=selected_start_time.minute, 
                second=0, 
                microsecond=0
            )
            new_duration_mins = int(selected_duration.split()[0])
            new_end_dt = new_start_dt + timedelta(minutes=new_duration_mins)
            
            # Check if the selected room has any overlapping active assignments
            conflict = None
            for existing in assignments_table.all():
                if existing['room'] == selected_room:
                    ex_start_obj = datetime.strptime(existing['start_time'], "%I:%M %p")
                    ex_start_dt = now.replace(
                        hour=ex_start_obj.hour, 
                        minute=ex_start_obj.minute, 
                        second=0, 
                        microsecond=0
                    )
                    ex_duration_mins = int(existing['duration'].split()[0])
                    ex_end_dt = ex_start_dt + timedelta(minutes=ex_duration_mins)
                    
                    # Overlap check: starts before existing ends AND ends after existing starts
                    if new_start_dt < ex_end_dt and new_end_dt > ex_start_dt:
                        conflict = (
                            existing['therapist'], 
                            existing['start_time'], 
                            ex_end_dt.strftime("%I:%M %p")
                        )
                        break
            
            if conflict:
                # Trigger the pop-up dialog instead of saving
                room_conflict_popup(selected_room, conflict[0], conflict[1], conflict[2])
            else:
                assignment_data = {
                    "therapist": selected_therapist,
                    "room": selected_room,
                    "start_time": selected_start_time.strftime("%I:%M %p"),
                    "duration": selected_duration,
                    "dispatch_time": now.strftime("%I:%M %p")
                }
                assignments_table.insert(assignment_data)
                st.rerun()

# --- 4. ACTIVE ASSIGNMENTS GRID ---
st.divider()
st.subheader("Current Active Rooms")

@st.fragment(run_every=1)
def live_active_rooms():
    active_assignments = assignments_table.all()
    
    if not active_assignments:
        st.info("No active room assignments.")
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
            
            # Render the custom HTML card with guaranteed borders
            theme.render_room_card(
                room=assignment['room'],
                therapist=assignment['therapist'],
                schedule_str=schedule_str,
                is_in_progress=is_in_progress,
                timer_str=timer_str,
                duration=assignment['duration'],
                large=False
            )
            
            if st.button("Finish Early", key=f"clear_{assignment.doc_id}"):
                assignments_table.remove(doc_ids=[assignment.doc_id])
                st.rerun()

live_active_rooms()