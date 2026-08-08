import streamlit as st
import requests
from datetime import date, datetime

from supabase import create_client, Client


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Macro",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS — MOBILE-FIRST DESIGN SYSTEM
# ============================================================

st.markdown(
    """
    <style>

    /* =========================================================
       DESIGN TOKENS
       ========================================================= */

    :root {
        --bg: #f5f6f2;
        --surface: #ffffff;
        --surface-soft: #eef1eb;
        --surface-muted: #f8f9f7;
        --ink: #182019;
        --ink-soft: #566057;
        --muted: #7a837c;
        --line: #e1e5df;
        --line-strong: #d2d8d0;
        --primary: #5d7f61;
        --primary-dark: #45664b;
        --primary-soft: #e3ece2;
        --accent: #e89b57;
        --danger: #c95d57;
        --radius-sm: 10px;
        --radius-md: 16px;
        --radius-lg: 22px;
        --shadow-sm: 0 1px 2px rgba(24, 32, 25, 0.04);
        --shadow-md: 0 8px 28px rgba(24, 32, 25, 0.07);
    }

    /* =========================================================
       GLOBAL APP
       ========================================================= */

    html, body, [class*="css"] {
        font-family:
            Inter,
            ui-sans-serif,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
        color: var(--ink);
    }

    .stApp {
        background: var(--bg);
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(
                circle at 100% 0%,
                rgba(93, 127, 97, 0.08),
                transparent 28rem
            ),
            var(--bg);
    }

    .main .block-container {
        max-width: 1080px;
        padding: 1.25rem 1rem 6rem;
    }

    /* Remove Streamlit's excess top whitespace */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0.75rem;
    }

    /* Hide the default decoration/header chrome where possible */
    [data-testid="stHeader"] {
        background: transparent;
    }

    /* =========================================================
       TYPOGRAPHY
       ========================================================= */

    h1, h2, h3 {
        color: var(--ink) !important;
        letter-spacing: -0.035em !important;
    }

    h1 {
        font-size: clamp(1.9rem, 7vw, 2.75rem) !important;
        line-height: 1.05 !important;
        font-weight: 780 !important;
        margin: 0 0 0.35rem !important;
    }

    h2 {
        font-size: clamp(1.35rem, 5vw, 1.8rem) !important;
        line-height: 1.15 !important;
        font-weight: 720 !important;
    }

    h3 {
        font-size: 1.05rem !important;
        line-height: 1.25 !important;
        font-weight: 700 !important;
    }

    p, label, .stCaption {
        color: var(--ink-soft);
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    hr {
        border: 0 !important;
        border-top: 1px solid var(--line) !important;
        margin: 1.5rem 0 !important;
    }

    /* =========================================================
       SIDEBAR — DESKTOP DRAWER / MOBILE MENU
       ========================================================= */

    section[data-testid="stSidebar"] {
        background: #182019;
        border-right: 0;
    }

    section[data-testid="stSidebar"] > div {
        background: #182019;
        padding: 1.1rem 0.85rem;
    }

    section[data-testid="stSidebar"] * {
        color: #f7faf5 !important;
    }

    section[data-testid="stSidebar"] hr {
        border-top-color: rgba(255,255,255,0.10) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        color: #ffffff !important;
        font-size: 1.65rem !important;
        margin-bottom: 0.1rem !important;
    }

    /* Navigation radio */
    section[data-testid="stSidebar"] [role="radiogroup"] {
        gap: 0.35rem;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] > label {
        border-radius: 13px;
        padding: 0.75rem 0.85rem;
        transition: background 0.15s ease;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] [role="radiogroup"] > label[data-checked="true"] {
        background: rgba(255,255,255,0.13);
    }

    /* =========================================================
       BUTTONS
       ========================================================= */

    .stButton > button {
        width: 100%;
        min-height: 46px;
        border-radius: 13px;
        border: 1px solid var(--line);
        background: var(--surface);
        color: var(--ink);
        font-size: 0.93rem;
        font-weight: 680;
        box-shadow: var(--shadow-sm);
        transition:
            transform 0.12s ease,
            box-shadow 0.12s ease,
            background 0.12s ease;
    }

    .stButton > button:hover {
        border-color: var(--line-strong);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    .stButton > button[kind="primary"] {
        background: var(--primary);
        border-color: var(--primary);
        color: #ffffff;
        box-shadow: 0 7px 18px rgba(93, 127, 97, 0.22);
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--primary-dark);
        border-color: var(--primary-dark);
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.07);
        border-color: rgba(255,255,255,0.10);
        color: #fff;
        box-shadow: none;
    }

    /* =========================================================
       INPUTS
       ========================================================= */

    input,
    textarea,
    [data-baseweb="select"] > div,
    [data-testid="stNumberInput"] > div {
        border-radius: 13px !important;
    }

    input,
    textarea {
        background: var(--surface) !important;
    }

    [data-baseweb="select"] > div {
        background: var(--surface) !important;
        border-color: var(--line) !important;
    }

    input:focus,
    textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(93, 127, 97, 0.12) !important;
    }

    [data-testid="stTextInput"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stSelectbox"] label {
        font-size: 0.82rem;
        font-weight: 650;
        color: var(--ink-soft) !important;
        margin-bottom: 0.25rem;
    }

    /* =========================================================
       TABS
       ========================================================= */

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: var(--surface-soft);
        padding: 0.3rem;
        border-radius: 14px;
        overflow-x: auto;
    }

    .stTabs [data-baseweb="tab"] {
        min-height: 42px;
        border-radius: 10px;
        padding: 0.45rem 0.8rem;
        color: var(--ink-soft);
        font-weight: 650;
        white-space: nowrap;
    }

    .stTabs [aria-selected="true"] {
        background: var(--surface);
        color: var(--ink) !important;
        box-shadow: var(--shadow-sm);
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }

    /* =========================================================
       METRIC CARDS
       ========================================================= */

    div[data-testid="metric-container"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        padding: 1rem;
        box-shadow: var(--shadow-sm);
        min-height: 108px;
    }

    div[data-testid="metric-container"] label {
        color: var(--muted) !important;
        font-size: 0.78rem;
        font-weight: 650;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--ink) !important;
        font-size: clamp(1.35rem, 6vw, 1.9rem);
        font-weight: 780;
        letter-spacing: -0.035em;
    }

    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* =========================================================
       PROGRESS
       ========================================================= */

    [data-testid="stProgress"] > div > div {
        height: 9px;
        border-radius: 999px;
        background: #dfe5dc;
    }

    [data-testid="stProgress"] > div > div > div {
        border-radius: 999px;
        background: var(--primary);
    }

    /* =========================================================
       CONTAINERS / CARDS
       ========================================================= */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface);
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-sm);
        padding: 0.2rem;
    }

    .food-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        padding: 1rem;
        margin-bottom: 0.7rem;
        box-shadow: var(--shadow-sm);
    }

    .food-name {
        color: var(--ink);
        font-weight: 720;
        font-size: 0.98rem;
        line-height: 1.25;
    }

    .food-meta {
        color: var(--muted);
        font-size: 0.82rem;
        margin-top: 0.25rem;
    }

    /* =========================================================
       ALERTS / STATUS
       ========================================================= */

    [data-testid="stAlert"] {
        border-radius: 13px;
        border: 1px solid var(--line);
        box-shadow: none;
    }

    /* =========================================================
       LOGIN SCREEN
       ========================================================= */

    .login-shell {
        max-width: 430px;
        margin: 7vh auto 0;
    }

    .login-brand {
        text-align: center;
        margin-bottom: 1.75rem;
    }

    .login-icon {
        width: 62px;
        height: 62px;
        margin: 0 auto 1rem;
        display: grid;
        place-items: center;
        border-radius: 18px;
        background: var(--primary-soft);
        font-size: 1.8rem;
        box-shadow: var(--shadow-sm);
    }

    .login-brand h1 {
        margin-bottom: 0.25rem !important;
    }

    .login-brand p {
        margin: 0;
        color: var(--muted);
    }

    /* =========================================================
       MOBILE-FIRST LAYOUT
       ========================================================= */

    @media (max-width: 768px) {

        .main .block-container {
            max-width: 100%;
            padding: 0.8rem 0.8rem 5rem;
        }

        [data-testid="stAppViewBlockContainer"] {
            padding-top: 0.45rem;
        }

        h1 {
            font-size: 1.85rem !important;
        }

        h2 {
            font-size: 1.35rem !important;
        }

        h3 {
            font-size: 1rem !important;
        }

        /* Stack Streamlit columns by making their contents comfortable */
        [data-testid="column"] {
            min-width: 0 !important;
        }

        /* Metrics become a compact 2x2 grid */
        div[data-testid="metric-container"] {
            min-height: 94px;
            padding: 0.8rem;
            border-radius: 15px;
        }

        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 1.35rem;
        }

        /* Make every important action thumb-friendly */
        .stButton > button {
            min-height: 48px;
        }

        input,
        [data-baseweb="select"] > div {
            min-height: 46px;
        }

        /* Keep tabs usable with a thumb */
        .stTabs [data-baseweb="tab-list"] {
            scrollbar-width: none;
        }

        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none;
        }

        /* Tighter cards */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 15px !important;
        }

        /* Login */
        .login-shell {
            margin: 5vh auto 0;
        }
    }

    /* =========================================================
       SMALL PHONES
       ========================================================= */

    @media (max-width: 430px) {

        .main .block-container {
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }

        div[data-testid="metric-container"] {
            padding: 0.7rem;
        }

        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 1.2rem;
        }

        .stTabs [data-baseweb="tab"] {
            padding-left: 0.65rem;
            padding-right: 0.65rem;
            font-size: 0.82rem;
        }
    }

    /* =========================================================
       REDUCE MOTION FOR ACCESSIBILITY
       ========================================================= */

    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            scroll-behavior: auto !important;
            transition: none !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SUPABASE
# ============================================================

@st.cache_resource
def get_supabase() -> Client:

    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


supabase = get_supabase()


# ============================================================
# SESSION STATE
# ============================================================

if "session" not in st.session_state:
    st.session_state.session = None

if "user" not in st.session_state:
    st.session_state.user = None


# ============================================================
# AUTHENTICATION
# ============================================================

def login_screen():

    st.markdown(
        """
        <div style="
            max-width:460px;
            margin:80px auto;
            text-align:center;
        ">
            <div style="font-size:3rem;">🥗</div>
            <h1>Macro</h1>
            <p style="color:#737780;">
                Your personal nutrition tracker.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_signup = st.tabs(
        ["Log in", "Create account"]
    )

    with tab_login:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Log in",
            type="primary",
            use_container_width=True,
        ):

            try:

                response = supabase.auth.sign_in_with_password(
                    {
                        "email": email,
                        "password": password,
                    }
                )

                st.session_state.session = response.session
                st.session_state.user = response.user

                st.rerun()

            except Exception as e:

                st.error(
                    "Could not log in. Check your email and password."
                )

    with tab_signup:

        email = st.text_input(
            "Email",
            key="signup_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        if st.button(
            "Create account",
            use_container_width=True,
        ):

            try:

                response = supabase.auth.sign_up(
                    {
                        "email": email,
                        "password": password,
                    }
                )

                if response.session:

                    st.session_state.session = response.session
                    st.session_state.user = response.user

                    st.success("Account created!")
                    st.rerun()

                else:

                    st.success(
                        "Account created. Check your email to verify it."
                    )

            except Exception as e:

                st.error(str(e))


