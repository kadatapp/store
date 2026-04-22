from datetime import datetime
from pathlib import Path
import os
import pandas as pd
from dash import Dash, Input, Output, State, ALL, dcc, html, callback_context, no_update


MENU_ITEMS = [
    {
        "id": "burger",
        "name": "Smoky House Burger",
        "price": 14,
        "store": "Urban Bites Kitchen",
        "department": "Food",
        "category": "Best Seller",
        "description": "Grilled beef, cheddar, caramelized onions, and signature sauce.",
        "ingredients": {"Bun": 1, "Beef Patty": 1, "Cheddar": 1, "Onions": 2, "Sauce": 1},
        "ingredient_prices": {"Bun": 0.75, "Beef Patty": 2.5, "Cheddar": 0.8, "Onions": 0.35, "Sauce": 0.25},
        "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "pizza",
        "name": "Fire Oven Pizza",
        "price": 18,
        "store": "Urban Bites Kitchen",
        "department": "Food",
        "category": "Chef Pick",
        "description": "Stone-baked crust with basil, mozzarella, and roasted tomato.",
        "ingredients": {"Dough": 1, "Mozzarella": 2, "Basil": 4, "Tomato": 3},
        "ingredient_prices": {"Dough": 1.2, "Mozzarella": 0.9, "Basil": 0.2, "Tomato": 0.35},
        "image": "https://images.unsplash.com/photo-1548365328-9f547fb0953c?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "bowl",
        "name": "Green Power Bowl",
        "price": 13,
        "store": "Urban Bites Kitchen",
        "department": "Food",
        "category": "Fresh",
        "description": "Quinoa, avocado, crispy chickpeas, cucumber, and lime dressing.",
        "ingredients": {"Quinoa": 4, "Avocado": 2, "Chickpeas": 2, "Cucumber": 3},
        "ingredient_prices": {"Quinoa": 0.45, "Avocado": 1.1, "Chickpeas": 0.5, "Cucumber": 0.3},
        "image": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "tacos",
        "name": "Street Tacos",
        "price": 12,
        "store": "Urban Bites Kitchen",
        "department": "Food",
        "category": "Fast Favorite",
        "description": "Three loaded tacos with salsa verde and pickled onions.",
        "ingredients": {"Tortillas": 3, "Beef": 2, "Onions": 2, "Salsa": 1},
        "ingredient_prices": {"Tortillas": 0.5, "Beef": 1.5, "Onions": 0.3, "Salsa": 0.25},
        "image": "https://images.unsplash.com/photo-1552332386-f8dd00dc2f85?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "burrito",
        "name": "Loaded Burrito",
        "price": 15,
        "store": "Urban Bites Kitchen",
        "department": "Food",
        "category": "Build It",
        "description": "A burrito with adjustable rice, beans, chicken, cheese, and salsa.",
        "ingredients": {"Rice": 5, "Beans": 3, "Chicken": 2, "Cheese": 2, "Salsa": 1},
        "ingredient_prices": {"Rice": 0.4, "Beans": 0.55, "Chicken": 1.6, "Cheese": 0.85, "Salsa": 0.3},
        "image": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "margherita",
        "name": "Margherita Classic",
        "price": 16,
        "store": "Slice House Pizza",
        "department": "Food",
        "category": "Pizza House",
        "description": "Wood-fired pizza with tomato sauce, mozzarella, and basil.",
        "ingredients": {"Dough": 1, "Mozzarella": 2, "Basil": 4, "Sauce": 2},
        "ingredient_prices": {"Dough": 1.2, "Mozzarella": 0.9, "Basil": 0.2, "Sauce": 0.35},
        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "pepperoni",
        "name": "Pepperoni Heat",
        "price": 19,
        "store": "Slice House Pizza",
        "department": "Food",
        "category": "Pizza House",
        "description": "Pepperoni, chili oil, mozzarella, and roasted garlic.",
        "ingredients": {"Dough": 1, "Pepperoni": 5, "Mozzarella": 2, "Garlic": 2},
        "ingredient_prices": {"Dough": 1.2, "Pepperoni": 0.75, "Mozzarella": 0.9, "Garlic": 0.25},
        "image": "https://images.unsplash.com/photo-1628840042765-356cda07504e?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "veggie-pie",
        "name": "Garden Veggie Pie",
        "price": 17,
        "store": "Slice House Pizza",
        "department": "Food",
        "category": "Pizza House",
        "description": "Bell peppers, olives, mushrooms, onions, and provolone.",
        "ingredients": {"Peppers": 3, "Olives": 2, "Mushrooms": 3, "Onions": 2},
        "ingredient_prices": {"Peppers": 0.35, "Olives": 0.4, "Mushrooms": 0.45, "Onions": 0.3},
        "image": "https://images.unsplash.com/photo-1594007654729-407eedc4be65?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "mango-smoothie",
        "name": "Mango Smoothie",
        "price": 7,
        "store": "Fresh Sip Beverages",
        "department": "Food",
        "category": "Beverage",
        "description": "Cold mango smoothie blended with yogurt and ice.",
        "ingredients": {"Mango": 3, "Yogurt": 1, "Ice": 2, "Honey": 1},
        "ingredient_prices": {"Mango": 0.8, "Yogurt": 0.6, "Ice": 0.1, "Honey": 0.25},
        "image": "https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "iced-coffee",
        "name": "Iced Coffee",
        "price": 6,
        "store": "Fresh Sip Beverages",
        "department": "Food",
        "category": "Beverage",
        "description": "Chilled coffee with milk, syrup, and extra ice options.",
        "ingredients": {"Coffee": 2, "Milk": 1, "Ice": 2, "Vanilla": 1},
        "ingredient_prices": {"Coffee": 0.9, "Milk": 0.45, "Ice": 0.1, "Vanilla": 0.3},
        "image": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "berry-lemonade",
        "name": "Berry Lemonade",
        "price": 5,
        "store": "Fresh Sip Beverages",
        "department": "Food",
        "category": "Beverage",
        "description": "Fresh lemonade with mixed berries and adjustable sweetness.",
        "ingredients": {"Lemon": 2, "Berries": 2, "Sugar": 1, "Ice": 2},
        "ingredient_prices": {"Lemon": 0.35, "Berries": 0.6, "Sugar": 0.15, "Ice": 0.1},
        "image": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "matcha-latte",
        "name": "Matcha Latte",
        "price": 8,
        "store": "Fresh Sip Beverages",
        "department": "Food",
        "category": "Beverage",
        "description": "Creamy matcha drink with milk, foam, and sweetener controls.",
        "ingredients": {"Matcha": 2, "Milk": 1, "Foam": 1, "Sweetener": 1},
        "ingredient_prices": {"Matcha": 1.0, "Milk": 0.45, "Foam": 0.25, "Sweetener": 0.2},
        "image": "https://images.unsplash.com/photo-1515823662972-da6a2e4d3002?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "fresh-tomatoes",
        "name": "Fresh Tomatoes",
        "price": 4,
        "store": "Harvest Market",
        "department": "Food",
        "category": "Groceries",
        "description": "Ripe red tomatoes for salads, sauces, and home cooking.",
        "image": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "yellow-onions",
        "name": "Yellow Onions",
        "price": 3,
        "store": "Harvest Market",
        "department": "Food",
        "category": "Groceries",
        "description": "Kitchen onions for soups, stews, rice, and everyday meals.",
        "image": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "spice-mix",
        "name": "House Spice Mix",
        "price": 6,
        "store": "Harvest Market",
        "department": "Food",
        "category": "Groceries",
        "description": "A versatile seasoning blend for meats, vegetables, and grains.",
        "image": "https://images.unsplash.com/photo-1532336414038-cf19250c5757?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "olive-oil",
        "name": "Cooking Olive Oil",
        "price": 10,
        "store": "Harvest Market",
        "department": "Food",
        "category": "Groceries",
        "description": "Everyday olive oil for sauteing, roasting, and salad dressing.",
        "image": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "green-vegetables",
        "name": "Mixed Vegetables",
        "price": 7,
        "store": "Harvest Market",
        "department": "Food",
        "category": "Groceries",
        "description": "A fresh mix of greens and seasonal vegetables for cooking.",
        "image": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "dry-beans",
        "name": "Dry Beans Bag",
        "price": 5,
        "store": "Harvest Market",
        "department": "Food",
        "category": "Groceries",
        "description": "Pantry beans ready for soups, burritos, bowls, and chili.",
        "image": "https://images.unsplash.com/photo-1515543904379-3d757afe72e3?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "sweet-corn",
        "name": "Sweet Corn",
        "price": 4,
        "store": "Harvest Market",
        "department": "Food",
        "category": "Groceries",
        "description": "Fresh sweet corn for salads, sides, and skillet dishes.",
        "image": "https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "cafeteria-coffee",
        "name": "Fresh Brew Coffee",
        "price": 4,
        "store": "Sunrise Cafeteria",
        "department": "Food",
        "category": "Cafeteria",
        "description": "Hot brewed coffee served smooth and ready for the morning rush.",
        "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "hot-chocolate",
        "name": "Hot Chocolate",
        "price": 5,
        "store": "Sunrise Cafeteria",
        "department": "Food",
        "category": "Cafeteria",
        "description": "Rich hot chocolate topped with a creamy, comforting finish.",
        "image": "https://images.unsplash.com/photo-1517578239113-b03992dcdd25?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "oatmeal-bowl",
        "name": "Warm Oatmeal Bowl",
        "price": 7,
        "store": "Sunrise Cafeteria",
        "department": "Food",
        "category": "Breakfast",
        "description": "Hearty oatmeal bowl for breakfast with a soft, homestyle texture.",
        "image": "https://images.unsplash.com/photo-1517673400267-0251440c45dc?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "scrambled-eggs",
        "name": "Scrambled Eggs",
        "price": 8,
        "store": "Sunrise Cafeteria",
        "department": "Food",
        "category": "Breakfast",
        "description": "Fluffy scrambled eggs cooked fresh for a quick cafeteria breakfast.",
        "options": {
            "Bread": {
                "default": "White Toast",
                "choices": {"White Toast": 0, "Wheat Toast": 0.5, "Brioche": 1.0},
            },
            "Egg Type": {
                "default": "Regular Eggs",
                "choices": {"Regular Eggs": 0, "Egg Whites": 1.0, "Brown Farm Eggs": 1.5},
            },
        },
        "image": "https://images.unsplash.com/photo-1510693206972-df098062cb71?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "cooked-eggs",
        "name": "Cooked Eggs Plate",
        "price": 8,
        "store": "Sunrise Cafeteria",
        "department": "Food",
        "category": "Breakfast",
        "description": "Simple cooked eggs plate served hot and ready for breakfast orders.",
        "image": "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "fried-eggs",
        "name": "Fried Eggs",
        "price": 8,
        "store": "Sunrise Cafeteria",
        "department": "Food",
        "category": "Breakfast",
        "description": "Classic fried eggs with crisp edges and a tender center.",
        "options": {
            "Bread": {
                "default": "White Toast",
                "choices": {"White Toast": 0, "Wheat Toast": 0.5, "Brioche": 1.0},
            },
            "Egg Type": {
                "default": "Sunny Side Up",
                "choices": {"Sunny Side Up": 0, "Over Easy": 0.5, "Over Hard": 0.5, "Brown Farm Eggs": 1.5},
            },
        },
        "image": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "pain-relief",
        "name": "Pain Relief Tablets",
        "price": 11,
        "store": "CarePlus Pharmacy",
        "department": "Pharmacy",
        "category": "Pain Care",
        "description": "Fast-acting tablets for headaches, fever, and body aches.",
        "image": "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "vitamin-c",
        "name": "Vitamin C Gummies",
        "price": 14,
        "store": "CarePlus Pharmacy",
        "department": "Pharmacy",
        "category": "Wellness",
        "description": "Daily immune support gummies with orange flavor.",
        "image": "https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "cough-syrup",
        "name": "Cough Relief Syrup",
        "price": 13,
        "store": "CarePlus Pharmacy",
        "department": "Pharmacy",
        "category": "Cold Relief",
        "description": "Soothing syrup for cough and throat irritation.",
        "image": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "first-aid",
        "name": "First Aid Kit",
        "price": 22,
        "store": "CarePlus Pharmacy",
        "department": "Pharmacy",
        "category": "Essentials",
        "description": "Compact home kit with bandages, wipes, gauze, and tape.",
        "image": "https://images.unsplash.com/photo-1603398938378-e54eab446dde?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "craft-lager",
        "name": "Craft Lager Pack",
        "price": 18,
        "store": "Night Owl Spirits",
        "department": "Alcohol",
        "category": "Beer",
        "description": "Six-pack of crisp craft lager with a smooth finish.",
        "image": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "red-wine",
        "name": "Red Wine Bottle",
        "price": 24,
        "store": "Night Owl Spirits",
        "department": "Alcohol",
        "category": "Wine",
        "description": "Medium-bodied red wine with berry notes and soft tannins.",
        "image": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "whiskey",
        "name": "Reserve Whiskey",
        "price": 42,
        "store": "Night Owl Spirits",
        "department": "Alcohol",
        "category": "Spirits",
        "description": "Oak-aged whiskey with caramel, vanilla, and spice notes.",
        "image": "https://images.unsplash.com/photo-1527281400683-1aae777175f8?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": "hard-seltzer",
        "name": "Berry Hard Seltzer",
        "price": 16,
        "store": "Night Owl Spirits",
        "department": "Alcohol",
        "category": "Ready To Drink",
        "description": "Refreshing sparkling seltzer with berry flavor.",
        "image": "https://images.unsplash.com/photo-1609951651556-5334e2706168?auto=format&fit=crop&w=900&q=80",
    },
]

