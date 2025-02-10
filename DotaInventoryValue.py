import streamlit as st
import requests
import pandas as pd
import json
import time

DOTA_APP_ID = 570  # Dota 2 App ID
DOTA_CONTEXT_ID = 2  # Correct context ID for Dota 2

# Function to fetch Steam inventory
def fetch_inventory(steam_id):
    url = f"https://steamcommunity.com/inventory/{steam_id}/{DOTA_APP_ID}/{DOTA_CONTEXT_ID}?l=english&count=5000"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Cache item price requests to improve speed
@st.cache_data
def fetch_item_price(item_name):
    market_url = f"https://steamcommunity.com/market/priceoverview/?currency=1&appid={DOTA_APP_ID}&market_hash_name={item_name}"
    for _ in range(3):  # Retry up to 3 times if price is missing
        response = requests.get(market_url)
        if response.status_code == 200:
            data = response.json()
            if "lowest_price" in data:
                return data["lowest_price"]
        time.sleep(1)  # Wait before retrying
    return "Not Available"  # More descriptive message

# Streamlit UI
st.title("Dota 2 Inventory Value Calculator")

steam_id = st.text_input("Enter your Steam ID:")

if st.button("Calculate Inventory Value") and steam_id:
    inventory_data = fetch_inventory(steam_id)
    if inventory_data and "descriptions" in inventory_data:
        item_values = []
        total_value = 0.0
        progress_bar = st.progress(0)
        total_items = len(inventory_data["descriptions"])
        
        for idx, item in enumerate(inventory_data["descriptions"]):
            item_name = item.get("market_hash_name", "Unknown Item")
            price = fetch_item_price(item_name)
            
            if price.startswith("$"):
                price_value = float(price.replace("$", ""))
                total_value += price_value
            else:
                price_value = "Not Available"
            
            item_values.append({"Item Name": item_name, "Value": price})
            progress_bar.progress((idx + 1) / total_items)
        
        df = pd.DataFrame(item_values)
        st.write("### Inventory Items & Values")
        st.dataframe(df)
        
        st.write(f"## Total Inventory Value: ${total_value:.2f}")
    else:
        st.error("Failed to fetch inventory. Make sure your inventory is public and the Steam ID is correct.")