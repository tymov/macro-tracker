from datetime import datetime, timedelta

import extra_streamlit_components as stx
import streamlit as st

from pages import add_food, dashboard, goals
from services.supabase import get_profile, get_supabase


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(page_title="Macro", layout="wide")


# ============================================================
# THEME
# ============================================================
#
# Hardcoded dark navy/purple design system — does not follow the
# browser/OS light-dark preference. Paired with .streamlit/config.toml
# (base="dark" + matching colors) so native BaseWeb components that
# render outside this DOM tree — dropdown menus, calendar popovers,
# tooltips — inherit the same palette instead of falling back to
# Streamlit's stock dark theme.
#
# Navigation lives in a single st.container(key="main_nav") block —
# giving it a stable "st-key-main_nav" class is what lets the media
# query below pin it to the bottom of the screen on mobile instead
# of the old collapsible sidebar, which was the root of the "tabs
# show nothing" mobile bug (sidebar collapse/expand is the flakiest
# part of Streamlit on small screens).

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #0B0E1A;
        --surface: #131829;
        --surface-raised: #1A2036;
        --border: #262C46;
        --text: #ECEDF5;
        --text-muted: #8B92AC;
        --text-faint: #565D78;
        --accent: #8B7CF6;
        --accent-hover: #7A6AE8;
        --accent-text: #FFFFFF;
        --radius: 8px;
    }

    html, body, * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont,
            'Segoe UI', Roboto, sans-serif !important;
    }

    /* ---------- GLOBAL ---------- */

    .stApp, [data-testid="stAppViewContainer"], .main {
        background: var(--bg) !important;
    }

    header[data-testid="stHeader"] {
        background: var(--bg) !important;
    }

    .block-container {
        max-width: 720px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* ---------- HEADINGS & TEXT ---------- */

    h1, h2, h3, h4, h5, h6 {
        color: var(--text) !important;
    }

    h1 {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }

    h2 { font-size: 1.15rem !important; font-weight: 600 !important; }
    h3 { font-size: 1rem !important; font-weight: 600 !important; }

    p, span, label, div, li { color: var(--text); }

    .stCaption, small, [data-testid="stCaptionContainer"] {
        color: var(--text-muted) !important;
    }

    a { color: var(--accent) !important; }

    hr {
        border-color: var(--border) !important;
        margin: 1.25rem 0 !important;
    }

    /* ---------- METRIC CARDS ---------- */

    div[data-testid="metric-container"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 14px;
        box-shadow: none;
    }

    div[data-testid="metric-container"] label {
        color: var(--text-muted) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-weight: 600;
        font-size: 1.35rem;
        color: var(--text) !important;
    }

    /* ---------- CONTAINERS / BORDERED BLOCKS ---------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--border) !important;
        border-radius: var(--radius) !important;
        background: var(--surface) !important;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button {
        border-radius: var(--radius);
        border: 1px solid var(--border);
        font-weight: 500;
        min-height: 40px;
        background: var(--surface-raised) !important;
        color: var(--text) !important;
        box-shadow: none;
    }

    .stButton > button:hover {
        border-color: var(--accent);
        color: var(--accent) !important;
    }

    .stButton > button[kind="primary"] {
        background: var(--accent) !important;
        border-color: var(--accent);
        color: var(--accent-text) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--accent-hover) !important;
        border-color: var(--accent-hover);
        color: var(--accent-text) !important;
    }

    .stButton > button[kind="primary"] p { color: var(--accent-text) !important; }

    /* ---------- TEXT / NUMBER INPUTS ---------- */

    input, textarea {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
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
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
    }

    /* ---------- SELECT / DROPDOWN (incl. portal popover) ---------- */

    div[data-baseweb="select"] > div {
        background: var(--surface) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
        border-radius: var(--radius) !important;
    }

    div[data-baseweb="popover"] ul[role="listbox"],
    div[data-baseweb="menu"] {
        background: var(--surface-raised) !important;
        border: 1px solid var(--border) !important;
    }

    li[role="option"] { background: var(--surface-raised) !important; color: var(--text) !important; }

    li[role="option"]:hover, li[aria-selected="true"] {
        background: var(--surface) !important;
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
        border-radius: var(--radius);
        padding: 8px 14px;
        margin: 0 !important;
        cursor: pointer;
    }

    .main div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) {
        background: var(--accent);
        border-color: var(--accent);
    }

    .main div[data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked) p {
        color: var(--accent-text) !important;
    }

    .main div[data-testid="stRadio"] input[type="radio"] { display: none; }

    /* ---------- TABS ---------- */

    button[data-baseweb="tab"] { font-weight: 500; font-size: 0.9rem; color: var(--text-muted) !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: var(--text) !important; }
    div[data-baseweb="tab-highlight"] { background-color: var(--accent) !important; }
    div[data-baseweb="tab-border"] { background-color: var(--border) !important; }

    /* ---------- PROGRESS ---------- */

    .stProgress > div > div > div { background: var(--accent) !important; }
    .stProgress > div > div { background: var(--border) !important; }
    .progress-label { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 4px; }

    /* ---------- ALERTS ---------- */

    div[data-testid="stAlert"] {
        border-radius: var(--radius);
        border: 1px solid var(--border);
        background: var(--surface) !important;
    }

    div[data-testid="stAlert"] p { color: var(--text) !important; }

    /* ---------- MACRO RINGS ---------- */

    .ring-row {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        margin: 4px 0 8px 0;
    }

    .ring-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
    }

    .ring {
        width: 68px;
        height: 68px;
        border-radius: 50%;
        background: conic-gradient(var(--accent) calc(var(--pct) * 360deg), var(--border) 0deg);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 6px;
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

    .ring-value { font-weight: 600; font-size: 0.8rem; color: var(--text); }
    .ring-label { font-size: 0.75rem; color: var(--text-muted); margin-top: 6px; font-weight: 500; }
    .ring-target { font-size: 0.65rem; color: var(--text-faint); }

    /* ---------- HISTORY STRIP ---------- */

    .st-key-history_strip [data-testid="column"] { padding: 0 3px; }

    .st-key-history_strip .stButton > button {
        min-height: 56px;
        white-space: pre-line;
        font-size: 0.75rem;
        line-height: 1.3;
    }

    /* ---------- MAIN NAV — top on desktop, fixed bottom on mobile ---------- */

    .st-key-main_nav div[role="radiogroup"] {
        justify-content: center;
    }

    .st-key-main_nav div[role="radiogroup"] label {
        flex: 1;
        text-align: center;
        justify-content: center;
        display: flex;
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

        .block-container {
            padding-top: 2.5rem;
            padding-bottom: 5.5rem;
        }

        h1 { font-size: 2rem !important; }
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
    """Stores the refresh token in a long-lived cookie so a dropped
    connection or full page reload (common on mobile — backgrounding
    the browser, locking the phone) can silently restore the login
    instead of bouncing back to the login screen."""

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
# RESTORE SESSION FROM COOKIE (if we don't already have one)
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
            <p style="color:#8B92AC; font-size:0.9rem;">Track what you eat.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_signup = st.tabs(["Log in", "Create account"])

    with tab_login:

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Log in", type="primary", use_container_width=True):

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

        if st.button("Create account", use_container_width=True):

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

# Profiles table isn't pre-populated with an empty row anymore — an
# insert with only `id` set fails immediately if any other column in
# `profiles` is NOT NULL without a default, which was likely the
# actual cause of goals silently failing to save. A row now only gets
# written the first time the person actually saves their goals.
profile = get_profile(user_id) or {}


# ============================================================
# HEADER
# ============================================================

h1, h2, h3 = st.columns([3, 1.3, 1.1])

with h1:
    st.markdown("### Macro")
    st.caption(st.session_state.user.email)

with h2:
    if st.button("Add / Scan", use_container_width=True):
        st.session_state.pop("selected_product", None)
        st.query_params["page"] = "Add food"
        st.rerun()

with h3:
    if st.button("Log out", use_container_width=True):
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
# NAVIGATION
# ============================================================

PAGE_NAMES = ["Dashboard", "Add food", "Goals"]

query_page = st.query_params.get("page", "Dashboard")
default_index = PAGE_NAMES.index(query_page) if query_page in PAGE_NAMES else 0

with st.container(key="main_nav"):
    page = st.radio(
        "Navigation",
        PAGE_NAMES,
        index=default_index,
        horizontal=True,
        label_visibility="collapsed",
        key="nav_radio",
    )

if page != query_page:
    st.query_params["page"] = page

st.write("")


# ============================================================
# ROUTING
# ============================================================

if page == "Dashboard":
    dashboard.render(user_id, profile)

elif page == "Add food":
    add_food.render(user_id)

elif page == "Goals":
    goals.render(user_id, profile)
