import streamlit as st
from tinydb import TinyDB, Query
import theme

# Must be the first Streamlit command
st.set_page_config(page_title="Front Desk Dispatch", layout="wide")
theme.apply_theme()

# --- 1. THE DATA SETUP ---
db = TinyDB('spa_data.json')
therapists_table = db.table('therapists')
assignments_table = db.table('assignments')
presets_table = db.table('presets')

rooms = [
    "Room 1 (Double)", "Room 2", "Room 3 (Double)", "Room 4", 
    "Room 5 (Double)", "Room 6", "Room 7", "Room 8", "Room 9", "Room 10"
]

def get_active_therapists():
    return [person['name'] for person in therapists_table.all()]

active_therapists = get_active_therapists()

# --- 2. MANAGE STAFF UI ---
st.title("Healing Place - Front Desk Dispatch")

# Track all busy therapists (supports both single and 2-therapist double rooms)
active_assignments = assignments_table.all()
assigned_therapists = []
for assignment in active_assignments:
    if 'therapists' in assignment:
        assigned_therapists.extend(assignment['therapists'])
    elif 'therapist' in assignment:
        # Backward compatibility if an older card is still active
        assigned_therapists.extend([t.strip() for t in assignment['therapist'].split(',')])

available_therapists = [t for t in active_therapists if t not in assigned_therapists]

tab_staff, tab_presets = st.tabs(["Manage Individual Staff", "Shift Presets"])

selected_preset_name = None

with tab_staff:
    col1, col2 = st.columns(2)
    with col1:
        with st.form("add_therapist_form", clear_on_submit=True):
            new_name = st.text_input("Add Therapist Name")
            submitted_staff = st.form_submit_button("Add to Shift")
            
            if submitted_staff:
                if new_name and new_name not in active_therapists:
                    therapists_table.insert({'name': new_name})
                    st.rerun()
                elif not new_name:
                    st.warning("Please enter a therapist name.")
                else:
                    st.warning(f"'{new_name}' is already on shift.")
                
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
            st.info("All therapists on shift are currently assigned to a room.")
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
def room_conflict_popup(room_name, therapist_name):
    st.write(f"**{room_name}** is currently occupied by **{therapist_name}**.")
    st.write("Please clear the room first or choose another room.")
    if st.button("OK"):
        st.rerun()

# --- 3. DISPATCH UI ---
st.divider()
st.subheader("Assign Room")

if "dispatch_reset_counter" not in st.session_state:
    st.session_state.dispatch_reset_counter = 0

# Filter out rooms that are already occupied
occupied_rooms = [assignment['room'] for assignment in assignments_table.all()]
available_rooms = [r for r in rooms if r not in occupied_rooms]

if not active_therapists:
    st.warning("Please add therapists or load a preset using the tabs above.")
elif not available_therapists:
    st.error("All therapists on shift are currently assigned to a room.")
elif not available_rooms:
    st.info("All rooms are currently occupied.")
else:
    with st.container(border=True):
        # 1. Select Room First (only showing unoccupied rooms)
        selected_room = st.selectbox("Select Room", available_rooms)
        
        # 2. Select Therapist
        selected_therapist = st.selectbox("Select Therapist", available_therapists)
        
        # 3. Select 2nd Therapist if a Double room is selected
        selected_second_therapist = "None"
        if "(Double)" in selected_room:
            remaining_therapists = ["None"] + [t for t in available_therapists if t != selected_therapist]
            selected_second_therapist = st.selectbox(
                "Select 2nd Therapist (Optional)", 
                remaining_therapists,
                index=0
            )
            
        additional_notes = st.text_input(
            "Additional Notes (Optional)", 
            placeholder="e.g., 60 min deep tissue, couples massage, hot stone...",
            key=f"notes_input_{st.session_state.dispatch_reset_counter}"
        )
        
        if st.button("Assign to Room"):
            if selected_second_therapist and selected_second_therapist != "None":
                chosen_list = [selected_therapist, selected_second_therapist]
                display_therapist_str = f"{selected_therapist}, {selected_second_therapist}"
            else:
                chosen_list = [selected_therapist]
                display_therapist_str = selected_therapist

            assignment_data = {
                "therapist": display_therapist_str,
                "therapists": chosen_list,
                "room": selected_room,
                "notes": additional_notes.strip()
            }
            assignments_table.insert(assignment_data)
            st.session_state.dispatch_reset_counter += 1
            st.rerun()

# --- 4. ACTIVE ASSIGNMENTS GRID ---
st.divider()
st.subheader("Current Active Rooms")

@st.fragment(run_every=2)
def live_active_rooms():
    active_assignments = assignments_table.all()
    
    if not active_assignments:
        st.info("No active room assignments.")
        return

    cols = st.columns(3)
    
    for index, assignment in enumerate(active_assignments):
        current_col = cols[index % 3]
        
        with current_col:
            theme.render_room_card(
                room=assignment['room'],
                therapist=assignment['therapist'],
                notes=assignment.get('notes', ''),
                large=False
            )
            
            if st.button("Clear Room", key=f"clear_{assignment.doc_id}"):
                assignments_table.remove(doc_ids=[assignment.doc_id])
                st.rerun()

live_active_rooms()