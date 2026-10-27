import streamlit as st
import math
import html

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

def render_room_card(room, therapist, notes="", large=False, total_cards=1):
    """Renders the room card with Room, Therapist, and optional Notes."""
    if large:
        if total_cards > 6:
            # Compact TV sizing for 7-10+ cards (3 rows)
            title_size = "clamp(18px, 2.3vh, 24px)"
            sub_size = "clamp(16px, 2.0vh, 22px)"
            note_size = "clamp(14px, 1.7vh, 18px)"
            card_pad = "1.2vh 1.2vw"
            row_margin = "0.5vh"
        elif total_cards > 3:
            # Medium TV sizing for 4-6 cards (2 rows)
            title_size = "clamp(22px, 2.8vh, 30px)"
            sub_size = "clamp(18px, 2.4vh, 26px)"
            note_size = "clamp(16px, 2.0vh, 22px)"
            card_pad = "1.8vh 1.5vw"
            row_margin = "0.7vh"
        else:
            # Spacious TV sizing for 1-3 cards (1 row)
            title_size = "clamp(26px, 3.6vh, 38px)"
            sub_size = "clamp(20px, 2.8vh, 30px)"
            note_size = "clamp(18px, 2.3vh, 25px)"
            card_pad = "2.5vh 1.8vw"
            row_margin = "1.0vh"
    else:
        # Front Desk PC sizing
        title_size = "20px"
        sub_size = "17px"
        note_size = "15px"
        card_pad = "16px"
        row_margin = "6px"

    notes_clean = str(notes).strip()
    if notes_clean:
        notes_html = f'<div class="spa-card-notes" style="font-size: {note_size}; margin-top: {row_margin};"><strong>Notes:</strong> {notes_clean}</div>'
    else:
        notes_html = ""

    card_html = f"""
    <div class="spa-card" style="padding: {card_pad};">
        <div class="spa-card-title" style="font-size: {title_size}; margin-bottom: {row_margin};">{room}</div>
        <div class="spa-card-subtitle" style="font-size: {sub_size}; margin-bottom: 0;"><strong>Therapist:</strong> {therapist}</div>
        {notes_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_breakroom_grid(assignments):
    """
    Renders Break Room cards using pure percentage grid columns (zoom-proof),
    leaves bottom breathing room, centers the Room title, and dynamically scales
    font sizes using cqmin (card container query units).
    """
    cards_html = "".join([
        f'<div class="spa-grid-card">'
        f'<div class="spa-grid-title">{html.escape(str(a.get("room", "")))}</div>'
        f'<div class="spa-grid-subtitle"><strong>Therapist:</strong> {html.escape(str(a.get("therapist", "")))}</div>'
        + (
            f'<div class="spa-grid-notes"><strong>Notes:</strong> {html.escape(str(a.get("notes", "")).strip())}</div>'
            if str(a.get("notes", "")).strip() else ""
        )
        + '</div>'
        for a in assignments
    ])

    st.markdown(f"""
    <style>
        .spa-breakroom-grid {{
            display: grid;
            /* Pure percentage (21%) keeps 4 columns even when zoomed in */
            grid-template-columns: repeat(auto-fit, minmax(21%, 1fr));
            grid-auto-rows: 1fr;
            gap: 1.4rem;
            /* Leaves comfortable vertical space at the bottom of the screen */
            height: calc(100vh - 12.5rem);
            min-height: 420px;
            width: 100%;
            box-sizing: border-box;
        }}
        .spa-grid-card {{
            container-type: size;
            border: 2px solid currentColor;
            border-radius: 14px;
            padding: 6cqmin 7cqi;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
            width: 100%;
            box-sizing: border-box;
            overflow: hidden;
        }}
        .spa-grid-title {{
            /* Centered and dynamically scaled to card dimensions */
            text-align: center;
            width: 100%;
            font-size: clamp(1.5rem, 14cqmin, 4.2rem);
            font-weight: 800;
            line-height: 1.15;
            margin-bottom: 4cqmin;
        }}
        .spa-grid-subtitle {{
            /* Left-aligned and larger dynamic font */
            text-align: left;
            width: 100%;
            font-size: clamp(1.15rem, 9.5cqmin, 2.8rem);
            line-height: 1.3;
        }}
        .spa-grid-notes {{
            text-align: left;
            width: 100%;
            font-size: clamp(1rem, 7.5cqmin, 2.2rem);
            line-height: 1.35;
            margin-top: 3cqmin;
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow: hidden;
            opacity: 0.9;
        }}
    </style>
    <div class="spa-breakroom-grid">{cards_html}</div>
    """, unsafe_allow_html=True)

def apply_theme(hide_sidebar=False, compact_top=False):
    if not hide_sidebar:
        render_sidebar()

    # Removed overflow: hidden so zooming in never hides cards without a scrollbar
    top_space_css = """
        [data-testid="stHeader"] {
            background: transparent !important;
        }
        .block-container, [data-testid="stMainBlockContainer"] {
            padding-top: 2.2rem !important;
            padding-bottom: 1.5rem !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
            max-width: 100% !important;
        }
        h1 {
            margin-top: 0px !important;
            padding-top: 0px !important;
            margin-bottom: 1rem !important;
        }
    """ if compact_top else ""

    custom_css = f"""
    <style>
        {top_space_css}

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
            line-height: 1.3 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        .spa-card-notes {{
            line-height: 1.35 !important;
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            opacity: 0.9 !important;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)