# ============================================================
# PROFILE
# ============================================================

def get_profile():

    user_id = st.session_state.user.id

    response = (
        supabase
        .table("profiles")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    return response.data


def save_profile(data):

    user_id = st.session_state.user.id

    data["id"] = user_id

    supabase \
        .table("profiles") \
        .upsert(data) \
        .execute()


# ============================================================
# BMR / TDEE CALCULATOR
# ============================================================

def calculate_bmr(
    sex,
    weight,
    height,
    age,
):

    # Mifflin-St Jeor
    if sex == "male":

        return (
            10 * weight
            + 6.25 * height
            - 5 * age
            + 5
        )

    elif sex == "female":

        return (
            10 * weight
            + 6.25 * height
            - 5 * age
            - 161
        )

    else:

        # Neutral midpoint when "other" is selected
        return (
            10 * weight
            + 6.25 * height
            - 5 * age
            - 78
        )


ACTIVITY_MULTIPLIERS = {
    "Sedentary": 1.2,
    "Lightly active": 1.375,
    "Moderately active": 1.55,
    "Very active": 1.725,
    "Extremely active": 1.9,
}


def calculate_targets(
    bmr,
    activity,
    goal,
    weekly_change,
):

    tdee = bmr * ACTIVITY_MULTIPLIERS[activity]

    if goal == "Lose weight":

        calories = tdee - (
            abs(weekly_change) * 1100
        )

    elif goal == "Gain weight":

        calories = tdee + (
            abs(weekly_change) * 1100
        )

    else:

        calories = tdee

    calories = max(calories, 1200)

    # Protein-first approach
    protein = 1.8 * profile_weight

    # Fat around 25% of calories
    fat = (calories * 0.25) / 9

    # Remaining calories go to carbs
    carbs = (
        calories
        - (protein * 4)
        - (fat * 9)
    ) / 4

    return (
        round(tdee),
        round(calories),
        round(protein),
        round(carbs),
        round(fat),
    )


# ============================================================
# FOOD API
# ============================================================

OFF_URL = "https://world.openfoodfacts.org"


def search_open_food_facts(query):

    url = f"{OFF_URL}/cgi/search.pl"

    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 12,
        "fields": (
            "code,"
            "product_name,"
            "brands,"
            "quantity,"
            "image_front_small_url,"
            "nutriments"
        ),
    }

    headers = {
        "User-Agent": (
            "PersonalMacroTracker/1.0 "
            "(personal nutrition app)"
        )
    }

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json().get(
            "products",
            []
        )

    except Exception:

        return []


