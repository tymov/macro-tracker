import streamlit as st
from datetime import date

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="My Macro Tracker",
    page_icon="🥗",
    layout="wide"
)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "food_log" not in st.session_state:
    st.session_state.food_log = []

if "foods" not in st.session_state:
    st.session_state.foods = {
        "Chicken breast": {
            "calories": 165,
            "protein": 31,
            "carbs": 0,
            "fat": 3.6
        },
        "White rice": {
            "calories": 130,
            "protein": 2.7,
            "carbs": 28,
            "fat": 0.3
        },
        "Egg": {
            "calories": 143,
            "protein": 12.6,
            "carbs": 0.7,
            "fat": 9.5
        },
        "Greek yogurt": {
            "calories": 59,
            "protein": 10.3,
            "carbs": 3.6,
            "fat": 0.4
        },
        "Banana": {
            "calories": 89,
            "protein": 1.1,
            "carbs": 22.8,
            "fat": 0.3
        },
        "Oats": {
            "calories": 389,
            "protein": 16.9,
            "carbs": 66.3,
            "fat": 6.9
        }
    }

# ---------------------------------------------------------
# TARGETS
# ---------------------------------------------------------

CALORIE_TARGET = 2400
PROTEIN_TARGET = 180
CARB_TARGET = 250
FAT_TARGET = 80

# ---------------------------------------------------------
# CALCULATE TOTALS
# ---------------------------------------------------------

total_calories = sum(item["calories"] for item in st.session_state.food_log)
total_protein = sum(item["protein"] for item in st.session_state.food_log)
total_carbs = sum(item["carbs"] for item in st.session_state.food_log)
total_fat = sum(item["fat"] for item in st.session_state.food_log)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🥗 My Macro Tracker")

st.caption(date.today().strftime("%A, %d %B %Y"))

st.divider()

# ---------------------------------------------------------
# MACRO SUMMARY
# ---------------------------------------------------------

st.subheader("Today's Macros")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Calories",
        f"{total_calories:.0f} kcal",
        f"{CALORIE_TARGET - total_calories:.0f} remaining"
    )

with col2:
    st.metric(
        "Protein",
        f"{total_protein:.1f} g",
        f"{PROTEIN_TARGET - total_protein:.1f} g remaining"
    )

with col3:
    st.metric(
        "Carbs",
        f"{total_carbs:.1f} g",
        f"{CARB_TARGET - total_carbs:.1f} g remaining"
    )

with col4:
    st.metric(
        "Fat",
        f"{total_fat:.1f} g",
        f"{FAT_TARGET - total_fat:.1f} g remaining"
    )

# ---------------------------------------------------------
# PROGRESS BARS
# ---------------------------------------------------------

st.write("")

st.write("Calories")
st.progress(
    min(total_calories / CALORIE_TARGET, 1.0)
)

col1, col2, col3 = st.columns(3)

with col1:
    st.write("Protein")
    st.progress(min(total_protein / PROTEIN_TARGET, 1.0))

with col2:
    st.write("Carbs")
    st.progress(min(total_carbs / CARB_TARGET, 1.0))

with col3:
    st.write("Fat")
    st.progress(min(total_fat / FAT_TARGET, 1.0))

st.divider()

# ---------------------------------------------------------
# ADD FOOD
# ---------------------------------------------------------

st.subheader("➕ Add Food")

meal = st.selectbox(
    "Meal",
    ["Breakfast", "Lunch", "Dinner", "Snack"]
)

food_names = list(st.session_state.foods.keys())

selected_food = st.selectbox(
    "Food",
    food_names
)

quantity = st.number_input(
    "Quantity (grams)",
    min_value=1.0,
    value=100.0,
    step=1.0
)

food = st.session_state.foods[selected_food]

multiplier = quantity / 100

calories = food["calories"] * multiplier
protein = food["protein"] * multiplier
carbs = food["carbs"] * multiplier
fat = food["fat"] * multiplier

st.write(
    f"**{quantity:.0f}g {selected_food}:** "
    f"{calories:.0f} kcal · "
    f"P {protein:.1f}g · "
    f"C {carbs:.1f}g · "
    f"F {fat:.1f}g"
)

if st.button("Add to diary", type="primary"):

    st.session_state.food_log.append({
        "meal": meal,
        "food": selected_food,
        "quantity": quantity,
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat
    })

    st.rerun()

st.divider()

# ---------------------------------------------------------
# TODAY'S FOOD
# ---------------------------------------------------------

st.subheader("🍽️ Today's Food")

if not st.session_state.food_log:

    st.info("Nothing logged yet. Add your first food above!")

else:

    meals = ["Breakfast", "Lunch", "Dinner", "Snack"]

    for current_meal in meals:

        meal_items = [
            item
            for item in st.session_state.food_log
            if item["meal"] == current_meal
        ]

        if not meal_items:
            continue

        meal_calories = sum(
            item["calories"]
            for item in meal_items
        )

        st.markdown(
            f"### {current_meal} — {meal_calories:.0f} kcal"
        )

        for index, item in enumerate(
            meal_items
        ):

            col1, col2, col3 = st.columns(
                [4, 2, 1]
            )

            with col1:
                st.write(
                    f"**{item['food']}** "
                    f"({item['quantity']:.0f}g)"
                )

            with col2:
                st.write(
                    f"{item['calories']:.0f} kcal"
                )

            with col3:

                if st.button(
                    "✕",
                    key=f"delete_{current_meal}_{index}"
                ):

                    st.session_state.food_log.remove(
                        item
                    )

                    st.rerun()

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Personal macro tracker • Version 1"
)
