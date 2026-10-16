import streamlit as st
from tinydb import TinyDB

def get_current_theme():
    db = TinyDB('spa_data.json')
    settings_table = db.table('settings')
    all_settings = settings_table.all()
    if all_settings and 'theme' in all_settings[0]:
        return all_settings[0]['theme']
    return "Light (Day Spa)"

def render_sidebar():
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### Navigation")
        st.page_link("main.py", label="Front Desk Dispatch")
        st.page_link("pages/staff.py", label="Break Room Monitor")
        st.page_link("pages/settings.py", label="System Settings")

def render_room_card(room, therapist, schedule_str, is_in_progress, timer_str, duration, large=False):
    """Renders a rock-solid custom HTML card that guarantees visible borders in both themes."""
    title_size = "28px" if large else "24px"
    sub_size = "22px" if large else "19px"
    
    if is_in_progress:
        status_html = (
            f"<div class='spa-card-row'><span class='status-in-progress'>Session in Progress</span></div>"
            f"<div class='spa-card-row'><strong>Time Remaining:</strong> {timer_str}</div>"
        )
    else:
        status_html = f"<div class='spa-card-row'><strong>Starts in:</strong> {timer_str}</div>"

    card_html = f"""
    <div class="spa-card">
        <div class="spa-card-title" style="font-size: {title_size};">{room}</div>
        <div class="spa-card-subtitle" style="font-size: {sub_size};"><strong>Therapist:</strong> {therapist}</div>
        <div class="spa-card-row"><strong>Schedule:</strong> {schedule_str}</div>
        {status_html}
        <div class="spa-card-row"><strong>Duration:</strong> {duration}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def apply_theme(hide_sidebar=False):
    if not hide_sidebar:
        render_sidebar()
        
    mode = get_current_theme()
    is_dark = (mode == "Dark (Night Spa)")

    if is_dark:
        bg_color = "#1C1C1C"        # Soft black
        sec_bg_color = "#2A2E28"    # Deep mossy charcoal
        card_bg_color = "#232722"   # Slightly darker moss for cards
        text_color = "#F2EDE4"      # Creamy neutral
        primary_color = "#5F9EA0"   # Muted teal
        border_color = "#FFFFFF"    # Crisp white outline in Dark Mode
        status_green = "#81C784"    # High-level light green
    else:
        bg_color = "#F5F2EB"        # Warm beige
        sec_bg_color = "#EAE5D9"    # Oat
        card_bg_color = "#FCFAF5"   # Creamy white
        text_color = "#403D39"      # Deep espresso
        primary_color = "#7A907C"   # Sage green
        border_color = "#6E6659"    # High-contrast warm taupe/umber outline in Light Mode
        status_green = "#1B5E20"    # Rich forest green

    sidebar_hide_css = """
        [data-testid="collapsedControl"] { display: none !important; }
    """ if hide_sidebar else ""

    custom_css = f"""
    <style>
        :root {{
            --bg-color: {bg_color};
            --sec-bg-color: {sec_bg_color};
            --card-bg-color: {card_bg_color};
            --text-color: {text_color};
            --primary-color: {primary_color};
            --border-color: {border_color};
            --status-green: {status_green};
        }}

        {sidebar_hide_css}

        /* 1. Main App, Top Header Bar, and Sidebar Backgrounds */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-color: var(--bg-color) !important;
        }}
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {{
            background-color: var(--sec-bg-color) !important;
            border-right: 2px solid var(--border-color) !important;
        }}

        /* 2. Custom Spa Room Card (Guaranteed Border & Styling) */
        .spa-card {{
            background-color: var(--card-bg-color) !important;
            border: 2.5px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            margin-bottom: 12px !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08) !important;
            color: var(--text-color) !important;
        }}
        .spa-card-title {{
            font-weight: 700 !important;
            margin-bottom: 10px !important;
            color: var(--text-color) !important;
        }}
        .spa-card-subtitle {{
            margin-bottom: 10px !important;
            color: var(--text-color) !important;
        }}
        .spa-card-row {{
            font-size: 18px !important;
            margin-bottom: 6px !important;
            color: var(--text-color) !important;
        }}
        .status-in-progress {{
            color: var(--status-green) !important;
            font-weight: 700 !important;
            font-size: 20px !important;
        }}

        /* 3. Body Text & Headers */
        p, li, label, [data-testid="stWidgetLabel"] p {{
            color: var(--text-color) !important;
            font-size: 18px !important;
        }}
        h1, h1 span {{
            color: var(--text-color) !important;
            font-size: 38px !important;
            font-weight: 700 !important;
        }}
        h2, h2 span {{
            color: var(--text-color) !important;
            font-size: 28px !important;
            font-weight: 600 !important;
        }}
        h3, h3 span {{
            color: var(--text-color) !important;
            font-size: 22px !important;
            font-weight: 600 !important;
        }}

        /* 4. Inputs, Time Picker, and Dropdowns */
        div[data-baseweb="input"], 
        div[data-baseweb="base-input"], 
        div[data-baseweb="select"] > div,
        input {{
            background-color: var(--sec-bg-color) !important;
            color: var(--text-color) !important;
            border: 1.5px solid var(--border-color) !important;
            border-radius: 8px !important;
            font-size: 18px !important;
            -webkit-text-fill-color: var(--text-color) !important;
        }}
        div[data-baseweb="select"] div {{
            background-color: transparent !important;
            color: var(--text-color) !important;
        }}
        div[data-baseweb="select"] svg {{
            fill: var(--text-color) !important;
        }}
        div[data-baseweb="popover"] div, 
        ul[role="listbox"], 
        li[role="option"] {{
            background-color: var(--sec-bg-color) !important;
            color: var(--text-color) !important;
            font-size: 18px !important;
        }}
        li[role="option"]:hover {{
            background-color: var(--primary-color) !important;
            color: #FFFFFF !important;
        }}

        /* 5. Buttons and Form Containers */
        .stButton > button, 
        .stFormSubmitButton > button {{
            background-color: var(--primary-color) !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 22px !important;
        }}
        .stButton > button *, 
        .stFormSubmitButton > button * {{
            color: #FFFFFF !important;
            font-size: 18px !important;
            font-weight: 500 !important;
        }}
        [data-testid="stForm"] {{
            background-color: var(--card-bg-color) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 20px !important;
        }}

        /* 6. Tabs, Sidebar Links, and Info Boxes */
        button[data-baseweb="tab"] {{
            background-color: transparent !important;
        }}
        button[data-baseweb="tab"] p {{
            color: var(--text-color) !important;
            font-size: 18px !important;
        }}
        [data-testid="stPageLink-NavLink"] {{
            background-color: transparent !important;
            border-radius: 8px !important;
        }}
        [data-testid="stPageLink-NavLink"] span {{
            color: var(--text-color) !important;
            font-size: 18px !important;
        }}
        [data-testid="stPageLink-NavLink"]:hover {{
            background-color: var(--border-color) !important;
        }}
        div[data-testid="stAlert"] {{
            background-color: var(--sec-bg-color) !important;
            color: var(--text-color) !important;
            border: 1.5px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)