def get_product_by_barcode(barcode):

    url = (
        f"{OFF_URL}/api/v2/product/"
        f"{barcode}.json"
    )

    headers = {
        "User-Agent": (
            "PersonalMacroTracker/1.0 "
            "(personal nutrition app)"
        )
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") == 1:

            return data.get("product")

    except Exception:

        pass

    return None


def nutrition_from_product(product):

    nutrients = product.get(
        "nutriments",
        {}
    )

    return {
        "calories": nutrients.get(
            "energy-kcal_100g",
            0
        ) or 0,

        "protein": nutrients.get(
            "proteins_100g",
            0
        ) or 0,

        "carbs": nutrients.get(
            "carbohydrates_100g",
            0
        ) or 0,

        "fat": nutrients.get(
            "fat_100g",
            0
        ) or 0,

        "fiber": nutrients.get(
            "fiber_100g",
            0
        ) or 0,

        "sugar": nutrients.get(
            "sugars_100g",
            0
        ) or 0,

        "sodium": nutrients.get(
            "sodium_100g",
            0
        ) or 0,
    }


# ============================================================
# SAVE FOOD TO CACHE
# ============================================================

def cache_food(product):

    nutrients = nutrition_from_product(
        product
    )

    data = {

        "external_id": product.get("code"),

        "source": "open_food_facts",

        "barcode": product.get("code"),

        "name": (
            product.get("product_name")
            or "Unknown food"
        ),

        "brand": product.get(
            "brands"
        ),

        "serving_size": None,

        "serving_unit": "g",

        "calories": nutrients["calories"],

        "protein": nutrients["protein"],

        "carbs": nutrients["carbs"],

        "fat": nutrients["fat"],

        "fiber": nutrients["fiber"],

        "sugar": nutrients["sugar"],

        "sodium": nutrients["sodium"],

        "image_url": product.get(
            "image_front_small_url"
        ),

    }

    try:

        result = (
            supabase
            .table("foods")
            .upsert(
                data,
                on_conflict="source,external_id"
            )
            .execute()
        )

        return result.data[0]

    except Exception:

        return None


# ============================================================
# DASHBOARD
# ============================================================

def dashboard(profile):

    st.title("Good to see you 👋")

    st.caption(
        date.today().strftime(
            "%A, %d %B %Y"
        )
    )

    target_calories = (
        profile.get("calorie_target")
        or 0
    )

    target_protein = (
        profile.get("protein_target")
        or 0
    )

    target_carbs = (
        profile.get("carb_target")
        or 0
    )

    target_fat = (
        profile.get("fat_target")
        or 0
    )

    today_start = (
        f"{date.today()}T00:00:00"
    )

    logs = (
        supabase
        .table("food_logs")
        .select("*")
        .eq(
            "user_id",
            st.session_state.user.id
        )
        .gte(
            "eaten_at",
            today_start
        )
        .execute()
        .data
    )

    total_calories = sum(
        float(x["calories"] or 0)
        for x in logs
    )

    total_protein = sum(
        float(x["protein"] or 0)
        for x in logs
    )

    total_carbs = sum(
        float(x["carbs"] or 0)
        for x in logs
    )

    total_fat = sum(
        float(x["fat"] or 0)
        for x in logs
    )

    st.subheader("Today's overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Calories",
            f"{total_calories:.0f}",
            f"{target_calories - total_calories:.0f} left",
        )

    with c2:
        st.metric(
            "Protein",
            f"{total_protein:.0f} g",
            f"{target_protein - total_protein:.0f} g left",
        )

    with c3:
        st.metric(
            "Carbs",
            f"{total_carbs:.0f} g",
            f"{target_carbs - total_carbs:.0f} g left",
        )

    with c4:
        st.metric(
            "Fat",
            f"{total_fat:.0f} g",
            f"{target_fat - total_fat:.0f} g left",
        )

    st.write("")

    if target_calories:
        st.progress(
            min(
                total_calories
                / target_calories,
                1.0,
            )
        )

    st.divider()

    st.subheader("Today's meals")

    meals = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snacks"),
    ]

    for meal_key, meal_name in meals:

        meal_logs = [
            x
            for x in logs
            if x["meal"] == meal_key
        ]

        meal_total = sum(
            float(x["calories"] or 0)
            for x in meal_logs
        )

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(
                    f"### {meal_name}"
                )

            with col2:
                st.markdown(
                    f"**{meal_total:.0f} kcal**"
                )

            if meal_logs:

                for item in meal_logs:

                    cols = st.columns(
                        [4, 2, 1]
                    )

                    with cols[0]:
                        st.write(
                            item["food_name"]
                        )

                    with cols[1]:
                        st.write(
                            f'{item["quantity"]:.0f}'
                            f'{item["unit"]}'
                        )

                    with cols[2]:

                        if st.button(
                            "×",
                            key=f"delete_{item['id']}",
                        ):

                            (
                                supabase
                                .table("food_logs")
                                .delete()
                                .eq(
                                    "id",
                                    item["id"]
                                )
                                .execute()
                            )

                            st.rerun()

            else:

                st.caption(
                    "Nothing logged."
                )


