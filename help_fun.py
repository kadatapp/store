

from datetime import datetime
from pathlib import Path

import pandas as pd
from dash import Dash, Input, Output, State, ALL, dcc, html, callback_context, no_update
from help_DATA import get_dict_MENU_ITEMS,get_dict_RENTAL_LISTINGS

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload









MENU_ITEMS =get_dict_MENU_ITEMS()
RENTAL_LISTINGS=get_dict_RENTAL_LISTINGS()


PROMO_CODE = "DASHFOOD"
PROMO_THRESHOLD = 40
PROMO_RATE = 0.20
ITEM_LOOKUP = {item["id"]: item for item in MENU_ITEMS}















SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def upload_to_drive(file_path, file_id):
    service = get_drive_service()

    media = MediaFileUpload(
        file_path,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    service.files().update(
        fileId=file_id,
        media_body=media
    ).execute()





from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = "1GjRXG_U_i_KF_UleYquU-nekznqN7Evnv389ZdE6tQQ"
RANGE = "Sheet1!A:Z"

# def get_sheets_service():
#     creds = service_account.Credentials.from_service_account_file(
#         "service_account.json",
#         scopes=SCOPES
#     )
#     return build("sheets", "v4", credentials=creds)
import os, json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]





 
def get_service():
    with open("service_account.json") as f:
        creds_dict = json.load(f)

    # # Fix newline issue
    # creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )

    return build("sheets", "v4", credentials=creds)




import os, json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheets_service():
    creds_dict = json.loads(os.environ["GOOGLE_CREDS"])

    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )

    return build("sheets", "v4", credentials=creds)

def save_order_to_sheet(order_row: dict):
    service = get_service()

    values = [[
        order_row["order_time"],
        order_row["department"],
        order_row["stores"],
        order_row["customer_name"],
        order_row["phone"],
        order_row["address"],
        order_row["promo_code"],
        order_row["items"],
        order_row["subtotal"],
        order_row["discount"],
        order_row["total"],
    ]]

    body = {"values": values}

    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()




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
    ORDERS_FILE,
    DRIVE_FILE_ID, 
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

    # updated_orders.to_excel(ORDERS_FILE, index=False)
    # upload_to_drive(str(ORDERS_FILE), DRIVE_FILE_ID)
    save_order_to_sheet(order_row)





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



