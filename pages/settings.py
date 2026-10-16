import streamlit as st
from tinydb import TinyDB
import theme

st.set_page_config(page_title="System Settings", layout="wide")
theme.apply_theme()

db = TinyDB('spa_data.json')
settings_table = db.table('settings')

st.title("System Settings")
st.write("Configure the visual appearance and global preferences for the Front Desk and Break Room screens.")
st.divider()

st.subheader("Appearance & Theme")

current_theme = theme.get_current_theme()
theme_options = ["Light (Day Spa)", "Dark (Night Spa)"]

selected_theme = st.radio(
    "Select Color Theme",
    options=theme_options,
    index=theme_options.index(current_theme)
)

# If the user clicks a different option, save it to TinyDB and refresh immediately
if selected_theme != current_theme:
    settings_table.truncate()
    settings_table.insert({'theme': selected_theme})
    st.rerun()