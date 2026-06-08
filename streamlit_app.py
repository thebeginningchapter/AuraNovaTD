import streamlit as st
import json
import os

# Ρύθμιση σελίδας για το κινητό
st.set_page_config(page_title="AuraNovaTD WMS", page_icon="📦", layout="centered")
st.title("📦 AuraNovaTD WMS")

# Τοπικό αρχείο αποθήκευσης στον server
DATA_FILE = "wms_data.json"

# Η ΣΩΣΤΗ ΛΙΣΤΑ ΜΟΝΤΕΛΩΝ ΜΕ ΤΑ GROUP ΣΟΥ
DEFAULT_DATA = {
    "iPhone 13 / 13 Pro / 14 / 16e / 17e": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 15 Pro": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 15 Pro Max": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 15 / 16": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 16 Pro": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 16 Pro Max": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 17": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 17 Pro": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 17 Pro Max": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0}
}

def load_inventory():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                current_data = json.load(f)
                # Προσθήκη νέων μοντέλων αν λείπουν από το αρχείο, χωρίς διαγραφή των παλιών
                for model in DEFAULT_DATA:
                    if model not in current_data:
                        current_data[model] = DEFAULT_DATA[model]
                return current_data
        except:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_inventory(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "wms_data" not in st.session_state:
    st.session_state.wms_data = load_inventory()

inventory = st.session_state.wms_data

# Εμφάνιση των προϊόντων με τη νέα σειρά
for model in DEFAULT_DATA.keys():
    if model not in inventory:
        inventory[model] = DEFAULT_DATA[model]
        
    stats = inventory[model]
    net_profit = stats["sold_profit"] - stats["total_cost"]
    
    with st.container():
        st.markdown(f"### 📱 {model}")
        
        col1, col2 = st.columns(2)
        col1.metric("Στοκ Αποθήκης", stats["stock"])
        col2.metric("Πουλήθηκαν (Sold)", stats["sold"])
        
        col3, col4 = st.columns(2)
        col3.metric("Συνολικά Αγορασμένα", stats["total_stock"])
        col4.metric("Καθαρό Κέρδος", f"{net_profit:.2f}€")
        
        action = st.radio(f"Ενέργεια για {model}", ["Αναμονή", "🔄 Restock (Αγορά)", "💰 Καταγραφή Πώλησης"], key=f"act_{model}")
        
        if action == "🔄 Restock (Αγορά)":
            qty_in = st.number_input("Πόσα κομμάτια αγόρασες;", min_value=0, step=1, key=f"q_{model}")
            cost_in = st.number_input("Συνολικό Κόστος Νέας Αγοράς (€)", min_value=0.0, step=0.5, key=f"c_{model}")
            
            if st.button("🚀 Επιβεβαίωση Restock", key=f"b_r_{model}"):
                if qty_in <= 0:
                    st.error("❌ Πρέπει να δηλώσεις τουλάχιστον 1 τεμάχιο για να κάνεις Restock!")
                else:
                    inventory[model]["total_stock"] += qty_in
                    inventory[model]["stock"] += qty_in
                    inventory[model]["total_cost"] += cost_in
                    
                    st.session_state.wms_data = inventory
                    save_inventory(inventory)
                    st.success("Το Restock καταγράφηκε επιτυχώς!")
                    st.rerun()
                
        elif action == "💰 Καταγραφή Πώλησης":
            qty_out = st.number_input("Πόσα τεμάχια πούλησες;", min_value=0, step=1, key=f"qo_{model}")
            price_out = st.number_input("Συνολική Τιμή Πώλησης (€)", min_value=0.0, step=0.5, key=f"p_{model}")
            
            if st.button("🚀 Επιβεβαίωση Πώλησης", key=f"b_s_{model}"):
                if qty_out <= 0:
                    st.error("❌ Πρέπει να δηλώσεις τουλάχιστον 1 τεμάχιο για να καταγράψεις πώληση!")
                elif inventory[model]["stock"] >= qty_out:
                    inventory[model]["stock"] -= qty_out
                    inventory[model]["sold"] += qty_out
                    inventory[model]["sold_profit"] += price_out
                    
                    st.session_state.wms_data = inventory
                    save_inventory(inventory)
                    st.success("Η πώληση καταγράφηκε επιτυχώς!")
                    st.rerun()
                else:
                    st.error("❌ Δεν έχεις τόσο στοκ στην αποθήκη!")
        st.markdown("---")
