import streamlit as st
import requests
from datetime import date, datetime

from supabase import create_client, Client


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Macro",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================
#
# Design system — hardcoded, does not follow the browser/OS
# light-dark preference. Paired with .streamlit/config.toml
# (base="dark" + matching colors) so native BaseWeb components
# that render outside this DOM tree — dropdown menus, calendar
# popovers, tooltips — inherit the same palette instead of
# falling back to Streamlit's stock dark theme.
#
# Background   #0B0E1A (page) / #131829 (surface) / #1A2036 (raised)
# Text         #ECEDF5 (primary) / #8B92AC (muted) / #565D78 (faint)
# Border       #262C46
# Accent       #8B7CF6 (violet) — used only for primary actions,
#              the active nav state, and focus rings
# Type         Inter for UI text, system fallback stack
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

    /* Sidebar radio acting as nav */

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
            max-width:380px;
            margin:64px auto 32px auto;
            text-align:center;
        ">
            <h1 style="margin-bottom:4px;">Macro</h1>
            <p style="color:#6B6B6B; font-size:0.9rem;">
                Track what you eat.
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

                    st.success("Account created.")
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

    st.title("Overview")

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

    st.subheader("Today")

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

        st.markdown(
            '<div class="progress-label">Calories consumed</div>',
            unsafe_allow_html=True,
        )

        st.progress(
            min(
                total_calories
                / target_calories,
                1.0,
            )
        )

    st.divider()

    st.subheader("Meals")

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
                            "Remove",
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

    st.title("Goals")
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
        "Calculate my targets",
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
            "Search",
            "Barcode",
            "Quick add",
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
            "Camera scanning is coming next."
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
        "### Macro"
    )

    st.caption(
        st.session_state.user.email
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Add food",
            "Goals",
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

if page == "Dashboard":

    dashboard(profile)

elif page == "Add food":

    add_food_page()

elif page == "Goals":

    goals_page(profile)
