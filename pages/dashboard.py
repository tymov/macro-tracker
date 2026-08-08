from datetime import date

import streamlit as st

from components.food_card import render_log_row
from components.macro_progress import render_daily_summary
from services.supabase import delete_food_log, get_logs_for_day


def render(user_id, profile):

    st.title("Overview")
    st.caption(date.today().strftime("%A, %d %B %Y"))

    logs = get_logs_for_day(user_id, date.today())

    st.subheader("Today")

    render_daily_summary(profile, logs)

    st.divider()

    def handle_remove(log_id):
        delete_food_log(log_id)
        st.rerun()

    # ---------- MEALS ----------

    st.subheader("Meals")

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
    st.subheader("Drinks")

    drink_logs = [x for x in logs if (x.get("food_type") or "food") == "drink"]

    with st.container(border=True):

        if drink_logs:
            for item in drink_logs:
                render_log_row(item, handle_remove)
        else:
            st.caption("Nothing logged.")
