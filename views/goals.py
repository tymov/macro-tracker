import re

import streamlit as st

from services.nutrition import (
    ACTIVITY_MULTIPLIERS,
    calculate_bmr,
    calculate_targets,
)
from services.supabase import save_profile


def _save_profile_resilient(user_id, data):
    """Saves the profile; if a check constraint on the profiles table
    rejects one specific column (e.g. activity_level allows different
    values than the app sends), retries without that column so the
    rest of the save still goes through, and reports which field to
    fix in Supabase rather than failing the whole save.

    Returns None on a clean save, or a warning message string.
    """

    try:
        save_profile(user_id, data)
        return None

    except Exception as e:

        msg = str(e)
        match = re.search(r'"profiles_(\w+)_check"', msg)

        if match and "23514" in msg and match.group(1) in data:

            field = match.group(1)
            fallback = {k: v for k, v in data.items() if k != field}

            try:
                save_profile(user_id, fallback)
                return (
                    f"Saved everything except **{field}** — your database's "
                    f"check constraint on that column rejects the value the "
                    f"app sends ('{data[field]}'). See the note in schema.sql "
                    f"to fix it permanently."
                )
            except Exception as e2:
                return f"Couldn't save: {e2}"

        return f"Couldn't save: {e}"


def render(user_id, profile):

    st.title("Goals")
    st.caption("Calculate your targets or set them manually.")

    st.subheader("Your information")

    c1, c2 = st.columns(2)

    with c1:

        age = st.number_input(
            "Age",
            min_value=13,
            max_value=100,
            value=int(profile.get("age") or 25),
        )

        height = st.number_input(
            "Height (cm)",
            min_value=100.0,
            max_value=250.0,
            value=float(profile.get("height_cm") or 180),
        )

        weight = st.number_input(
            "Weight (kg)",
            min_value=30.0,
            max_value=300.0,
            value=float(profile.get("weight_kg") or 80),
        )

    with c2:

        sex = st.selectbox(
            "Sex",
            ["male", "female", "other"],
            index=["male", "female", "other"].index(profile.get("sex") or "male"),
        )

        activity = st.selectbox("Activity level", list(ACTIVITY_MULTIPLIERS.keys()))

        goal = st.selectbox("Goal", ["Lose weight", "Maintain", "Gain weight"])

    weekly_change = st.number_input(
        "Desired weekly weight change (kg)",
        min_value=0.0,
        max_value=2.0,
        value=0.5,
        step=0.1,
    )

    if st.button("Calculate my targets", type="primary"):

        bmr = calculate_bmr(sex, weight, height, age)

        tdee, calories, protein, carbs, fat = calculate_targets(
            weight, bmr, activity, goal, weekly_change
        )

        st.session_state.calculated_targets = {
            "bmr": round(bmr),
            "tdee": tdee,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
        }

    if "calculated_targets" in st.session_state:

        calc = st.session_state.calculated_targets

        st.divider()
        st.subheader("Suggested targets")

        c1, c2 = st.columns(2)

        with c1:
            st.metric("BMR", f"{calc['bmr']} kcal")
            st.metric("Estimated TDEE", f"{calc['tdee']} kcal")

        with c2:
            st.metric("Suggested calories", f"{calc['calories']} kcal")
            st.write(f"Protein: **{calc['protein']} g**")
            st.write(f"Carbs: **{calc['carbs']} g**")
            st.write(f"Fat: **{calc['fat']} g**")

        if st.button("Use these targets", type="primary"):

            warning = _save_profile_resilient(
                user_id,
                {
                    "age": int(age),
                    "sex": sex,
                    "height_cm": float(height),
                    "weight_kg": float(weight),
                    "goal": (
                        "lose_weight" if goal == "Lose weight"
                        else "gain_weight" if goal == "Gain weight"
                        else "maintain"
                    ),
                    "activity_level": activity.lower().replace(" ", "_"),
                    "calorie_target": int(calc["calories"]),
                    "protein_target": int(calc["protein"]),
                    "carb_target": int(calc["carbs"]),
                    "fat_target": int(calc["fat"]),
                    "weekly_weight_change": float(weekly_change),
                },
            )

            if warning:
                st.warning(warning)
            else:
                st.success("Your targets have been saved.")
                st.rerun()

    st.divider()
    st.subheader("Or set them manually")

    current_calories = float(profile.get("calorie_target") or 2000)
    current_protein = float(profile.get("protein_target") or 150)
    current_carbs = float(profile.get("carb_target") or 200)
    current_fat = float(profile.get("fat_target") or 65)

    c1, c2 = st.columns(2)

    with c1:
        manual_calories = st.number_input(
            "Calories", min_value=500.0, max_value=10000.0,
            value=current_calories, step=50.0,
        )
        manual_protein = st.number_input(
            "Protein (g)", min_value=0.0, max_value=1000.0,
            value=current_protein, step=5.0,
        )

    with c2:
        manual_carbs = st.number_input(
            "Carbs (g)", min_value=0.0, max_value=1000.0,
            value=current_carbs, step=5.0,
        )
        manual_fat = st.number_input(
            "Fat (g)", min_value=0.0, max_value=1000.0,
            value=current_fat, step=5.0,
        )

    if st.button("Save manual targets"):

        warning = _save_profile_resilient(
            user_id,
            {
                "age": int(age),
                "sex": sex,
                "height_cm": float(height),
                "weight_kg": float(weight),
                "calorie_target": float(manual_calories),
                "protein_target": float(manual_protein),
                "carb_target": float(manual_carbs),
                "fat_target": float(manual_fat),
            },
        )

        if warning:
            st.warning(warning)
        else:
            st.success("Your goals have been updated.")
            st.rerun()
