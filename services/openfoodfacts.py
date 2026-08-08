"""
Thin wrapper around the Open Food Facts API: search, barcode lookup,
and pulling a consistent nutrient dict out of a product record.
"""

import requests


OFF_URL = "https://world.openfoodfacts.org"

FIELDS = (
    "code,"
    "product_name,"
    "brands,"
    "quantity,"
    "serving_size,"
    "categories_tags,"
    "image_front_small_url,"
    "nutriments"
)

HEADERS = {
    "User-Agent": "PersonalMacroTracker/1.0 (personal nutrition app)"
}


def looks_like_barcode(text):
    """True for a plain run of 8-14 digits, e.g. an EAN/UPC code."""

    text = text.strip()

    return text.isdigit() and 8 <= len(text) <= 14


def search_products(query, page_size=12):

    url = f"{OFF_URL}/cgi/search.pl"

    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size,
        "fields": FIELDS,
    }

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json().get("products", [])

    except Exception:
        return []


def get_product_by_barcode(barcode):

    url = f"{OFF_URL}/api/v2/product/{barcode}.json"

    try:
        response = requests.get(
            url,
            params={"fields": FIELDS},
            headers=HEADERS,
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

    nutrients = product.get("nutriments", {})

    return {
        "calories": nutrients.get("energy-kcal_100g", 0) or 0,
        "protein": nutrients.get("proteins_100g", 0) or 0,
        "carbs": nutrients.get("carbohydrates_100g", 0) or 0,
        "fat": nutrients.get("fat_100g", 0) or 0,
        "fiber": nutrients.get("fiber_100g", 0) or 0,
        "sugar": nutrients.get("sugars_100g", 0) or 0,
        "sodium": nutrients.get("sodium_100g", 0) or 0,
    }
