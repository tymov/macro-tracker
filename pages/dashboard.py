from datetime import date, timedelta

import streamlit as st

from components.food_card import render_log_row
from services.supabase import delete_food_log, get_logs_for_range


def render(user_id, profile):

    st.title("Overview")

    if "selected_day" not in st.session_state:
        st.session_state.selected_day = date.today()

    selected_day = st.session_state.selected_day
    range_start = date.today() - timedelta(days=4)

    all_logs = get_logs_for_range(user_id, range_start, date.today())

    logs_by_day = {}
    for row in all_logs:
        eaten_at = row.get("eaten_at") or ""
        day_key = eaten_at[:10]
        logs_by_day.setdefault(day_key, []).append(row)

    target_calories = profile.get("calorie_target") or 0

    _render_history_strip(logs_by_day, target_calories, range_start)

    st.divider()

    logs = logs_by_day.get(str(selected_day), [])

    label = "Today" if selected_day == date.today() else selected_day.strftime("%A, %d %B")
    st.subheader(label)

    _render_rings(profile, logs)

    total_calories = sum(float(x["calories"] or 0) for x in logs)

    if target_calories and total_calories >= target_calories:
        toast_key = f"toast_goal_hit_{selected_day}"
        if not st.session_state.get(toast_key):
            st.session_state[toast_key] = True
            st.toast("Daily goal reached.", icon=":material/celebration:")

    st.divider()

    def handle_remove(log_id):
        delete_food_log(log_id)
        st.rerun()

    # ---------- MEALS ----------

    st.subheader(":material/restaurant: Meals")

    meal_logs = [x for x in logs if (x.get("food_type") or "food") == "food"]

    meals = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snacks"),
    ]

    for meal_key, meal_name in meals:

        items = [x for x in meal_logs if x["meal"] == meal_key]
        meal_total = sum(float(x["calories"] or 0) for x in items)

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### {meal_name}")

            with col2:
                st.markdown(f"**{meal_total:.0f} kcal**")

            if items:
                for item in items:
                    render_log_row(item, handle_remove)
            else:
                st.caption("Nothing logged.")

    # ---------- DRINKS ----------

    st.divider()
    st.subheader(":material/local_cafe: Drinks")

    drink_logs = [x for x in logs if (x.get("food_type") or "food") == "drink"]

    with st.container(border=True):

        if drink_logs:
            for item in drink_logs:
                render_log_row(item, handle_remove)
        else:
            st.caption("Nothing logged.")


def _render_history_strip(logs_by_day, target_calories, range_start):
    """Last 5 days as tappable tiles, each flagging whether that
    day's calorie total was within the target."""

    with st.container(key="history_strip"):

        cols = st.columns(5)

        for i in range(5):

            day = range_start + timedelta(days=i)
            day_logs = logs_by_day.get(str(day), [])
            day_total = sum(float(x["calories"] or 0) for x in day_logs)

            has_data = len(day_logs) > 0
            hit_goal = (
                has_data and target_calories
                and target_calories * 0.9 <= day_total <= target_calories * 1.1
            )

            is_selected = day == st.session_state.selected_day
            is_future = day > date.today()

            label = f"{day.strftime('%a')}\n{day.day}"

            with cols[i]:
                st.button(
                    label,
                    key=f"day_{day}",
                    icon=":material/check_circle:" if hit_goal else None,
                    use_container_width=True,
                    disabled=is_future,
                    type="primary" if is_selected else "secondary",
                    on_click=_select_day,
                    args=(day,),
                )


def _select_day(day):
    st.session_state.selected_day = day


def _render_rings(profile, logs):
    """Renders the four macro rings as one flat block of HTML.

    Streamlit's markdown renderer only stays in "raw HTML" mode for a
    contiguous block of markup — a blank line inside an
    unsafe_allow_html string ends that block early and everything
    after it gets treated as plain markdown text (which is why the
    tags themselves were showing up on screen). Building this as a
    single joined string with no blank lines, and no per-line
    leading whitespace, keeps the whole thing as one HTML block.
    """

    totals = {
        "Calories": (
            sum(float(x["calories"] or 0) for x in logs),
            profile.get("calorie_target") or 0,
        ),
        "Protein": (
            sum(float(x["protein"] or 0) for x in logs),
            profile.get("protein_target") or 0,
        ),
        "Carbs": (
            sum(float(x["carbs"] or 0) for x in logs),
            profile.get("carb_target") or 0,
        ),
        "Fat": (
            sum(float(x["fat"] or 0) for x in logs),
            profile.get("fat_target") or 0,
        ),
    }

    items_html = []

    for label, (value, target) in totals.items():

        pct = min(value / target, 1.0) if target else 0
        unit = "" if label == "Calories" else "g"

        items_html.append(
            f'<div class="ring-item">'
            f'<div class="ring" style="--pct:{pct};">'
            f'<div class="ring-inner"><div class="ring-value">{value:.0f}</div></div>'
            f'</div>'
            f'<div class="ring-label">{label}</div>'
            f'<div class="ring-target">of {target:.0f}{unit}</div>'
            f'</div>'
        )

    rings_html = '<div class="ring-row">' + "".join(items_html) + "</div>"

    st.markdown(rings_html, unsafe_allow_html=True)
