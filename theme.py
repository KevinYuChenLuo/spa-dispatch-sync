import streamlit as st
from datetime import datetime
import math
import html

def cleanup_expired_assignments(assignments_table, history_table=None, timeout_minutes=60):
    """
    Removes any room assignment older than timeout_minutes (default 60 mins).
    Returns True if any expired rooms were removed so the caller can trigger st.rerun() if needed.
    """
    now = datetime.now()
    removed_any = False

    for assignment in list(assignments_table.all()):
        assigned_str = assignment.get("assigned_at")
        if not assigned_str:
            # Backfill timestamp if an older card didn't have one
            assignments_table.update({"assigned_at": now.isoformat()}, doc_ids=[assignment.doc_id])
            continue

        assigned_dt = datetime.fromisoformat(assigned_str)
        elapsed_seconds = (now - assigned_dt).total_seconds()

        if elapsed_seconds >= timeout_minutes * 60:
            if history_table is not None:
                history_table.insert({
                    "date": now.strftime("%Y-%m-%d"),
                    "day_of_week": now.strftime("%A"),
                    "hour_assigned": assigned_dt.hour,
                    "room": assignment["room"],
                    "is_double_room": "(Double)" in assignment["room"],
                    "therapists": assignment.get("therapists", [assignment["therapist"]]),
                    "num_therapists": len(assignment.get("therapists", [assignment["therapist"]])),
                    "notes": assignment.get("notes", ""),
                    "assigned_at": assigned_str,
                    "cleared_at": now.isoformat(),
                    "turnaround_mins": float(timeout_minutes),
                    "auto_expired": True
                })
            assignments_table.remove(doc_ids=[assignment.doc_id])
            removed_any = True

    return removed_any

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
    80vh Break Room grid with extra-large dynamic fonts for no-notes cards
    and balanced header/notes sizing for cards with comments.
    """
    cards_html_list = []
    for a in assignments:
        room_str = html.escape(str(a.get("room", "")))
        therapist_str = html.escape(str(a.get("therapist", "")))
        notes_clean = html.escape(str(a.get("notes", "")).strip())
        
        has_notes_class = "has-notes" if notes_clean else "no-notes"
        notes_html = (
            f'<div class="spa-grid-notes"><strong>Notes:</strong> {notes_clean}</div>'
            if notes_clean else ""
        )

        card_html = (
            f'<div class="spa-grid-card {has_notes_class}">'
            f'<div class="spa-card-header">'
            f'<div class="spa-grid-title">{room_str}</div>'
            f'<div class="spa-grid-subtitle"><strong>Therapist:</strong> {therapist_str}</div>'
            f'</div>'
            f'{notes_html}'
            f'</div>'
        )
        cards_html_list.append(card_html)

    cards_html = "".join(cards_html_list)

    st.markdown(f"""
    <style>
        .spa-breakroom-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(21%, 1fr));
            grid-auto-rows: 1fr;
            gap: 1.5vh 1.3vw;
            /* 80vh cuts the bottom empty gap in half while avoiding TV bezel cutoff */
            height: 80vh;
            width: 100%;
            max-width: 100% !important;
            box-sizing: border-box;
        }}
        .spa-grid-card {{
            container-type: size;
            border: 2px solid currentColor;
            border-radius: 1.4vh;
            padding: 2.5cqh 3cqi !important;
            display: flex;
            flex-direction: column;
            height: 100%;
            width: 100%;
            max-width: 100% !important;
            box-sizing: border-box;
            overflow: hidden;
        }}
        .spa-grid-card.no-notes {{
            justify-content: center;
            align-items: center;
        }}
        .spa-grid-card.has-notes {{
            justify-content: flex-start;
            align-items: stretch;
            padding: 2cqh 3cqi !important;
        }}
        .spa-grid-card > div {{
            width: 100% !important;
            max-width: 100% !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            box-sizing: border-box !important;
            word-break: normal !important;
            overflow-wrap: break-word !important;
        }}
        .spa-card-header {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center !important;
            gap: 1.2cqh;
            flex-shrink: 0;
        }}
        /* Extra-large fonts when card has NO notes */
        .spa-grid-card.no-notes .spa-grid-title {{
            text-align: center !important;
            font-size: clamp(14px, min(13.5cqi, 30cqh), 5.5rem) !important;
            font-weight: 800 !important;
            line-height: 1.1 !important;
            margin: 0 !important;
        }}
        .spa-grid-card.no-notes .spa-grid-subtitle {{
            text-align: center !important;
            font-size: clamp(12px, min(10.5cqi, 23cqh), 4.0rem) !important;
            line-height: 1.15 !important;
            margin: 0 !important;
        }}
        /* Slightly larger but balanced header when card HAS notes */
        .spa-grid-card.has-notes .spa-grid-title {{
            text-align: center !important;
            font-size: clamp(12px, min(10.5cqi, 20cqh), 4.2rem) !important;
            font-weight: 800 !important;
            line-height: 1.1 !important;
            margin: 0 !important;
        }}
        .spa-grid-card.has-notes .spa-grid-subtitle {{
            text-align: center !important;
            font-size: clamp(11px, min(8.5cqi, 15.5cqh), 3.2rem) !important;
            line-height: 1.15 !important;
            margin: 0 !important;
        }}
        .spa-grid-notes {{
            flex: 1;
            min-height: 0;
            margin-top: 1.5cqh !important;
            padding-top: 1.5cqh !important;
            border-top: 1px solid rgba(128, 128, 128, 0.35);
            text-align: left !important;
            font-size: clamp(10px, min(7.5cqi, 14cqh), 2.6rem) !important;
            line-height: 1.22 !important;
            white-space: pre-wrap !important;
            overflow: hidden;
            opacity: 0.94;
        }}
    </style>
    <div class="spa-breakroom-grid">{cards_html}</div>
    """, unsafe_allow_html=True)


def apply_theme(hide_sidebar=False, compact_top=False):
    if not hide_sidebar:
        render_sidebar()

    top_space_css = """
        [data-testid="stHeader"] {
            background: transparent !important;
            height: 0px !important;
            min-height: 0px !important;
        }
        [data-testid="stToolbar"], [data-testid="collapsedControl"] {
            top: 1.5vh !important;
        }
        .block-container, [data-testid="stMainBlockContainer"] {
            padding-top: 3.2vh !important;
            padding-bottom: 1vh !important;
            padding-left: 3.2vw !important;
            padding-right: 3.2vw !important;
            max-width: 100% !important;
        }
        [data-testid="stVerticalBlock"] {
            gap: 0.5vh !important;
        }
        h1 {
            font-size: clamp(1.2rem, 4.0vh, 3.0rem) !important;
            margin-top: 0px !important;
            padding-top: 0px !important;
            margin-bottom: 0.8vh !important;
            line-height: 1.1 !important;
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