from datetime import datetime, timedelta

import extra_streamlit_components as stx
import streamlit as st

from views import add_food, dashboard, goals
from services.supabase import get_profile, get_supabase


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(page_title="Macro", layout="wide")

# IMPORTANT: delete the top-level `pages/` folder from this repo.
# Streamlit auto-generates its own sidebar navigation for any folder
# literally named `pages/` next to app.py, regardless of whether
# anything imports from it. That's the second nav you're seeing —
# app.py never imports pages/, it only imports views/ below, so
# pages/ is dead weight that's actively fighting the custom nav.
# `components/macro_progress.py` is similarly unused and can go too.


# ============================================================
# THEME — mobile-app-first, minimal, dark navy/purple
# ============================================================

st.markdown(
    """
    <style>

    :root {
        --bg: #0B0E17;
        --surface: #141826;
        --surface-raised: #1B2033;
        --border: #232840;
        --text: #F1F2F8;
        --text-muted: #9298B0;
        --text-faint: #565D78;
        --accent: #8B5CF6;
        --accent-soft: rgba(139, 92, 246, 0.14);
        --accent-hover: #7C4DEE;
        --accent-text: #FFFFFF;
        --danger: #F87171;
        --radius-lg: 18px;
        --radius-md: 14px;
        --radius-sm: 10px;
    }

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
            Inter, Roboto, sans-serif;
    }

    /* ---------- GLOBAL ---------- */

    .stApp, [data-testid="stAppViewContainer"], .main {
        background: var(--bg) !important;
    }

    header[data-testid="stHeader"] {
        background: var(--bg) !important;
        height: 0;
    }

    /* Kill Streamlit's own multipage sidebar/nav entirely, in case
       pages/ hasn't been deleted yet — belt and suspenders. */
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    .block-container {
        max-width: 480px;
        margin: 0 auto;
        padding: 12px 16px 96px 16px;
    }

    /* ---------- TYPE ---------- */

    h1, h2, h3, h4, h5, h6 { color: var(--text) !important; }

    h1 {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem !important;
    }

    h2 { font-size: 1.05rem !important; font-weight: 600 !important; }
    h3 { font-size: 0.95rem !important; font-weight: 600 !important; }

    p, span, label, div, li { color: var(--text); }

    .stCaption, small, [data-testid="stCaptionContainer"] {
        color: var(--text-muted) !important;
        font-size: 0.8rem !important;
    }

    a { color: var(--accent) !important; }

    hr {
        border-color: var(--border) !important;
        margin: 1rem 0 !important;
        opacity: 0.6;
    }

    /* ---------- CARDS / BORDERED CONTAINERS ---------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--surface) !important;
    }

    /* ---------- METRICS ---------- */

    div[data-testid="metric-container"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 12px 14px;
    }

    div[data-testid="metric-container"] label {
        color: var(--text-muted) !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-weight: 700;
        font-size: 1.25rem;
        color: var(--text) !important;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button {
        border-radius: var(--radius-sm);
        border: 1px solid var(--border);
        font-weight: 500;
        min-height: 42px;
        background: var(--surface-raised) !important;
        color: var(--text) !important;
        box-shadow: none;
        transition: background 0.15s ease, border-color 0.15s ease;
    }

    .stButton > button:hover {
        border-color: var(--accent);
        color: var(--accent) !important;
    }

    .stButton > button p { display: flex; align-items: center; gap: 6px; }

    .stButton > button[kind="primary"] {
        background: var(--accent) !important;
        border-color: var(--accent);
        color: var(--accent-text) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--accent-hover) !important;
        border-color: var(--accent-hover);
    }

    .stButton > button[kind="primary"] p { color: var(--accent-text) !important; }

    /* Compact icon-only buttons (e.g. remove row) */
    .stButton > button:has(> div > span[data-testid="stIconMaterial"]:only-child) {
        min-height: 34px;
        min-width: 34px;
        padding: 0;
    }

    /* ---------- INPUTS ---------- */

    input, textarea {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text) !important;
    }

    input:focus, textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }

    input::placeholder, textarea::placeholder { color: var(--text-faint) !important; }

    div[data-baseweb="input"], div[data-baseweb="textarea"],
    div[data-baseweb="base-input"] {
        background: var(--surface) !important;
        border-color: var(--border) !important;
    }

    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {
        background: var(--surface) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
    }

    .stTextInput label, .stNumberInput label, .stSelectbox label,
    .stTextArea label {
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
    }

    /* ---------- SELECT / DROPDOWN ---------- */

    div[data-baseweb="select"] > div {
        background: var(--surface) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
        border-radius: var(--radius-sm) !important;
    }

    div[data-baseweb="popover"] ul[role="listbox"],
    div[data-baseweb="menu"] {
        background: var(--surface-raised) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
    }

    li[role="option"] { background: var(--surface-raised) !important; color: var(--text) !important; }

    li[role="option"]:hover, li[aria-selected="true"] {
        background: var(--accent-soft) !important;
        color: var(--accent) !important;
    }

    /* ---------- SEGMENTED RADIO (Category / Meal pickers) ---------- */

    .main div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
    }

    .main div[data-testid="stRadio"] > div[role="radiogroup"] label {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 7px 14px;
        margin: 0 !important;
        cursor: pointer;
        font-size: 0.85rem;
    }

    .main div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) {
        background: var(--accent-soft);
        border-color: var(--accent);
    }

    .main div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) p {
        color: var(--accent) !important;
        font-weight: 600;
    }

    .main div[data-testid="stRadio"] input[type="radio"] { display: none; }

    /* ---------- PROGRESS ---------- */

    .stProgress > div > div > div { background: var(--accent) !important; }
    .stProgress > div > div { background: var(--border) !important; }
    .progress-label { font-size: 0.78rem; color: var(--text-muted); margin-bottom: 4px; }

    /* ---------- ALERTS ---------- */

    div[data-testid="stAlert"] {
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        background: var(--surface) !important;
    }

    div[data-testid="stAlert"] p { color: var(--text) !important; }

    /* ---------- MACRO RINGS ---------- */

    .ring-row {
        display: flex;
        justify-content: space-between;
        gap: 6px;
        margin: 6px 0 4px 0;
    }

    .ring-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
    }

    .ring {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: conic-gradient(var(--accent) calc(var(--pct) * 360deg), var(--border) 0deg);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 5px;
    }

    .ring-inner {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: var(--bg);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .ring-value { font-weight: 700; font-size: 0.78rem; color: var(--text); }
    .ring-label { font-size: 0.72rem; color: var(--text-muted); margin-top: 6px; font-weight: 500; }
    .ring-target { font-size: 0.62rem; color: var(--text-faint); }

    /* ---------- HISTORY STRIP ---------- */

    .st-key-history_strip [data-testid="column"] { padding: 0 3px; }

    .st-key-history_strip .stButton > button {
        min-height: 52px;
        border-radius: var(--radius-sm);
        white-space: pre-line;
        font-size: 0.72rem;
        line-height: 1.3;
    }

    /* ---------- BOTTOM TAB BAR ---------- */

    .st-key-main_nav div[role="radiogroup"] {
        justify-content: space-around;
        gap: 0 !important;
    }

    .st-key-main_nav div[role="radiogroup"] label {
        flex: 1;
        text-align: center;
        justify-content: center;
        display: flex;
        background: transparent !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 6px 4px !important;
    }

    .st-key-main_nav div[role="radiogroup"] label p {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2px;
        font-size: 0.68rem !important;
        color: var(--text-muted) !important;
    }

    .st-key-main_nav div[role="radiogroup"] label span[data-testid="stIconMaterial"] {
        font-size: 1.3rem !important;
        color: var(--text-muted) !important;
    }

    .st-key-main_nav div[role="radiogroup"] label:has(input:checked) {
        background: var(--accent-soft) !important;
    }

    .st-key-main_nav div[role="radiogroup"] label:has(input:checked) p,
    .st-key-main_nav div[role="radiogroup"] label:has(input:checked) span[data-testid="stIconMaterial"] {
        color: var(--accent) !important;
    }

    @media (max-width: 768px) {

        .st-key-main_nav {
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 999;
            background: var(--surface);
            border-top: 1px solid var(--border);
            padding: 8px 10px calc(8px + env(safe-area-inset-bottom, 0px));
            margin: 0 !important;
        }

        .block-container { padding-bottom: 92px; }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


supabase = get_supabase()
cookie_manager = stx.CookieManager(key="cookie_manager")

COOKIE_NAME = "mt_refresh_token"


# ============================================================
# SESSION STATE
# ============================================================

if "session" not in st.session_state:
    st.session_state.session = None

if "user" not in st.session_state:
    st.session_state.user = None


def _persist_session(session):
    cookie_manager.set(
        COOKIE_NAME,
        session.refresh_token,
        expires_at=datetime.now() + timedelta(days=30),
        key="set_refresh_token",
    )


def _clear_session_cookie():
    try:
        cookie_manager.delete(COOKIE_NAME, key="delete_refresh_token")
    except Exception:
        pass


# ============================================================
# RESTORE SESSION FROM COOKIE
# ============================================================

if st.session_state.user is None:

    cookies = cookie_manager.get_all()

    if cookies is not None:

        refresh_token = cookies.get(COOKIE_NAME)

        if refresh_token:
            try:
                auth_response = supabase.auth.refresh_session(refresh_token)
                st.session_state.session = auth_response.session
                st.session_state.user = auth_response.user
                _persist_session(auth_response.session)

            except Exception:
                _clear_session_cookie()


# ============================================================
# AUTHENTICATION
# ============================================================

def login_screen():

    st.markdown(
        """
        <div style="max-width:380px; margin:64px auto 32px auto; text-align:center;">
            <h1 style="margin-bottom:4px;">Macro</h1>
            <p style="color:#9298B0; font-size:0.9rem;">Track what you eat.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_signup = st.tabs(["Log in", "Create account"])

    with tab_login:

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Log in", type="primary", use_container_width=True, icon=":material/login:"):

            try:
                response = supabase.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
                st.session_state.session = response.session
                st.session_state.user = response.user
                _persist_session(response.session)
                st.rerun()

            except Exception:
                st.error("Could not log in. Check your email and password.")

    with tab_signup:

        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Create account", use_container_width=True, icon=":material/person_add:"):

            try:
                response = supabase.auth.sign_up({"email": email, "password": password})

                if response.session:
                    st.session_state.session = response.session
                    st.session_state.user = response.user
                    _persist_session(response.session)
                    st.success("Account created.")
                    st.rerun()
                else:
                    st.success("Account created. Check your email to verify it.")

            except Exception as e:
                st.error(str(e))


# ============================================================
# APP ENTRY
# ============================================================

if st.session_state.user is None:
    login_screen()
    st.stop()


user_id = st.session_state.user.id
profile = get_profile(user_id) or {}


# ============================================================
# HEADER
# ============================================================

h1, h2, h3 = st.columns([3, 1.1, 1.1])

with h1:
    st.markdown("### Macro")
    st.caption(st.session_state.user.email)

with h2:
    if st.button("Add", use_container_width=True, icon=":material/add:"):
        st.session_state.pop("selected_product", None)
        st.query_params["page"] = "Add food"
        st.rerun()

with h3:
    if st.button("Log out", use_container_width=True, icon=":material/logout:"):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        _clear_session_cookie()
        st.session_state.session = None
        st.session_state.user = None
        st.rerun()

st.divider()


# ============================================================
# NAVIGATION — single tab bar, icon + label, pinned to bottom
# on mobile via CSS above. This is the ONLY nav in the app;
# make sure the pages/ folder is deleted so Streamlit doesn't
# also render its own sidebar nav on top of this.
# ============================================================

PAGE_NAMES = ["Dashboard", "Add food", "Goals"]

NAV_ICONS = {
    "Dashboard": "space_dashboard",
    "Add food": "add_circle",
    "Goals": "flag",
}

query_page = st.query_params.get("page", "Dashboard")
default_index = PAGE_NAMES.index(query_page) if query_page in PAGE_NAMES else 0

with st.container(key="main_nav"):
    page = st.radio(
        "Navigation",
        PAGE_NAMES,
        index=default_index,
        horizontal=True,
        label_visibility="collapsed",
        format_func=lambda name: f":material/{NAV_ICONS[name]}:\n\n{name}",
        key="nav_radio",
    )

if page != query_page:
    st.query_params["page"] = page


# ============================================================
# ROUTING
# ============================================================

if page == "Dashboard":
    dashboard.render(user_id, profile)

elif page == "Add food":
    add_food.render(user_id)

elif page == "Goals":
    goals.render(user_id, profile)