RENTAL_LISTINGS = [
    {
        "id": "downtown-loft",
        "name": "Downtown Loft",
        "price_label": "$1,850 / month",
        "description": "Bright one-bedroom loft with open kitchen, balcony, and quick access to restaurants and transit.",
        "image": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80",
        "map_url": "https://maps.google.com/maps?q=Downtown%20Miami&t=&z=13&ie=UTF8&iwloc=&output=embed",
    },
    {
        "id": "garden-apartment",
        "name": "Garden Apartment",
        "price_label": "$1,420 / month",
        "description": "Cozy rental with a green courtyard view, two bedrooms, and a calm residential setting.",
        "image": "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80",
        "map_url": "https://maps.google.com/maps?q=Brooklyn%20NY&t=&z=13&ie=UTF8&iwloc=&output=embed",
    },
    {
        "id": "city-studio",
        "name": "City Studio",
        "price_label": "$1,260 / month",
        "description": "Compact modern studio with smart storage, full bath, and walkable access to shops and nightlife.",
        "image": "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1200&q=80",
        "map_url": "https://maps.google.com/maps?q=Queens%20NY&t=&z=13&ie=UTF8&iwloc=&output=embed",
    },
]

ORDERS_FILE = Path(__file__).with_name("orders.xlsx")
PROMO_CODE = "DASHFOOD"
PROMO_THRESHOLD = 40
PROMO_RATE = 0.20
ITEM_LOOKUP = {item["id"]: item for item in MENU_ITEMS}


