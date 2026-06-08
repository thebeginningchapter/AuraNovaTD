import streamlit as st
import json
import os

st.set_page_config(page_title="My Resell WMS", page_icon="📦", layout="centered")
st.title("📦 Aura Nova WMS (Αυτόνομο)")

DATA_FILE = "wms_data.json"

# Αρχικά δεδομένα αν το αρχείο δεν υπάρχει ακόμα
DEFAULT_DATA = {
    "iPhone 11": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 12": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 13": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 14": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0}
}

# Συναρτήσεις για διάβασμα και γράψιμο στο τοπικό αρχείο
def load_inventory():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_DATA

def save_inventory(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Φόρτωση δεδομένων στη μνήμη
inventory = load_inventory()

# Εμφάνιση των προϊόντων
for model, stats in inventory.items():
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
            qty_in = st.number_input("Πόσα κομμάτια αγόρασες;", min_value=1, step=1, key=f"q_{model}")
            cost_in = st.number_input("Συνολικό Κόστος Νέας Αγοράς (€)", min_value=0.0, step=0.5, key=f"c_{model}")
            
            if st.button("🚀 Επιβεβαίωση Restock", key=f"b_r_{model}"):
                inventory[model]["total_stock"] += qty_in
                inventory[model]["stock"] += qty_in
                inventory[model]["total_cost"] += cost_in
                
                save_inventory(inventory)
                st.success("Το Restock καταγράφηκε επιτυχώς!")
                st.rerun()
                
        elif action == "💰 Καταγραφή Πώλησης":
            qty_out = st.number_input("Πόσα τεμάχια πούλησες;", min_value=1, step=1, key=f"qo_{model}")
            price_out = st.number_input("Συνολική Τιμή Πώλησης (€)", min_value=0.0, step=0.5, key=f"p_{model}")
            
            if st.button("🚀 Επιβεβαίωση Πώλησης", key=f"b_s_{model}"):
                if inventory[model]["stock"] >= qty_out:
                    inventory[model]["stock"] -= qty_out
                    inventory[model]["sold"] += qty_out
                    inventory[model]["sold_profit"] += price_out
                    
                    save_inventory(inventory)
                    st.success("Η πώληση καταγράφηκε επιτυχώς!")
                    st.rerun()
                else:
                    st.error("❌ Δεν έχεις τόσο στοκ στην αποθήκη!")
        st.markdown("---")
