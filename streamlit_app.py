import streamlit as st
import pandas as pd
import requests

# Ρύθμιση σελίδας για τέλεια εμφάνιση στο κινητό
st.set_page_config(page_title="AuraNovaTD WMS", page_icon="📦", layout="centered")
st.title("📦 AuraNovaTD WMS")

# 1. Το Link από το Google Sheet σου για διάβασμα των τρεχουσών τιμών
SHEET_URL = "https://docs.google.com/spreadsheets/d/1sHsvJ4Lac5MuKV221QDpbJ-GfjRBNVh85C6jnCQtQbE/edit?usp=drivesdk"
CSV_URL = SHEET_URL.replace("/edit?usp=drivesdk", "/gviz/tq?tqx=out:csv&sheet=Stock")

# 2. Το Link της Google Φόρμας σου για αυτόματη εγγραφή
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc9tUrfzkKLAlArm9RYcP2bUi8mgw1OwUg95sUJes2kv9fYdQ/formResponse"

@st.cache_data(ttl=3)  # Γρήγορη ανανέωση κάθε 3 δευτερόλεπτα
def load_data():
    return pd.read_csv(CSV_URL)

try:
    df = load_data()
except Exception as e:
    st.error("⚠️ Πρόβλημα σύνδεσης με το Google Sheet.")
    st.stop()

if not df.empty:
    df.columns = df.columns.str.strip()
    
    for index, row in df.iterrows():
        model = row['Iphone Model']
        stock = int(row['Stock'])
        sold = int(row['Sold'])
        total_stock = int(row['Total Stock'])
        total_cost = float(row['Total Cost'])
        sold_profit = float(row['Sold Profit'])
        net_profit = sold_profit - total_cost
        
        with st.container():
            st.markdown(f"### 📱 {model}")
            
            # Στατιστικά στην οθόνη
            col1, col2 = st.columns(2)
            col1.metric("Στοκ Αποθήκης", stock)
            col2.metric("Θέλουν Restock (Sold)", sold)
            
            col3, col4 = st.columns(2)
            col3.metric("Συνολικά Αγορασμένα", total_stock)
            col4.metric("Καθαρό Κέρδος", f"{net_profit:.2f}€")
            
            # Επιλογή Ενέργειας
            action = st.radio(f"Ενέργεια για {model}", ["Αναμονή", "🔄 Restock (Αγορά)", "💰 Καταγραφή Πώλησης"], key=f"act_{model}")
            
            # ΛΕΙΤΟΥΡΓΙΑ 1: ΑΥΤΟΜΑΤΟ RESTOCK
            if action == "🔄 Restock (Αγορά)":
                qty = st.number_input("Πόσα κομμάτια αγόρασες;", min_value=1, step=1, key=f"q_{model}")
                cost = st.number_input("Συνολικό Κόστος Νέας Αγοράς (€)", min_value=0.0, step=0.5, key=f"c_{model}")
                
                if st.button("🚀 Επιβεβαίωση Restock", key=f"b_r_{model}"):
                    # Τα κρυφά IDs των ερωτήσεών σου από τον κώδικα της φόρμας
                    form_data = {
                        'entry.1147572793': model,       # Ερώτηση: Model
                        'entry.2127271810': 'Restock',     # Ερώτηση: Type (Multiple Choice)
                        'entry.2064099496': qty,           # Ερώτηση: Qty
                        'entry.174246835': cost            # Ερώτηση: Amount
                    }
                    # Αποστολή live στο Google Sheet μέσω της φόρμας
                    requests.post(FORM_URL, data=form_data)
                    st.success(f"🔄 Το Restock για το {model} καταγράφηκε αυτόματα!")
                    st.toast("Γίνεται ανανέωση δεδομένων...")
                    st.rerun()
                    
            # ΛΕΙΤΟΥΡΓΙΑ 2: ΑΥΤΟΜΑΤΗ ΠΩΛΗΣΗ
            elif action == "💰 Καταγραφή Πώλησης":
                price = st.number_input("Τιμή Πώλησης στο Vinted (€)", min_value=0.0, step=0.5, key=f"p_{model}")
                
                if st.button("🚀 Επιβεβαίωση Πώλησης", key=f"b_s_{model}"):
                    if stock > 0:
                        form_data = {
                            'entry.1147572793': model,
                            'entry.2127271810': 'Πώληση',   # Ερώτηση: Type (Multiple Choice)
                            'entry.2064099496': 1,           # Μειώνει κατά 1 κομμάτι την αποθήκη
                            'entry.174246835': price         # Ερώτηση: Amount
                        }
                        # Αποστολή live στο Google Sheet μέσω της φόρμας
                        requests.post(FORM_URL, data=form_data)
                        st.success(f"🎉 Η πώληση για το {model} καταγράφηκε αυτόματα!")
                        st.toast("Γίνεται ανανέωση δεδομένων...")
                        st.rerun()
                    else:
                        st.error("❌ Δεν έχεις στοκ στην αποθήκη για αυτό το μοντέλο!")
                        
            st.markdown("---")