def format_currency(amount: int) -> str:
    return f"${amount:.2f}"


def build_initial_ingredient_state() -> dict:
    return {
        item["id"]: dict(item.get("ingredients", {}))
        for item in MENU_ITEMS
        if item["department"] == "Food" and item.get("ingredients")
    }


def build_initial_quantity_state() -> dict:
    return {item["id"]: 1 for item in MENU_ITEMS}


def build_initial_option_state() -> dict:
    return {
        item["id"]: {option_name: option_config["default"] for option_name, option_config in item.get("options", {}).items()}
        for item in MENU_ITEMS
        if item.get("options")
    }


def normalize_ingredient_state(ingredient_data: dict | None) -> dict:
    normalized = build_initial_ingredient_state()
    for item_id, ingredients in (ingredient_data or {}).items():
        if item_id not in normalized:
            continue
        for ingredient_name, quantity in ingredients.items():
            if ingredient_name in normalized[item_id]:
                normalized[item_id][ingredient_name] = max(0, int(quantity))
    return normalized


def normalize_quantity_state(quantity_data: dict | None) -> dict:
    normalized = build_initial_quantity_state()
    for item_id, quantity in (quantity_data or {}).items():
        if item_id in normalized:
            normalized[item_id] = max(1, int(quantity))
    return normalized


def normalize_option_state(option_data: dict | None) -> dict:
    normalized = build_initial_option_state()
    for item_id, selections in (option_data or {}).items():
        if item_id not in normalized:
            continue
        for option_name, selected_value in selections.items():
            option_config = ITEM_LOOKUP[item_id].get("options", {}).get(option_name)
            if option_config and selected_value in option_config["choices"]:
                normalized[item_id][option_name] = selected_value
    return normalized


