import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="My Resell WMS", page_icon="📦", layout="centered")
st.title("📦 My Resell WMS (Αυτόματο)")

# 1. Το Link από το Google Sheet σου για διάβασμα
SHEET_URL = "https://docs.google.com/spreadsheets/d/1sHsvJ4Lac5MuKV221QDpbJ-GfjRBNVh85C6jnCQtQbE/edit?usp=drivesdk"
CSV_URL = SHEET_URL.replace("/edit?usp=drivesdk", "/gviz/tq?tqx=out:csv&sheet=Stock")

# 2. ΕΔΩ ΒΑΖΕΙΣ ΤΟ LINK ΤΗΣ ΦΟΡΜΑΣ ΣΟΥ (Θα σου δείξω στο Βήμα 3 πώς θα το βρεις)
FORM_URL = "https://docs.google.com/forms/d/e/XXXXXXXXXXXXX/formResponse"

@st.cache_data(ttl=5)
def load_data():
    return pd.read_csv(CSV_URL)

try:
    df = load_data()
except:
    st.error("Πρόβλημα σύνδεσης.")
    st.stop()

if not df.empty:
    df.columns = df.columns.str.strip()
    
    for index, row in df.iterrows():
        model = row['Iphone Model']
        stock = int(row['Stock'])
        sold = int(row['Sold'])
        
        with st.container():
            st.markdown(f"### 📱 {model}")
            col1, col2 = st.columns(2)
            col1.metric("Στοκ Αποθήκης", stock)
            col2.metric("Πουλήθηκαν", sold)
            
            action = st.radio(f"Ενέργεια για {model}", ["Αναμονή", "🔄 Restock", "💰 Πώληση"], key=f"act_{model}")
            
            if action == "🔄 Restock":
                qty = st.number_input("Πόσα κομμάτια;", min_value=1, step=1, key=f"q_{model}")
                cost = st.number_input("Συνολικό Κόστος (€)", min_value=0.0, step=0.5, key=f"c_{model}")
                
                if st.button("🚀 Επιβεβαίωση Restock", key=f"b_r_{model}"):
                    # Στέλνει τα δεδομένα αυτόματα στο Google Sheet μέσω της φόρμας
                    form_data = {
                        'entry.XXXXX_1': model,   # Θα αντικαταστήσουμε τα XXXXX με τα δικά σου
                        'entry.XXXXX_2': 'Restock',
                        'entry.XXXXX_3': qty,
                        'entry.XXXXX_4': cost
                    }
                    requests.post(FORM_URL, data=form_data)
                    st.success(f"Το Restock για το {model} καταγράφηκε αυτόματα στο Sheet!")
                    st.rerun()
                    
            elif action == "💰 Πώληση":
                price = st.number_input("Τιμή Πώλησης (€)", min_value=0.0, step=0.5, key=f"p_{model}")
                if st.button("🚀 Επιβεβαίωση Πώλησης", key=f"b_s_{model}"):
                    if stock > 0:
                        form_data = {
                            'entry.XXXXX_1': model,
                            'entry.XXXXX_2': 'Sale',
                            'entry.XXXXX_3': 1,
                            'entry.XXXXX_4': price
                        }
                        requests.post(FORM_URL, data=form_data)
                        st.success(f"Η πώληση για το {model} καταγράφηκε αυτόματα στο Sheet!")
                        st.rerun()
                    else:
                        st.error("Δεν υπάρχει στοκ!")
            st.markdown("---")
