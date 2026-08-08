import streamlit as st

from pages import add_food, dashboard, goals
from services.supabase import get_profile, get_supabase, save_profile


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Macro",
    layout="wide",
    initial_sidebar_state="expanded",
)


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
# Background   #0B0E1A (page) / #131829 (surface) / #1A2036 (raised)
# Text         #ECEDF5 (primary) / #8B92AC (muted) / #565D78 (faint)
# Border       #262C46
# Accent       #8B7CF6 (violet) — primary actions, active nav/tab
#              state, focus rings only
# Type         Inter, system fallback stack
# Radius       8px, shadow none — structure comes from the border
#
# Mobile-first: base rules target narrow viewports; the >768px block
# only adds breathing room, it never changes structure.

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
        padding-bottom: 5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small {
        color: var(--text-muted) !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: var(--border) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        border-radius: var(--radius);
        padding: 8px 10px;
        margin-bottom: 2px;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: var(--surface-raised);
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

    h2 {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
    }

    h3 {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    p, span, label, div, li {
        color: var(--text);
    }

    .stCaption, small, [data-testid="stCaptionContainer"] {
        color: var(--text-muted) !important;
    }

    a { color: var(--accent) !important; }

    /* ---------- DIVIDERS ---------- */

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

    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.75rem;
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

    .stButton > button[kind="primary"] p {
        color: var(--accent-text) !important;
    }

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

    input::placeholder, textarea::placeholder {
        color: var(--text-faint) !important;
    }

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

    li[role="option"] {
        background: var(--surface-raised) !important;
        color: var(--text) !important;
    }

    li[role="option"]:hover,
    li[aria-selected="true"] {
        background: var(--surface) !important;
        color: var(--accent) !important;
    }

    /* ---------- SEGMENTED RADIO (Category / Meal pickers) ----------
       Scoped to .main so the sidebar nav radio (styled above) is
       untouched. */

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

    .main div[data-testid="stRadio"] input[type="radio"] {
        display: none;
    }

    /* ---------- TABS ---------- */

    button[data-baseweb="tab"] {
        font-weight: 500;
        font-size: 0.9rem;
        color: var(--text-muted) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--text) !important;
    }

    div[data-baseweb="tab-highlight"] {
        background-color: var(--accent) !important;
    }

    div[data-baseweb="tab-border"] {
        background-color: var(--border) !important;
    }

    /* ---------- PROGRESS ---------- */

    .stProgress > div > div > div {
        background: var(--accent) !important;
    }

    .stProgress > div > div {
        background: var(--border) !important;
    }

    .progress-label {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-bottom: 4px;
    }

    /* ---------- ALERTS ---------- */

    div[data-testid="stAlert"] {
        border-radius: var(--radius);
        border: 1px solid var(--border);
        background: var(--surface) !important;
    }

    div[data-testid="stAlert"] p {
        color: var(--text) !important;
    }

    /* ---------- MOBILE ---------- */

    @media (min-width: 768px) {

        .block-container {
            padding-top: 2.5rem;
        }

        h1 {
            font-size: 2rem !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


supabase = get_supabase()


# ============================================================
# SESSION STATE
# ============================================================

if "session" not in st.session_state:
    st.session_state.session = None

if "user" not in st.session_state:
    st.session_state.user = None


# Restore the Supabase session if Streamlit state was lost
if st.session_state.user is None:
    try:
        current_session = supabase.auth.get_session()

        if current_session and current_session.user:
            st.session_state.session = current_session
            st.session_state.user = current_session.user

    except Exception:
        st.session_state.session = None
        st.session_state.user = None

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

profile = get_profile(user_id)

if profile is None:
    save_profile(user_id, {})
    profile = get_profile(user_id)


with st.sidebar:

    st.markdown("### Macro")
    st.caption(st.session_state.user.email)

    st.divider()

    page = st.radio(
        "Navigation",
        ["Dashboard", "Add food", "Goals"],
        label_visibility="collapsed",
    )

    st.divider()

    if st.button("Log out", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.session = None
        st.session_state.user = None
        st.rerun()


# ============================================================
# ROUTING
# ============================================================

if page == "Dashboard":
    dashboard.render(user_id, profile)

elif page == "Add food":
    add_food.render(user_id)

elif page == "Goals":
    goals.render(user_id, profile)
