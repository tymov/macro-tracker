"""
All Supabase reads/writes live here. Pages and components pass in
user_id explicitly rather than reaching into st.session_state, so
this module has no dependency on Streamlit's session state.
"""

from datetime import datetime, timezone

import streamlit as st
from supabase import create_client, Client


def get_supabase() -> Client:
    """One client per browser session, not per server process.

    @st.cache_resource would share a single client (and its logged-in
    auth session) across every visitor hitting the same server
    process — fine for a single-user demo, not fine once more than
    one person uses the app at once. Storing it in st.session_state
    keeps each visitor's client, and therefore their auth session,
    isolated to them.
    """

    if "_supabase_client" not in st.session_state:
        st.session_state["_supabase_client"] = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"],
        )

    return st.session_state["_supabase_client"]


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

def update_food_cache(food_id, nutrients):
    """Overwrites a cached food's per-100g nutrients with a
    user-corrected value. Best-effort — failures here shouldn't
    block the food log insert that triggered them."""

    try:
        get_supabase().table("foods").update(
            {
                "calories": nutrients["calories"],
                "protein": nutrients["protein"],
                "carbs": nutrients["carbs"],
                "fat": nutrients["fat"],
                "fiber": nutrients.get("fiber", 0),
                "sugar": nutrients.get("sugar", 0),
                "sodium": nutrients.get("sodium", 0),
            }
        ).eq("id", food_id).execute()

    except Exception:
        pass


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
    day_end = f"{day}T23:59:59.999999"

    response = (
        get_supabase()
        .table("food_logs")
        .select("*")
        .eq("user_id", user_id)
        .gte("eaten_at", day_start)
        .lte("eaten_at", day_end)
        .order("eaten_at", desc=True)
        .execute()
    )

    return response.data or []


def get_logs_for_range(user_id, start_day, end_day):
    """All logs between two dates (inclusive), for the history strip.
    One query instead of one-per-day."""

    range_start = f"{start_day}T00:00:00"
    range_end = f"{end_day}T23:59:59.999999"

    response = (
        get_supabase()
        .table("food_logs")
        .select("*")
        .eq("user_id", user_id)
        .gte("eaten_at", range_start)
        .lte("eaten_at", range_end)
        .execute()
    )

    return response.data or []


def insert_food_log(user_id, entry):
    """Inserts one food_logs row.

    Two defensive additions vs. a naive insert:
    - eaten_at is set explicitly (UTC now) rather than relying on a
      database default. If that default doesn't exist, the row's
      eaten_at ends up NULL, and `.gte("eaten_at", ...)` in
      get_logs_for_day silently matches nothing — the exact "food
      saves fine but dashboard stays empty" symptom.
    - legacy `quantity` / `unit` columns are populated alongside the
      new `quantity_value` / `quantity_unit`, so this works whether
      or not schema.sql has been run yet (older schemas have a
      NOT NULL constraint on `quantity` that a quantity_value-only
      insert violates).
    """

    row = {
        "user_id": user_id,
        "eaten_at": datetime.now(timezone.utc).isoformat(),
        "quantity": entry.get("quantity_value"),
        "unit": entry.get("quantity_unit"),
        **entry,
    }

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

    row = {
        "user_id": user_id,
        "eaten_at": datetime.now(timezone.utc).isoformat(),
        **entry,
    }

    get_supabase().table("quick_entries").insert(row).execute()
