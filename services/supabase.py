"""
All Supabase reads/writes live here. Pages and components pass in
user_id explicitly rather than reaching into st.session_state, so
this module has no dependency on Streamlit's session state.
"""

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase() -> Client:

    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


# ============================================================
# PROFILE
# ============================================================

def get_profile(user_id):

    response = (
        get_supabase()
        .table("profiles")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    return response.data


def save_profile(user_id, data):

    data = {**data, "id": user_id}

    get_supabase().table("profiles").upsert(data).execute()


# ============================================================
# FOOD CACHE (per-100g nutrient data, deduped by source+external_id)
# ============================================================

def cache_food(product, nutrients):

    data = {
        "external_id": product.get("code"),
        "source": "open_food_facts",
        "barcode": product.get("code"),
        "name": product.get("product_name") or "Unknown food",
        "brand": product.get("brands"),
        "serving_size": None,
        "serving_unit": "g",
        "calories": nutrients["calories"],
        "protein": nutrients["protein"],
        "carbs": nutrients["carbs"],
        "fat": nutrients["fat"],
        "fiber": nutrients["fiber"],
        "sugar": nutrients["sugar"],
        "sodium": nutrients["sodium"],
        "image_url": product.get("image_front_small_url"),
    }

    try:
        result = (
            get_supabase()
            .table("foods")
            .upsert(data, on_conflict="source,external_id")
            .execute()
        )
        return result.data[0]

    except Exception:
        return None


# ============================================================
# FOOD LOGS
# ============================================================

def get_logs_for_day(user_id, day):

    day_start = f"{day}T00:00:00"

    response = (
        get_supabase()
        .table("food_logs")
        .select("*")
        .eq("user_id", user_id)
        .gte("eaten_at", day_start)
        .order("eaten_at", desc=True)
        .execute()
    )

    return response.data or []


def insert_food_log(user_id, entry):

    row = {"user_id": user_id, **entry}

    get_supabase().table("food_logs").insert(row).execute()


def delete_food_log(log_id):

    get_supabase().table("food_logs").delete().eq("id", log_id).execute()


def get_recent_foods(user_id, limit=8):
    """Recently logged catalog foods (skips quick/manual entries,
    which have no food_id), returned as OFF-shaped product dicts so
    they can flow through the same food editor as a fresh search."""

    response = (
        get_supabase()
        .table("food_logs")
        .select("food_id, food_name")
        .eq("user_id", user_id)
        .order("eaten_at", desc=True)
        .limit(40)
        .execute()
    )

    seen = []
    for row in response.data or []:
        food_id = row.get("food_id")
        if food_id and food_id not in seen:
            seen.append(food_id)
        if len(seen) >= limit:
            break

    if not seen:
        return []

    foods_response = (
        get_supabase()
        .table("foods")
        .select("*")
        .in_("id", seen)
        .execute()
    )

    foods_by_id = {row["id"]: row for row in (foods_response.data or [])}

    products = []
    for food_id in seen:
        row = foods_by_id.get(food_id)
        if not row:
            continue
        products.append(
            {
                "_food_id": row["id"],
                "code": row.get("barcode"),
                "product_name": row.get("name"),
                "brands": row.get("brand"),
                "categories_tags": [],
                "serving_size": None,
                "image_front_small_url": row.get("image_url"),
                "nutriments": {
                    "energy-kcal_100g": row.get("calories"),
                    "proteins_100g": row.get("protein"),
                    "carbohydrates_100g": row.get("carbs"),
                    "fat_100g": row.get("fat"),
                    "fiber_100g": row.get("fiber"),
                    "sugars_100g": row.get("sugar"),
                    "sodium_100g": row.get("sodium"),
                },
            }
        )

    return products


# ============================================================
# QUICK ENTRIES (manual macro logging, no OFF product behind it)
# ============================================================

def insert_quick_entry(user_id, entry):

    row = {"user_id": user_id, **entry}

    get_supabase().table("quick_entries").insert(row).execute()
