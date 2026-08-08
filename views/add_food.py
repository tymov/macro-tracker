import streamlit as st

from components.barcode_scanner import render_barcode_scanner
from components.food_card import render_product_result
from services.nutrition import (
    CONTAINER_ML_UNITS,
    UNIT_LABELS,
    UNITS,
    default_container_amount,
    default_unit_for,
    guess_food_type,
    parse_serving_grams,
    resolve_grams,
    suggest_meal,
)
from services.openfoodfacts import (
    get_product_by_barcode,
    looks_like_barcode,
    nutrition_from_product,
    search_products,
)
from services.supabase import (
    cache_food,
    get_recent_foods,
    insert_food_log,
    insert_quick_entry,
    update_food_cache,
)

MEALS = ["breakfast", "lunch", "dinner", "snack"]


def render(user_id):

    st.title("Add food")

    if "selected_product" in st.session_state:
        _render_editor(user_id, st.session_state.selected_product)
        return

    _render_picker(user_id)


# ============================================================
# STEP 1 — search / scan / recent
# ============================================================

def _render_picker(user_id):

    query = st.text_input(
        "Search food or enter a barcode",
        placeholder="e.g. chicken breast, or 5449000000996",
    )

    with st.expander("Scan a barcode"):
        code = render_barcode_scanner()
        if code:
            product = get_product_by_barcode(code)
            if product:
                st.session_state.selected_product = product
                st.rerun()
            else:
                st.error("That barcode wasn't found.")

    st.divider()

    if query:

        query = query.strip()

        if looks_like_barcode(query):
            product = get_product_by_barcode(query)
            products = [product] if product else []
        else:
            products = search_products(query)

        if not products:
            st.info("No results found.")

        for i, product in enumerate(products):
            if render_product_result(product, key=f"search_{i}"):
                st.session_state.selected_product = product
                st.rerun()

    else:

        st.subheader("Recent")

        recent = get_recent_foods(user_id)

        if not recent:
            st.caption("Foods you log will show up here.")

        for i, product in enumerate(recent):
            if render_product_result(product, key=f"recent_{i}", recent=True):
                st.session_state.selected_product = product
                st.rerun()

        st.divider()

        with st.expander("Enter macros manually"):
            _render_quick_add(user_id)


# ============================================================
# STEP 2 — food editor (category, quantity/unit, meal)
# ============================================================