def format_customizations(customizations: dict | None) -> str:
    if not customizations:
        return "Standard"
    return ", ".join(f"{name}: {value}" for name, value in customizations.items())


def merge_customizations(item: dict, ingredient_store: dict | None, option_store: dict | None) -> dict | None:
    customizations = {}
    if item.get("ingredients"):
        ingredient_state = normalize_ingredient_state(ingredient_store)
        customizations.update(dict(ingredient_state.get(item["id"], item["ingredients"])))
    if item.get("options"):
        option_state = normalize_option_state(option_store)
        customizations.update(dict(option_state.get(item["id"], build_initial_option_state().get(item["id"], {}))))
    return customizations or None


def compute_item_price(item: dict, customizations: dict | None) -> float:
    price = float(item["price"])
    if customizations:
        for ingredient_name, default_quantity in item.get("ingredients", {}).items():
            current_quantity = customizations.get(ingredient_name, default_quantity)
            unit_price = item.get("ingredient_prices", {}).get(ingredient_name, 0)
            price += (current_quantity - default_quantity) * unit_price

        for option_name, option_config in item.get("options", {}).items():
            selected_value = customizations.get(option_name, option_config["default"])
            price += option_config["choices"].get(selected_value, 0)

    return max(0, round(price, 2))


def build_cart_entry(
    item_id: str,
    ingredient_store: dict | None,
    option_store: dict | None,
    quantity_store: dict | None,
) -> dict:
    item = ITEM_LOOKUP[item_id]
    customizations = merge_customizations(item, ingredient_store, option_store)
    quantity_state = normalize_quantity_state(quantity_store)
    quantity = quantity_state.get(item_id, 1)
    unit_price = compute_item_price(item, customizations)

    return {
        "item_id": item["id"],
        "name": item["name"],
        "store": item["store"],
        "department": item["department"],
        "price": unit_price,
        "quantity": quantity,
        "customizations": customizations,
    }


