import streamlit as st


def render_daily_summary(profile, logs):
    """Renders the calorie/protein/carb/fat metrics + progress bar
    for a set of today's food_logs rows."""

    target_calories = profile.get("calorie_target") or 0
    target_protein = profile.get("protein_target") or 0
    target_carbs = profile.get("carb_target") or 0
    target_fat = profile.get("fat_target") or 0

    total_calories = sum(float(x["calories"] or 0) for x in logs)
    total_protein = sum(float(x["protein"] or 0) for x in logs)
    total_carbs = sum(float(x["carbs"] or 0) for x in logs)
    total_fat = sum(float(x["fat"] or 0) for x in logs)

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

    if target_calories:

        st.write("")

        st.markdown(
            '<div class="progress-label">Calories consumed</div>',
            unsafe_allow_html=True,
        )

        st.progress(min(total_calories / target_calories, 1.0))