def _render_editor(user_id, product):

    name = product.get("product_name") or "Food"
    brand = product.get("brands") or ""
    nutrients = nutrition_from_product(product)

    # Stable per-product suffix so widget state doesn't bleed between
    # different products selected one after another.
    product_key = str(product.get("code") or product.get("_food_id") or name)
    product_key = product_key.replace(" ", "_")[:40]

    if st.button("Back"):
        del st.session_state.selected_product
        st.rerun()

    st.subheader(name)
    if brand:
        st.caption(brand)

    st.markdown("Category")
    guessed_type = guess_food_type(product)
    food_type = st.radio(
        "Category",
        ["food", "drink"],
        index=0 if guessed_type == "food" else 1,
        horizontal=True,
        label_visibility="collapsed",
        format_func=lambda x: "Food" if x == "food" else "Drink",
        key=f"food_type_{product_key}",
    )

    default_unit = default_unit_for(food_type)
    unit_index = UNITS.index(default_unit) if default_unit in UNITS else 0

    c1, c2 = st.columns(2)

    with c1:
        unit = st.selectbox(
            "Unit",
            UNITS,
            index=unit_index,
            format_func=lambda u: UNIT_LABELS[u],
            key=f"unit_{product_key}",
        )

    with c2:
        if unit in ("g", "ml"):
            count = st.number_input(
                f"Quantity ({UNIT_LABELS[unit]})",
                min_value=0.0, value=100.0, step=10.0,
                key=f"count_{product_key}",
            )
        elif unit in ("kg", "L"):
            count = st.number_input(
                f"Quantity ({UNIT_LABELS[unit]})",
                min_value=0.0, value=1.0, step=0.1,
                key=f"count_{product_key}",
            )
        else:
            count = st.number_input(
                "Quantity",
                min_value=1, value=1, step=1,
                key=f"count_{product_key}",
            )

    if unit in CONTAINER_ML_UNITS:  # glass, can, cup, bottle

        default_amount = default_container_amount(unit, name, brand)

        per_unit_amount = st.number_input(
            f"Amount per {UNIT_LABELS[unit]} (ml)",
            min_value=1.0, value=float(default_amount), step=10.0,
            key=f"per_unit_{product_key}",
        )

        grams = resolve_grams(unit, count, container_amount=per_unit_amount)

    elif unit in ("serving", "piece"):

        serving_default = parse_serving_grams(product) or 100.0

        per_unit_amount = st.number_input(
            f"Amount per {UNIT_LABELS[unit]} (g)",
            min_value=1.0, value=float(serving_default), step=5.0,
            key=f"per_unit_{product_key}",
        )

        grams = resolve_grams(unit, count, serving_grams=per_unit_amount)

    else:
        grams = resolve_grams(unit, count)

    multiplier = grams / 100 if grams else 0

    scaled = {k: v * multiplier for k, v in nutrients.items()}

    st.markdown("Macros")
    st.caption("Auto-calculated from the quantity above — edit if it looks off.")

    c1, c2 = st.columns(2)

    with c1:
        final_calories = st.number_input(
            "Calories", min_value=0.0, value=round(scaled["calories"], 1),
            step=1.0, key=f"cal_override_{product_key}",
        )
        final_protein = st.number_input(
            "Protein (g)", min_value=0.0, value=round(scaled["protein"], 1),
            step=1.0, key=f"protein_override_{product_key}",
        )

    with c2:
        final_carbs = st.number_input(
            "Carbs (g)", min_value=0.0, value=round(scaled["carbs"], 1),
            step=1.0, key=f"carbs_override_{product_key}",
        )
        final_fat = st.number_input(
            "Fat (g)", min_value=0.0, value=round(scaled["fat"], 1),
            step=1.0, key=f"fat_override_{product_key}",
        )

    save_correction = st.checkbox(
        "Remember this correction for next time",
        key=f"save_correction_{product_key}",
    )

    st.markdown("Meal")
    meal = st.radio(
        "Meal",
        MEALS,
        index=MEALS.index(suggest_meal()),
        horizontal=True,
        label_visibility="collapsed",
        format_func=str.capitalize,
        key=f"meal_{product_key}",
    )

    if st.button("Add to diary", type="primary", use_container_width=True):

        final_nutrients = {
            "calories": final_calories,
            "protein": final_protein,
            "carbs": final_carbs,
            "fat": final_fat,
            "fiber": scaled["fiber"],
            "sugar": scaled["sugar"],
            "sodium": scaled["sodium"],
        }

        try:
            if product.get("_food_id"):
                food_id = product["_food_id"]
            else:
                cached = cache_food(product, nutrients)
                food_id = cached["id"] if cached else None

            if save_correction and food_id and multiplier:
                # Corrections are entered at this quantity's scale —
                # back-solve to a per-100g basis before caching, since
                # that's the basis every other lookup of this product
                # scales from.
                corrected_per_100g = {
                    k: (v / multiplier) for k, v in final_nutrients.items()
                }
                update_food_cache(food_id, corrected_per_100g)

            insert_food_log(
                user_id,
                {
                    "meal": meal,
                    "food_id": food_id,
                    "food_name": name,
                    "food_type": food_type,
                    "quantity_value": count,
                    "quantity_unit": unit,
                    **final_nutrients,
                },
            )

            del st.session_state.selected_product

            st.toast("Added to your diary.")
            st.rerun()

        except Exception as e:
            st.error(f"Couldn't save this entry: {e}")


# ============================================================
# MANUAL ENTRY (no OFF product behind it)
# ============================================================

def _render_quick_add(user_id):

    st.caption("Useful when you already know the macros.")

    c1, c2 = st.columns(2)

    with c1:
        meal = st.selectbox("Meal", MEALS, key="quick_meal")
        food_type = st.selectbox(
            "Category", ["food", "drink"],
            format_func=lambda x: "Food" if x == "food" else "Drink",
            key="quick_type",
        )

    with c2:
        name = st.text_input("Name", value="Quick entry", key="quick_name")

    c1, c2 = st.columns(2)

    with c1:
        calories = st.number_input("Calories", min_value=0.0, value=0.0, key="quick_cal")
        protein = st.number_input("Protein (g)", min_value=0.0, value=0.0, key="quick_protein")

    with c2:
        carbs = st.number_input("Carbs (g)", min_value=0.0, value=0.0, key="quick_carbs")
        fat = st.number_input("Fat (g)", min_value=0.0, value=0.0, key="quick_fat")

    if st.button("Add quick entry", type="primary"):

        try:
            insert_quick_entry(
                user_id,
                {
                    "meal": meal,
                    "food_type": food_type,
                    "name": name,
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat,
                },
            )
            st.toast("Added.")

        except Exception as e:
            st.error(f"Couldn't save this entry: {e}")
