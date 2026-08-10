import streamlit as st

from services.openfoodfacts import nutrition_from_product


def render_product_result(product, key, recent=False):
    """Renders one search/recent result card. Returns True the run
    the card's Add button is clicked."""

    name = product.get("product_name") or "Unknown product"
    brand = product.get("brands") or ""
    nutrients = nutrition_from_product(product)

    clicked = False

    with st.container(border=True):

        c1, c2 = st.columns([4, 1])

        with c1:
            st.markdown(f"### {name}")

            meta_bits = []
            if brand:
                meta_bits.append(brand)
            if recent:
                meta_bits.append("Recent")
            if meta_bits:
                st.caption(" · ".join(meta_bits))

            st.write(
                f"{nutrients['calories']:.0f} kcal · "
                f"P {nutrients['protein']:.1f}g · "
                f"C {nutrients['carbs']:.1f}g · "
                f"F {nutrients['fat']:.1f}g per 100g"
            )

        with c2:
            if st.button("Add", key=key, type="primary", icon=":material/add:"):
                clicked = True

    return clicked


def render_log_row(item, on_remove):
    """Renders one diary row (name, quantity, kcal, remove button).
    Calls on_remove(item_id) if the remove button is pressed."""

    quantity_value = item.get("quantity_value")
    quantity_unit = item.get("quantity_unit")

    if quantity_value is None:
        quantity_value = item.get("quantity")
    if not quantity_unit:
        quantity_unit = item.get("unit") or ""

    cols = st.columns([4, 2, 2, 1])

    with cols[0]:
        st.write(item.get("food_name") or "Unknown")

    with cols[1]:
        if quantity_value is not None:
            st.write(f"{quantity_value:g} {quantity_unit}")

    with cols[2]:
        st.write(f'{float(item.get("calories") or 0):.0f} kcal')

    with cols[3]:
        if st.button("", key=f"remove_{item['id']}", icon=":material/close:"):
            on_remove(item["id"])
