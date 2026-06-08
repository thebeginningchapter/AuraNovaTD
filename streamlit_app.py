import streamlit as st
import json
import os

# Ρύθμιση σελίδας για το κινητό
st.set_page_config(page_title="AuraNovaTD WMS", page_icon="📦", layout="centered")
st.title("📦 AuraNovaTD WMS (100% Αυτόματο)")

# Αρχικά δεδομένα
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

# Χρήση του αυτόματου τοπικού Storage που συγχρονίζεται με τον server
# (Σημείωση: Χρησιμοποιούμε μια μόνιμη SQL δομή μέσω της Streamlit για να μην χάνεται)
import sqlite3
conn = sqlite3.connect('auranova_wms.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS inventory (model TEXT PRIMARY KEY, data TEXT)''')
conn.commit()

def load_from_db():
    c.execute("SELECT * FROM inventory")
    rows = c.fetchall()
    if not rows:
        # Αν η βάση είναι άδεια, βάλε τα default
        for model, stats in DEFAULT_DATA.items():
            c.execute("INSERT INTO inventory VALUES (?, ?)", (model, json.dumps(stats)))
        conn.commit()
        return DEFAULT_DATA
    
    current_data = {}
    for row in rows:
        current_data[row[0]] = json.loads(row[1])
        
    # Έλεγχος για τυχόν νέα μοντέλα που προσθέσαμε στον κώδικα
    for model in DEFAULT_DATA:
        if model not in current_data:
            current_data[model] = DEFAULT_DATA[model]
            c.execute("INSERT INTO inventory VALUES (?, ?)", (model, json.dumps(DEFAULT_DATA[model])))
            conn.commit()
    return current_data

def save_to_db(model, stats):
    c.execute("UPDATE inventory SET data = ? WHERE model = ?", (json.dumps(stats), model))
    conn.commit()

# Φόρτωση δεδομένων αυτόματα από τη βάση
inventory = load_from_db()

# Εμφάνιση των προϊόντων
for model in DEFAULT_DATA.keys():
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
                    
                    save_to_db(model, inventory[model])
                    st.success("Το Restock αποθηκεύτηκε αυτόματα στη βάση!")
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
                    
                    save_to_db(model, inventory[model])
                    st.success("Η πώληση αποθηκεύτηκε αυτόματα στη βάση!")
                    st.rerun()
                else:
                    st.error("❌ Δεν έχεις τόσο στοκ στην αποθήκη!")
        st.markdown("---")