# ============================================================
# GOALS PAGE
# ============================================================

def goals_page(profile):

    st.title("Your goals")
    st.caption(
        "Calculate your targets or set them manually."
    )

    st.subheader(
        "Your information"
    )

    c1, c2 = st.columns(2)

    with c1:

        age = st.number_input(
            "Age",
            min_value=13,
            max_value=100,
            value=int(
                profile.get("age") or 25
            ),
        )

        height = st.number_input(
            "Height (cm)",
            min_value=100.0,
            max_value=250.0,
            value=float(
                profile.get("height_cm") or 180
            ),
        )

        weight = st.number_input(
            "Weight (kg)",
            min_value=30.0,
            max_value=300.0,
            value=float(
                profile.get("weight_kg") or 80
            ),
        )

    with c2:

        sex = st.selectbox(
            "Sex",
            ["male", "female", "other"],
            index=[
                "male",
                "female",
                "other",
            ].index(
                profile.get("sex")
                or "male"
            ),
        )

        activity = st.selectbox(
            "Activity level",
            list(
                ACTIVITY_MULTIPLIERS.keys()
            ),
        )

        goal = st.selectbox(
            "Goal",
            [
                "Lose weight",
                "Maintain",
                "Gain weight",
            ],
        )

    weekly_change = st.number_input(
        "Desired weekly weight change (kg)",
        min_value=0.0,
        max_value=2.0,
        value=0.5,
        step=0.1,
    )

    global profile_weight
    profile_weight = weight

    if st.button(
        "🧮 Calculate my targets",
        type="primary",
    ):

        bmr = calculate_bmr(
            sex,
            weight,
            height,
            age,
        )

        tdee = (
            bmr
            * ACTIVITY_MULTIPLIERS[activity]
        )

        if goal == "Lose weight":
            calories = tdee - (
                weekly_change * 1100
            )

        elif goal == "Gain weight":
            calories = tdee + (
                weekly_change * 1100
            )

        else:
            calories = tdee

        calories = max(
            calories,
            1200,
        )

        protein = weight * 1.8

        fat = (
            calories * 0.25
        ) / 9

        carbs = (
            calories
            - protein * 4
            - fat * 9
        ) / 4

        st.session_state.calculated_targets = {
            "bmr": round(bmr),
            "tdee": round(tdee),
            "calories": round(calories),
            "protein": round(protein),
            "carbs": round(carbs),
            "fat": round(fat),
        }

    if (
        "calculated_targets"
        in st.session_state
    ):

        calc = (
            st.session_state
            .calculated_targets
        )

        st.divider()

        st.subheader(
            "Suggested targets"
        )

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "BMR",
                f"{calc['bmr']} kcal",
            )

            st.metric(
                "Estimated TDEE",
                f"{calc['tdee']} kcal",
            )

        with c2:

            st.metric(
                "Suggested calories",
                f"{calc['calories']} kcal",
            )

            st.write(
                f"Protein: **{calc['protein']} g**"
            )

            st.write(
                f"Carbs: **{calc['carbs']} g**"
            )

            st.write(
                f"Fat: **{calc['fat']} g**"
            )

        if st.button(
            "Use these targets",
            type="primary",
        ):

            save_profile(
                {
                    "age": age,
                    "sex": sex,
                    "height_cm": height,
                    "weight_kg": weight,
                    "goal": (
                        "lose_weight"
                        if goal == "Lose weight"
                        else
                        "gain_weight"
                        if goal == "Gain weight"
                        else
                        "maintain"
                    ),
                    "activity_level": (
                        activity
                        .lower()
                        .replace(
                            " ",
                            "_"
                        )
                    ),
                    "calorie_target": calc[
                        "calories"
                    ],
                    "protein_target": calc[
                        "protein"
                    ],
                    "carb_target": calc[
                        "carbs"
                    ],
                    "fat_target": calc[
                        "fat"
                    ],
                    "weekly_weight_change": (
                        weekly_change
                    ),
                }
            )

            st.success(
                "Your targets have been saved."
            )

            st.rerun()

    st.divider()

    st.subheader(
        "Or set them manually"
    )

    current_calories = float(
        profile.get(
            "calorie_target"
        ) or 2000
    )

    current_protein = float(
        profile.get(
            "protein_target"
        ) or 150
    )

    current_carbs = float(
        profile.get(
            "carb_target"
        ) or 200
    )

    current_fat = float(
        profile.get(
            "fat_target"
        ) or 65
    )

    c1, c2 = st.columns(2)

    with c1:

        manual_calories = st.number_input(
            "Calories",
            min_value=500.0,
            max_value=10000.0,
            value=current_calories,
            step=50.0,
        )

        manual_protein = st.number_input(
            "Protein (g)",
            min_value=0.0,
            max_value=1000.0,
            value=current_protein,
            step=5.0,
        )

    with c2:

        manual_carbs = st.number_input(
            "Carbs (g)",
            min_value=0.0,
            max_value=1000.0,
            value=current_carbs,
            step=5.0,
        )

        manual_fat = st.number_input(
            "Fat (g)",
            min_value=0.0,
            max_value=1000.0,
            value=current_fat,
            step=5.0,
        )

    if st.button(
        "Save manual targets",
    ):

        save_profile(
            {
                "age": age,
                "sex": sex,
                "height_cm": height,
                "weight_kg": weight,
                "calorie_target": manual_calories,
                "protein_target": manual_protein,
                "carb_target": manual_carbs,
                "fat_target": manual_fat,
            }
        )

        st.success(
            "Your goals have been updated."
        )

        st.rerun()