def make_menu_card(item: dict, ingredient_store: dict, option_store: dict, quantity_store: dict) -> html.Article:
    ingredient_controls = []
    option_controls = []
    current_price = item["price"]
    selected_quantity = quantity_store.get(item["id"], 1)
    if item.get("ingredients"):
        current_ingredients = ingredient_store.get(item["id"], item["ingredients"])
        ingredient_controls = [
            html.Div(
                className="ingredient-picker",
                children=[
                    html.P("Ingredients", className="ingredient-picker__title"),
                    html.Div(
                        className="ingredient-picker__list",
                        children=[
                            html.Div(
                                className="ingredient-row",
                                children=[
                                    html.Span(ingredient_name, className="ingredient-row__label"),
                                    html.Span(
                                        format_currency(item.get("ingredient_prices", {}).get(ingredient_name, 0)),
                                        className="ingredient-row__price",
                                    ),
                                    html.Div(
                                        className="ingredient-row__controls",
                                        children=[
                                            html.Button(
                                                "-",
                                                id={
                                                    "type": "ingredient-minus",
                                                    "item": item["id"],
                                                    "ingredient": ingredient_name,
                                                },
                                                className="ingredient-row__button",
                                                n_clicks=0,
                                            ),
                                            html.Span(
                                                str(current_ingredients.get(ingredient_name, default_quantity)),
                                                className="ingredient-row__value",
                                            ),
                                            html.Button(
                                                "+",
                                                id={
                                                    "type": "ingredient-plus",
                                                    "item": item["id"],
                                                    "ingredient": ingredient_name,
                                                },
                                                className="ingredient-row__button",
                                                n_clicks=0,
                                            ),
                                        ],
                                    ),
                                ],
                            )
                            for ingredient_name, default_quantity in item["ingredients"].items()
                        ],
                    ),
                ],
            )
        ]
    if item.get("options"):
        current_options = option_store.get(item["id"], build_initial_option_state().get(item["id"], {}))
        option_controls = [
            html.Div(
                className="option-picker",
                children=[
                    html.P("Choose options", className="ingredient-picker__title"),
                    html.Div(
                        className="option-picker__list",
                        children=[
                            html.Div(
                                className="option-row",
                                children=[
                                    html.Div(
                                        className="option-row__copy",
                                        children=[
                                            html.Span(option_name, className="option-row__label"),
                                            html.Span(
                                                f"from {format_currency(min(option_config['choices'].values()))}",
                                                className="option-row__hint",
                                            ),
                                        ],
                                    ),
                                    dcc.Dropdown(
                                        id={"type": "item-option", "item": item["id"], "option": option_name},
                                        options=[
                                            {
                                                "label": f"{choice_name} ({format_currency(extra_price)})",
                                                "value": choice_name,
                                            }
                                            for choice_name, extra_price in option_config["choices"].items()
                                        ],
                                        value=current_options.get(option_name, option_config["default"]),
                                        clearable=False,
                                        searchable=False,
                                        className="option-row__dropdown",
                                    ),
                                ],
                            )
                            for option_name, option_config in item["options"].items()
                        ],
                    ),
                ],
            )
        ]
    current_price = compute_item_price(item, merge_customizations(item, ingredient_store, option_store))
    line_total = current_price * selected_quantity

    return html.Article(
        className="menu-card",
        children=[
            html.Div(
                className="menu-card__image",
                style={"backgroundImage": f"url('{item['image']}')"},
            ),
            html.Div(
                className="menu-card__body",
                children=[
                    html.Span(item["store"], className="menu-card__store"),
                    html.Span(item["category"], className="menu-card__tag"),
                    html.H3(item["name"]),
                    html.P(item["description"], className="menu-card__description"),
                    *ingredient_controls,
                    *option_controls,
                    html.Div(
                        className="menu-card__footer",
                        children=[
                            html.Div(
                                className="menu-card__purchase",
                                children=[
                                    html.Div(
                                        className="card-quantity",
                                        children=[
                                            html.Button(
                                                "-",
                                                id={"type": "qty-minus", "item": item["id"]},
                                                className="card-quantity__button",
                                                n_clicks=0,
                                            ),
                                            html.Span(str(selected_quantity), className="card-quantity__value"),
                                            html.Button(
                                                "+",
                                                id={"type": "qty-plus", "item": item["id"]},
                                                className="card-quantity__button",
                                                n_clicks=0,
                                            ),
                                        ],
                                    ),
                                    html.Span(format_currency(line_total), className="menu-card__price"),
                                ],
                            ),
                            html.Div(
                                className="menu-card__actions",
                                children=[
                                    html.Button(
                                        "Add to cart",
                                        id={"type": "add-button", "index": item["id"]},
                                        className="menu-card__button",
                                        n_clicks=0,
                                    ),
                                    html.A("Buy now", href="#checkout", className="menu-card__buy-now"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def grouped_menu_items(department: str):
    grouped = {}
    for item in MENU_ITEMS:
        if item["department"] != department:
            continue
        grouped.setdefault(item["store"], []).append(item)
    return grouped


def store_anchor_id(store_name: str) -> str:
    return "store-" + "".join(char.lower() if char.isalnum() else "-" for char in store_name).strip("-")


def food_store_previews() -> html.Div:
    preview_cards = []
    for store_name, items in grouped_menu_items("Food").items():
        hero_item = items[0]
        categories = sorted({item["category"] for item in items})
        category_label = " . ".join(categories[:2])
        preview_cards.append(
            html.A(
                className="store-preview-card",
                href=f"#{store_anchor_id(store_name)}",
                children=[
                    html.Div(
                        className="store-preview-card__image",
                        style={"backgroundImage": f"url('{hero_item['image']}')"},
                    ),
                    html.Strong(store_name),
                    html.Span(category_label),
                ],
            )
        )

    return html.Div(
        className="store-preview",
        children=[
            html.Div(
                className="store-preview__header",
                children=[
                    html.Strong("5 stores under Food"),
                    html.Span("Browse by store before jumping into the full menu below."),
                ],
            ),
            html.Div(className="store-preview__grid", children=preview_cards),
        ],
    )


def department_pills(active_department: str) -> html.Div:
    departments = [
        ("Food", "/", "Live now"),
        ("Rental", "/rental", "Places"),
        ("Alcohol", "/alcohol", "Open now"),
    ]
    return html.Section(
        className="department-strip",
        children=[
            dcc.Link(
                className=(
                    "department-pill department-pill--active"
                    if label == active_department
                    else "department-pill"
                ),
                href=href,
                children=[
                    html.Strong(label),
                    html.Span(status),
                ],
            )
            for label, href, status in departments
        ],
    )


def store_sections(department: str, store_caption: str, ingredient_store: dict, option_store: dict, quantity_store: dict) -> html.Div:
    return html.Div(
        className="store-sections",
        children=[
            html.Section(
                id=store_anchor_id(store_name),
                className="store-section",
                children=[
                    html.Div(
                        className="store-section__header",
                        children=[
                            html.H3(store_name),
                            html.P(store_caption),
                        ],
                    ),
                    html.Div(
                        className="menu-grid",
                        children=[make_menu_card(item, ingredient_store, option_store, quantity_store) for item in items],
                    ),
                ],
            )
            for store_name, items in grouped_menu_items(department).items()
        ],
    )


def compute_discount(subtotal: int, promo_code: str) -> int:
    if (promo_code or "").strip().upper() == PROMO_CODE and subtotal >= PROMO_THRESHOLD:
        return round(subtotal * PROMO_RATE)
    return 0


def serialize_order_items(cart_data: list, promo_code: str) -> tuple[str, int, int, int]:
    order_parts = []
    subtotal = 0
    for entry in cart_data or []:
        line_total = float(entry["price"]) * entry.get("quantity", 1)
        subtotal += line_total
        customizations = format_customizations(entry.get("customizations"))
        order_parts.append(
            f"{entry['store']} - {entry['name']} x{entry['quantity']} [{customizations}] ({format_currency(line_total)})"
        )

    discount = compute_discount(subtotal, promo_code)
    total = subtotal - discount
    return " | ".join(order_parts), subtotal, discount, total


def save_order_to_excel(
    customer_name: str,
    phone: str,
    address: str,
    promo_code: str,
    cart_data: list,
) -> None:
    order_items, subtotal, discount, total = serialize_order_items(cart_data, promo_code)
    active_departments = sorted({entry["department"] for entry in cart_data})
    active_stores = sorted({entry["store"] for entry in cart_data})
    order_row = {
        "order_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "department": ", ".join(active_departments),
        "stores": ", ".join(active_stores),
        "customer_name": customer_name.strip(),
        "phone": phone.strip(),
        "address": address.strip(),
        "promo_code": promo_code.strip().upper() or "NONE",
        "items": order_items,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
    }

    if ORDERS_FILE.exists():
        existing_orders = pd.read_excel(ORDERS_FILE)
        updated_orders = pd.concat([existing_orders, pd.DataFrame([order_row])], ignore_index=True)
    else:
        updated_orders = pd.DataFrame([order_row])

    updated_orders.to_excel(ORDERS_FILE, index=False)


app = Dash(__name__)
server = app.server


app.layout = html.Div(
    className="page-shell",
    children=[
        dcc.Location(id="url"),
        dcc.Store(id="cart-store", data=[]),
        dcc.Store(id="ingredient-store", data=build_initial_ingredient_state()),
        dcc.Store(id="option-store", data=build_initial_option_state()),
        dcc.Store(id="quantity-store", data=build_initial_quantity_state()),
        html.Div(id="page-content"),
    ],
)


def checkout_panel() -> html.Section:
    return html.Section(
        id="checkout",
        className="checkout-section",
        children=[
            html.Div(
                className="checkout-card",
                children=[
                    html.Div(
                        className="section-heading section-heading--compact",
                        children=[
                            html.Span("Cart", className="eyebrow eyebrow--dark"),
                            html.H2("Your order"),
                        ],
                    ),
                    html.Div(id="cart-items", className="cart-items"),
                    html.Div(
                        className="checkout-fields",
                        children=[
                            dcc.Input(
                                id="customer-name",
                                type="text",
                                placeholder="Customer name",
                                className="checkout-input",
                            ),
                            dcc.Input(
                                id="customer-phone",
                                type="text",
                                placeholder="Phone number",
                                className="checkout-input",
                            ),
                            dcc.Textarea(
                                id="customer-address",
                                placeholder="Delivery address",
                                className="checkout-textarea",
                            ),
                            dcc.Input(
                                id="promo-code",
                                type="text",
                                placeholder=f"Promo code (try {PROMO_CODE})",
                                className="checkout-input",
                            ),
                        ],
                    ),
                    html.Div(
                        className="checkout-summary",
                        children=[
                            html.Div(
                                className="summary-row",
                                children=[
                                    html.Span("Subtotal"),
                                    html.Strong(id="cart-subtotal", children=format_currency(0)),
                                ],
                            ),
                            html.Div(
                                className="summary-row",
                                children=[
                                    html.Span("Delivery"),
                                    html.Strong("Free"),
                                ],
                            ),
                            html.Div(
                                className="summary-row",
                                children=[
                                    html.Span("Discount"),
                                    html.Strong(id="cart-discount", children=format_currency(0)),
                                ],
                            ),
                            html.Div(
                                className="summary-row summary-row--total",
                                children=[
                                    html.Span("Total"),
                                    html.Strong(id="cart-total", children=format_currency(0)),
                                ],
                            ),
                        ],
                    ),
                    html.Div(id="checkout-message", className="checkout-message"),
                    html.Button(
                        "Checkout",
                        id="checkout-button",
                        className="button button--solid button--full",
                        n_clicks=0,
                    ),
                ],
            )
        ],
    )


def food_page(ingredient_store: dict, option_store: dict, quantity_store: dict) -> list:
    return [
        html.Header(
            className="hero",
            children=[
                html.Div(
                    className="hero__copy",
                    children=[
                        html.Span("Urban Bites", className="eyebrow"),
                        html.H1("Food marketplace with multiple stores in one website."),
                        html.P(
                            "Run one storefront with multiple food stores today and room to add "
                            "new departments like pharmacy later."
                        ),
                        html.Div(
                            className="hero__actions",
                            children=[
                                html.A("Order now", href="#menu", className="button button--solid"),
                                html.A("View deals", href="#deals", className="button button--ghost"),
                            ],
                        ),
                        food_store_previews(),
                    ],
                ),
                html.Div(
                    className="hero__spotlight",
                    children=[
                        html.Div(
                            className="spotlight-card",
                            children=[
                                html.P("Featured department", className="spotlight-card__label"),
                                html.H2("Food Department"),
                                html.P(
                                    "Customize each food item with plus and minus ingredient controls before adding it."
                                ),
                                html.Div(
                                    className="spotlight-card__price-row",
                                    children=[
                                        html.Span(format_currency(15), className="spotlight-card__price"),
                                        html.Span("Burrito starts with rice 5", className="spotlight-card__meta"),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),
        html.Main(
            children=[
                html.Section(
                    id="deals",
                    className="promo-strip",
                    children=[
                        html.Div(
                            children=[
                                html.Span("Weekend special", className="eyebrow eyebrow--dark"),
                                html.H2("Save 20% when food orders hit $40 or more."),
                            ]
                        ),
                        html.P(
                            f"Use code {PROMO_CODE} at checkout to unlock a bundle discount for orders of ${PROMO_THRESHOLD} or more."
                        ),
                    ],
                ),
                department_pills("Food"),
                html.Section(
                    id="menu",
                    className="content-grid",
                    children=[
                        html.Div(
                            className="section-heading",
                            children=[
                                html.Span("Food", className="eyebrow eyebrow--dark"),
                                html.H2("Order from multiple stores"),
                                html.P(
                                    "Kitchen, pizza, beverages, groceries, and cafeteria breakfast all share one cart, with ingredient counts on each food card."
                                ),
                            ],
                        ),
                        store_sections("Food", "Food store", ingredient_store, option_store, quantity_store),
                    ],
                ),
                checkout_panel(),
            ]
        ),
    ]


def rental_page() -> list:
    return [
        html.Header(
            className="hero",
            children=[
                html.Div(
                    className="hero__copy",
                    children=[
                        html.Span("Rental", className="eyebrow"),
                        html.H1("Find rental places from the same website."),
                        html.P(
                            "Browse apartments and places to rent with photos, map views, pricing, "
                            "and short descriptions in one page."
                        ),
                        html.Div(
                            className="hero__actions",
                            children=[
                                html.A("View rentals", href="#rentals", className="button button--solid"),
                                dcc.Link("Back to food", href="/", className="button button--ghost"),
                            ],
                        ),
                        html.Ul(
                            className="hero__stats",
                            children=[
                                html.Li([html.Strong("3 places"), html.Span("ready to view")]),
                                html.Li([html.Strong("Map"), html.Span("inside each card")]),
                                html.Li([html.Strong("Price"), html.Span("shown clearly")]),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="hero__spotlight",
                    children=[
                        html.Div(
                            className="spotlight-card",
                            children=[
                                html.P("Featured department", className="spotlight-card__label"),
                                html.H2("Rental Department"),
                                html.P(
                                    "Each listing shows a rental photo, a location map, the monthly price, and a short overview."
                                ),
                                html.Div(
                                    className="spotlight-card__price-row",
                                    children=[
                                        html.Span("$1,260+", className="spotlight-card__price"),
                                        html.Span("Monthly rent", className="spotlight-card__meta"),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),
        html.Main(
            children=[
                html.Section(
                    className="promo-strip",
                    children=[
                        html.Div(
                            children=[
                                html.Span("Rental", className="eyebrow eyebrow--dark"),
                                html.H2("Places to rent with picture, map, and price."),
                            ]
                        ),
                        html.P(
                            "Open each listing window below to compare homes and neighborhoods quickly."
                        ),
                    ],
                ),
                department_pills("Rental"),
                html.Section(
                    id="rentals",
                    className="content-grid",
                    children=[
                        html.Div(
                            className="section-heading",
                            children=[
                                html.Span("Rental", className="eyebrow eyebrow--dark"),
                                html.H2("Places available for rent"),
                                html.P(
                                    "Review the property image, map, monthly price, and description for each place."
                                ),
                            ],
                        ),
                        html.Div(
                            className="rental-grid",
                            children=[
                                html.Article(
                                    className="rental-card",
                                    children=[
                                        html.Div(
                                            className="rental-card__image",
                                            style={"backgroundImage": f"url('{listing['image']}')"},
                                        ),
                                        html.Div(
                                            className="rental-card__body",
                                            children=[
                                                html.Div(
                                                    className="rental-card__header",
                                                    children=[
                                                        html.H3(listing["name"]),
                                                        html.Strong(listing["price_label"], className="rental-card__price"),
                                                    ],
                                                ),
                                                html.P(listing["description"], className="rental-card__description"),
                                                html.Iframe(
                                                    src=listing["map_url"],
                                                    className="rental-card__map",
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                                for listing in RENTAL_LISTINGS
                            ],
                        ),
                    ],
                ),
            ]
        ),
    ]


def alcohol_page(ingredient_store: dict, option_store: dict, quantity_store: dict) -> list:
    return [
        html.Header(
            className="hero",
            children=[
                html.Div(
                    className="hero__copy",
                    children=[
                        html.Span("Night Owl", className="eyebrow"),
                        html.H1("Alcohol delivery now lives beside food and pharmacy."),
                        html.P(
                            "Open the alcohol department from the same website and browse beer, wine, "
                            "spirits, and ready-to-drink options from Night Owl Spirits."
                        ),
                        html.Div(
                            className="hero__actions",
                            children=[
                                html.A("Shop alcohol", href="#menu", className="button button--solid"),
                                dcc.Link("Back to food", href="/", className="button button--ghost"),
                            ],
                        ),
                        html.Ul(
                            className="hero__stats",
                            children=[
                                html.Li([html.Strong("1 store"), html.Span("Night Owl Spirits")]),
                                html.Li([html.Strong("Beer"), html.Span("wine and spirits")]),
                                html.Li([html.Strong("Same"), html.Span("shared cart")]),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="hero__spotlight",
                    children=[
                        html.Div(
                            className="spotlight-card",
                            children=[
                                html.P("Featured department", className="spotlight-card__label"),
                                html.H2("Alcohol Department"),
                                html.P(
                                    "A dedicated store page for beer, wine, whiskey, and canned drinks."
                                ),
                                html.Div(
                                    className="spotlight-card__price-row",
                                    children=[
                                        html.Span(format_currency(16), className="spotlight-card__price"),
                                        html.Span("Starting price", className="spotlight-card__meta"),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),
        html.Main(
            children=[
                html.Section(
                    className="promo-strip",
                    children=[
                        html.Div(
                            children=[
                                html.Span("Alcohol", className="eyebrow eyebrow--dark"),
                                html.H2("Beer, wine, and spirits from a dedicated store page."),
                            ]
                        ),
                        html.P(
                            "Night Owl Spirits is available as its own department beside Food and Pharmacy."
                        ),
                    ],
                ),
                department_pills("Alcohol"),
                html.Section(
                    id="menu",
                    className="content-grid",
                    children=[
                        html.Div(
                            className="section-heading",
                            children=[
                                html.Span("Alcohol", className="eyebrow eyebrow--dark"),
                                html.H2("Alcohol store catalog"),
                                html.P(
                                    "Browse alcoholic drinks on their own page while keeping the same website flow."
                                ),
                            ],
                        ),
                        store_sections("Alcohol", "Alcohol store", ingredient_store, option_store, quantity_store),
                    ],
                ),
                checkout_panel(),
            ]
        ),
    ]


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    Input("ingredient-store", "data"),
    Input("option-store", "data"),
    Input("quantity-store", "data"),
)
def render_page(pathname, ingredient_store, option_store, quantity_store):
    ingredient_store = normalize_ingredient_state(ingredient_store)
    option_store = normalize_option_state(option_store)
    quantity_store = normalize_quantity_state(quantity_store)
    if pathname == "/alcohol":
        return alcohol_page(ingredient_store, option_store, quantity_store)
    if pathname == "/rental":
        return rental_page()
    return food_page(ingredient_store, option_store, quantity_store)


@app.callback(
    Output("ingredient-store", "data"),
    Input({"type": "ingredient-minus", "item": ALL, "ingredient": ALL}, "n_clicks"),
    Input({"type": "ingredient-plus", "item": ALL, "ingredient": ALL}, "n_clicks"),
    State("ingredient-store", "data"),
    prevent_initial_call=True,
)
def update_ingredient_store(_minus_clicks, _plus_clicks, ingredient_store):
    triggered = callback_context.triggered_id
    if not triggered:
        return no_update

    updated_store = normalize_ingredient_state(ingredient_store)
    item_id = triggered["item"]
    ingredient_name = triggered["ingredient"]
    delta = -1 if triggered["type"] == "ingredient-minus" else 1
    current_value = updated_store[item_id][ingredient_name]
    updated_store[item_id][ingredient_name] = max(0, current_value + delta)
    return updated_store


@app.callback(
    Output("option-store", "data"),
    Input({"type": "item-option", "item": ALL, "option": ALL}, "value"),
    State("option-store", "data"),
    prevent_initial_call=True,
)
def update_option_store(_values, option_store):
    triggered = callback_context.triggered_id
    if not triggered:
        return no_update

    updated_store = normalize_option_state(option_store)
    item_id = triggered["item"]
    option_name = triggered["option"]
    selected_value = callback_context.triggered[0]["value"]
    option_config = ITEM_LOOKUP[item_id].get("options", {}).get(option_name)
    if option_config and selected_value in option_config["choices"]:
        updated_store[item_id][option_name] = selected_value
    return updated_store


@app.callback(
    Output("quantity-store", "data"),
    Input({"type": "qty-minus", "item": ALL}, "n_clicks"),
    Input({"type": "qty-plus", "item": ALL}, "n_clicks"),
    State("quantity-store", "data"),
    prevent_initial_call=True,
)
def update_quantity_store(_minus_clicks, _plus_clicks, quantity_store):
    triggered = callback_context.triggered_id
    if not triggered:
        return no_update

    updated_store = normalize_quantity_state(quantity_store)
    item_id = triggered["item"]
    delta = -1 if triggered["type"] == "qty-minus" else 1
    updated_store[item_id] = max(1, updated_store[item_id] + delta)
    return updated_store


@app.callback(
    Output("cart-store", "data"),
    Input({"type": "add-button", "index": ALL}, "n_clicks"),
    State("cart-store", "data"),
    State("ingredient-store", "data"),
    State("option-store", "data"),
    State("quantity-store", "data"),
    prevent_initial_call=True,
)
def update_cart(_clicks, cart_data, ingredient_store, option_store, quantity_store):
    cart_data = cart_data or []
    triggered = callback_context.triggered_id
    if not triggered:
        return cart_data

    item_id = triggered["index"]
    updated_cart = list(cart_data)
    updated_cart.append(build_cart_entry(item_id, ingredient_store, option_store, quantity_store))
    return updated_cart


@app.callback(
    Output("cart-items", "children"),
    Output("cart-subtotal", "children"),
    Output("cart-discount", "children"),
    Output("cart-total", "children"),
    Input("cart-store", "data"),
    Input("promo-code", "value"),
)
def render_cart(cart_data, promo_code):
    cart_data = cart_data or []
    if not cart_data:
        empty_state = html.Div(
            className="empty-cart",
            children="Your cart is empty. Add a few dishes to start an order.",
        )
        return empty_state, format_currency(0), format_currency(0), format_currency(0)

    line_items = []
    subtotal = 0
    for entry in cart_data:
        line_total = float(entry["price"]) * entry.get("quantity", 1)
        subtotal += line_total
        line_items.append(
            html.Div(
                className="cart-line",
                children=[
                    html.Div(
                        children=[
                            html.Strong(entry["name"]),
                            html.P(
                                f"{entry['store']} | Qty {entry['quantity']}",
                                className="cart-line__meta",
                            ),
                            html.P(
                                format_customizations(entry.get("customizations")),
                                className="cart-line__meta cart-line__meta--small",
                            ),
                        ]
                    ),
                    html.Strong(format_currency(line_total)),
                ],
            )
        )

    discount = compute_discount(subtotal, promo_code)
    total = subtotal - discount
    return line_items, format_currency(subtotal), format_currency(discount), format_currency(total)


@app.callback(
    Output("checkout-message", "children"),
    Output("cart-store", "data", allow_duplicate=True),
    Output("ingredient-store", "data", allow_duplicate=True),
    Output("option-store", "data", allow_duplicate=True),
    Output("quantity-store", "data", allow_duplicate=True),
    Output("customer-name", "value"),
    Output("customer-phone", "value"),
    Output("customer-address", "value"),
    Input("checkout-button", "n_clicks"),
    State("customer-name", "value"),
    State("customer-phone", "value"),
    State("customer-address", "value"),
    State("promo-code", "value"),
    State("cart-store", "data"),
    prevent_initial_call=True,
)
def complete_checkout(n_clicks, customer_name, phone, address, promo_code, cart_data):
    if not n_clicks:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

    customer_name = (customer_name or "").strip()
    phone = (phone or "").strip()
    address = (address or "").strip()
    promo_code = (promo_code or "").strip()
    cart_data = cart_data or []

    if not cart_data:
        return "Add at least one item before checking out.", no_update, no_update, no_update, no_update, no_update, no_update, no_update

    if not customer_name or not phone or not address:
        return (
            "Fill in your name, phone, and address before placing the order.",
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )

    try:
        save_order_to_excel(customer_name, phone, address, promo_code, cart_data)
    except Exception as exc:
        return f"Order could not be saved: {exc}", no_update, no_update, no_update, no_update, no_update, no_update, no_update

    _, _, discount, total = serialize_order_items(cart_data, promo_code)
    discount_message = (
        f" Discount applied: {format_currency(discount)}."
        if discount
        else " No discount applied."
    )
    return (
        f"Order saved to {ORDERS_FILE.name}. Final total: {format_currency(total)}.{discount_message}",
        [],
        build_initial_ingredient_state(),
        build_initial_option_state(),
        build_initial_quantity_state(),
        "",
        "",
        "",
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)
