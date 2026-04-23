from datetime import datetime
from pathlib import Path

import os,sys

sys.path.append(os.getcwd())

import pandas as pd
from dash import Dash, Input, Output, State, ALL, dcc, html, callback_context, no_update
from help_fun import (build_initial_ingredient_state,build_cart_entry,build_initial_option_state,build_initial_quantity_state,format_currency,
                      normalize_ingredient_state,normalize_quantity_state,normalize_option_state,alcohol_page,rental_page,
                      food_page,format_customizations,compute_discount,save_order_to_excel,serialize_order_items)
from help_DATA import get_dict_RENTAL_LISTINGS,get_dict_MENU_ITEMS







DRIVE_FILE_ID='1GjRXG_U_i_KF_UleYquU-nekznqN7Evnv389ZdE6tQQ'


MENU_ITEMS=get_dict_RENTAL_LISTINGS()



ORDERS_FILE = Path(__file__).with_name("orders.xlsx")
PROMO_CODE = "DASHFOOD"
PROMO_THRESHOLD = 40
PROMO_RATE = 0.20
ITEM_LOOKUP = {item["id"]: item for item in MENU_ITEMS}



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
        save_order_to_excel(customer_name, phone, address, promo_code, cart_data,ORDERS_FILE,DRIVE_FILE_ID,)
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