# ============================================================
# ADD FOOD PAGE
# ============================================================

def add_food_page():

    st.title("Add food")

    tab_search, tab_barcode, tab_quick = st.tabs(
        [
            "🔎 Search",
            "▣ Barcode",
            "⚡ Quick add",
        ]
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    with tab_search:

        query = st.text_input(
            "Search the food database",
            placeholder=(
                "e.g. Greek yogurt, chicken breast..."
            ),
        )

        if query:

            products = search_open_food_facts(
                query
            )

            if not products:

                st.info(
                    "No results found."
                )

            for i, product in enumerate(
                products
            ):

                name = (
                    product.get(
                        "product_name"
                    )
                    or "Unknown product"
                )

                brand = (
                    product.get("brands")
                    or ""
                )

                nutrients = nutrition_from_product(
                    product
                )

                with st.container(
                    border=True
                ):

                    c1, c2 = st.columns(
                        [4, 1]
                    )

                    with c1:

                        st.markdown(
                            f"### {name}"
                        )

                        if brand:
                            st.caption(
                                brand
                            )

                        st.write(
                            f"{nutrients['calories']:.0f} kcal "
                            f"· P {nutrients['protein']:.1f}g "
                            f"· C {nutrients['carbs']:.1f}g "
                            f"· F {nutrients['fat']:.1f}g "
                            f"per 100g"
                        )

                    with c2:

                        if st.button(
                            "Add",
                            key=f"select_{i}",
                            type="primary",
                        ):

                            st.session_state.selected_product = (
                                product
                            )

                            st.rerun()

        # Selected food

        if (
            "selected_product"
            in st.session_state
        ):

            product = (
                st.session_state
                .selected_product
            )

            nutrients = nutrition_from_product(
                product
            )

            st.divider()

            st.subheader(
                product.get(
                    "product_name"
                )
                or "Food"
            )

            meal = st.selectbox(
                "Meal",
                [
                    "breakfast",
                    "lunch",
                    "dinner",
                    "snack",
                ],
            )

            quantity = st.number_input(
                "Quantity (g)",
                min_value=1.0,
                value=100.0,
                step=1.0,
            )

            multiplier = (
                quantity / 100
            )

            calories = (
                nutrients["calories"]
                * multiplier
            )

            protein = (
                nutrients["protein"]
                * multiplier
            )

            carbs = (
                nutrients["carbs"]
                * multiplier
            )

            fat = (
                nutrients["fat"]
                * multiplier
            )

            st.info(
                f"{calories:.0f} kcal · "
                f"P {protein:.1f}g · "
                f"C {carbs:.1f}g · "
                f"F {fat:.1f}g"
            )

            if st.button(
                "Add to diary",
                type="primary",
            ):

                cached = cache_food(
                    product
                )

                food_id = (
                    cached["id"]
                    if cached
                    else None
                )

                supabase.table(
                    "food_logs"
                ).insert(
                    {
                        "user_id": (
                            st.session_state
                            .user.id
                        ),
                        "meal": meal,
                        "food_id": food_id,
                        "food_name": (
                            product.get(
                                "product_name"
                            )
                            or "Unknown food"
                        ),
                        "quantity": quantity,
                        "unit": "g",
                        "calories": calories,
                        "protein": protein,
                        "carbs": carbs,
                        "fat": fat,
                        "fiber": (
                            nutrients["fiber"]
                            * multiplier
                        ),
                        "sugar": (
                            nutrients["sugar"]
                            * multiplier
                        ),
                        "sodium": (
                            nutrients["sodium"]
                            * multiplier
                        ),
                    }
                ).execute()

                del st.session_state.selected_product

                st.success(
                    "Added to your diary."
                )

    # --------------------------------------------------------
    # BARCODE
    # --------------------------------------------------------

    with tab_barcode:

        st.subheader(
            "Scan a barcode"
        )

        st.info(
            "For now, enter the barcode manually. "
            "We'll add camera scanning next."
        )

        barcode = st.text_input(
            "Barcode",
            placeholder="e.g. 3017620422003",
        )

        if st.button(
            "Find product",
            type="primary",
        ):

            if not barcode:

                st.warning(
                    "Enter a barcode first."
                )

            else:

                product = get_product_by_barcode(
                    barcode.strip()
                )

                if product:

                    st.session_state.selected_product = (
                        product
                    )

                    st.success(
                        "Product found."
                    )

                    st.rerun()

                else:

                    st.error(
                        "That barcode wasn't found."
                    )

    # --------------------------------------------------------
    # QUICK ADD
    # --------------------------------------------------------

    with tab_quick:

        st.subheader(
            "Quick macro entry"
        )

        st.caption(
            "Useful when you already know the macros."
        )

        meal = st.selectbox(
            "Meal",
            [
                "breakfast",
                "lunch",
                "dinner",
                "snack",
            ],
            key="quick_meal",
        )

        name = st.text_input(
            "Name",
            value="Quick entry",
        )

        c1, c2 = st.columns(2)

        with c1:

            calories = st.number_input(
                "Calories",
                min_value=0.0,
                value=0.0,
            )

            protein = st.number_input(
                "Protein (g)",
                min_value=0.0,
                value=0.0,
            )

        with c2:

            carbs = st.number_input(
                "Carbs (g)",
                min_value=0.0,
                value=0.0,
            )

            fat = st.number_input(
                "Fat (g)",
                min_value=0.0,
                value=0.0,
            )

        if st.button(
            "Add quick entry",
            type="primary",
        ):

            supabase.table(
                "quick_entries"
            ).insert(
                {
                    "user_id": (
                        st.session_state
                        .user.id
                    ),
                    "meal": meal,
                    "name": name,
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat,
                }
            ).execute()

            st.success(
                "Added."
            )


# ============================================================
# APP ENTRY
# ============================================================

if st.session_state.user is None:

    login_screen()

    st.stop()


# ============================================================
# LOGGED-IN APP
# ============================================================

profile = get_profile()

if profile is None:

    save_profile({})

    profile = get_profile()


with st.sidebar:

    st.markdown(
        "# 🥗 Macro"
    )

    st.caption(
        st.session_state.user.email
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "➕ Add Food",
            "🎯 Goals",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    if st.button(
        "Log out",
        use_container_width=True,
    ):

        supabase.auth.sign_out()

        st.session_state.session = None
        st.session_state.user = None

        st.rerun()


# ============================================================
# ROUTING
# ============================================================

if page == "🏠 Dashboard":

    dashboard(profile)

elif page == "➕ Add Food":

    add_food_page()

elif page == "🎯 Goals":

    goals_page(profile)
