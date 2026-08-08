"""
Nutrition math: BMR/TDEE targets, and the unit system used by the
Add Food editor (quantity + unit -> grams, for scaling per-100g
nutrient data from Open Food Facts).
"""

from datetime import datetime


# ============================================================
# BMR / TDEE
# ============================================================

ACTIVITY_MULTIPLIERS = {
    "Sedentary": 1.2,
    "Lightly active": 1.375,
    "Moderately active": 1.55,
    "Very active": 1.725,
    "Extremely active": 1.9,
}


def calculate_bmr(sex, weight, height, age):

    # Mifflin-St Jeor
    if sex == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5

    elif sex == "female":
        return 10 * weight + 6.25 * height - 5 * age - 161

    else:
        # Neutral midpoint when "other" is selected
        return 10 * weight + 6.25 * height - 5 * age - 78


def calculate_targets(weight, bmr, activity, goal, weekly_change):
    """Returns (tdee, calories, protein, carbs, fat), all rounded."""

    tdee = bmr * ACTIVITY_MULTIPLIERS[activity]

    if goal == "Lose weight":
        calories = tdee - (abs(weekly_change) * 1100)

    elif goal == "Gain weight":
        calories = tdee + (abs(weekly_change) * 1100)

    else:
        calories = tdee

    calories = max(calories, 1200)

    # Protein-first approach
    protein = 1.8 * weight

    # Fat around 25% of calories
    fat = (calories * 0.25) / 9

    # Remaining calories go to carbs
    carbs = (calories - (protein * 4) - (fat * 9)) / 4

    return (
        round(tdee),
        round(calories),
        round(protein),
        round(carbs),
        round(fat),
    )


# ============================================================
# UNITS
# ============================================================
#
# Two families:
#  - direct amount units (g, kg, ml, L, piece): the number the user
#    types IS the amount.
#  - "container" units (glass, can, cup, bottle, serving): the user
#    picks a count (e.g. "1 can"), and we resolve that to an amount
#    using a default that depends on the unit and, for cans in
#    particular, the product itself (a Red Bull can isn't a Coke can).

DIRECT_UNITS = ["g", "kg", "ml", "L", "piece"]
CONTAINER_ML_UNITS = ["glass", "can", "cup", "bottle"]
CONTAINER_UNITS = CONTAINER_ML_UNITS + ["serving"]
UNITS = DIRECT_UNITS + CONTAINER_UNITS

UNIT_LABELS = {
    "g": "g",
    "kg": "kg",
    "ml": "ml",
    "L": "L",
    "piece": "piece",
    "glass": "glass",
    "can": "can",
    "cup": "cup",
    "bottle": "bottle",
    "serving": "serving",
}

# Default amount in grams/ml for one container unit
CONTAINER_DEFAULT_ML = {
    "glass": 250,
    "can": 330,
    "cup": 240,
    "bottle": 500,
}

# Brand-specific overrides for "can" (and could extend to bottle etc).
# Matched against "<product name> <brand>" lowercased, substring match.
CAN_OVERRIDES = [
    (["red bull"], 250),
    (["monster"], 500),
    (["coca-cola", "coca cola", "coke"], 330),
]


def guess_can_amount(product_name, brand):

    text = f"{product_name or ''} {brand or ''}".lower()

    for keywords, amount_ml in CAN_OVERRIDES:
        if any(k in text for k in keywords):
            return amount_ml

    return CONTAINER_DEFAULT_ML["can"]


def default_container_amount(unit, product_name, brand):

    if unit == "can":
        return guess_can_amount(product_name, brand)

    return CONTAINER_DEFAULT_ML.get(unit, 100)


def guess_food_type(product):
    """'drink' or 'food', based on Open Food Facts category tags,
    falling back to a keyword check on the product name."""

    tags = product.get("categories_tags") or []

    drink_tags = (
        "en:beverages",
        "en:sodas",
        "en:waters",
        "en:juices",
        "en:coffees",
        "en:teas",
        "en:energy-drinks",
        "en:alcoholic-beverages",
        "en:plant-based-beverages",
    )

    if any(t in tags for t in drink_tags):
        return "drink"

    name = (product.get("product_name") or "").lower()

    drink_keywords = [
        "juice", "soda", "cola", "water", "coffee", "tea",
        "energy drink", "beer", "wine", "smoothie", "milk",
    ]

    if any(k in name for k in drink_keywords):
        return "drink"

    return "food"


def default_unit_for(food_type):

    return "can" if food_type == "drink" else "g"


def parse_serving_grams(product):
    """Best-effort grams for one 'serving' or 'piece', from OFF's
    serving_size field (e.g. '30 g', '1 cup (240 ml)'). Returns
    None if it can't be parsed."""

    raw = product.get("serving_size")

    if not raw:
        return None

    digits = ""
    for ch in str(raw):
        if ch.isdigit() or ch == ".":
            digits += ch
        elif digits:
            break

    try:
        return float(digits)
    except ValueError:
        return None


def suggest_meal():
    """Default meal selection based on the current time of day."""

    hour = datetime.now().hour

    if 5 <= hour < 11:
        return "breakfast"
    if 11 <= hour < 15:
        return "lunch"
    if 15 <= hour < 21:
        return "dinner"
    return "snack"


def resolve_grams(unit, count, container_amount=None, serving_grams=None):
    """Turns a (unit, count) pair into a gram/ml amount that can be
    used to scale per-100g nutrient values."""

    if unit == "g":
        return count

    if unit == "kg":
        return count * 1000

    if unit == "ml":
        return count

    if unit == "L":
        return count * 1000

    if unit in ("glass", "can", "cup", "bottle"):
        return count * (container_amount or CONTAINER_DEFAULT_ML.get(unit, 100))

    if unit in ("serving", "piece"):
        return count * (serving_grams or 100)

    return count
