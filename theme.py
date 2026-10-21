import streamlit as st

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

def render_room_card(room, therapist, schedule_str, is_in_progress, timer_str, duration, large=False, total_cards=1):
    """Renders the room card with dynamic TV sizing while inheriting Streamlit's native Light/Dark colors."""
    is_multi_row = (total_cards > 3)

    if large:
        if is_multi_row:
            title_size = "clamp(18px, 2.2vh, 24px)"
            sub_size = "clamp(15px, 1.8vh, 20px)"
            row_size = "clamp(13px, 1.5vh, 17px)"
            status_size = "clamp(15px, 1.8vh, 20px)"
            card_pad = "1.2vh 1.2vw"
            row_margin = "0.4vh"
        else:
            title_size = "clamp(24px, 3.2vh, 34px)"
            sub_size = "clamp(18px, 2.4vh, 26px)"
            row_size = "clamp(16px, 2.0vh, 22px)"
            status_size = "clamp(18px, 2.4vh, 26px)"
            card_pad = "2.2vh 1.5vw"
            row_margin = "0.9vh"
    else:
        title_size = "22px"
        sub_size = "18px"
        row_size = "16px"
        status_size = "18px"
        card_pad = "16px"
        row_margin = "6px"

    if is_in_progress:
        status_html = (
            f"<div class='spa-card-row' style='font-size: {row_size}; margin-bottom: {row_margin};'>"
            f"<span class='status-in-progress' style='font-size: {status_size};'>Session in Progress</span></div>"
            f"<div class='spa-card-row' style='font-size: {row_size}; margin-bottom: {row_margin};'>"
            f"<strong>Time Remaining:</strong> {timer_str}</div>"
        )
    else:
        status_html = (
            f"<div class='spa-card-row' style='font-size: {row_size}; margin-bottom: {row_margin};'>"
            f"<strong>Starts in:</strong> {timer_str}</div>"
        )

    card_html = f"""
    <div class="spa-card" style="padding: {card_pad};">
        <div class="spa-card-title" style="font-size: {title_size}; margin-bottom: {row_margin};">{room}</div>
        <div class="spa-card-subtitle" style="font-size: {sub_size}; margin-bottom: {row_margin};"><strong>Therapist:</strong> {therapist}</div>
        <div class="spa-card-row" style="font-size: {row_size}; margin-bottom: {row_margin};"><strong>Schedule:</strong> {schedule_str}</div>
        {status_html}
        <div class="spa-card-row" style="font-size: {row_size}; margin-bottom: 0;"><strong>Duration:</strong> {duration}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def apply_theme(hide_sidebar=False, compact_top=False):
    if not hide_sidebar:
        render_sidebar()

    top_space_css = """
        .block-container, [data-testid="stMainBlockContainer"] {
            padding-top: 2.2rem !important;
            padding-bottom: 1rem !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
            max-width: 100% !important;
        }
        h1 {
            margin-top: 0px !important;
            padding-top: 0px !important;
            margin-bottom: 0.8rem !important;
        }
    """ if compact_top else ""

    custom_css = f"""
    <style>
        {top_space_css}

        /* Uses currentColor so the border automatically matches Streamlit's native Light/Dark text color */
        .spa-card {{
            border: 2px solid currentColor !important;
            border-radius: 12px !important;
            margin-bottom: 1.2vh !important;
        }}
        .spa-card-title {{
            font-weight: 700 !important;
            line-height: 1.2 !important;
        }}
        .spa-card-subtitle {{
            line-height: 1.25 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        .spa-card-row {{
            line-height: 1.3 !important;
            white-space: nowrap !important;
        }}
        .status-in-progress {{
            color: #2E7D32 !important;
            font-weight: 700 !important;
        }}
        @media (prefers-color-scheme: dark) {{
            .status-in-progress {{
                color: #81C784 !important;
            }}
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)