import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="My Resell WMS", page_icon="📦", layout="centered")
st.title("📦 My Resell WMS")

# Το link της φόρμας σου για να στέλνουμε δεδομένα
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc9tUrfzkKLAlArm9RYcP2bUi8mgw1OwUg95sUJes2kv9fYdQ/formResponse"

# Το link του Sheet - Διαβάζουμε απευθείας την καρτέλα των απαντήσεων της Φόρμας!
SHEET_URL = "https://docs.google.com/spreadsheets/d/1sHsvJ4Lac5MuKV221QDpbJ-GfjRBNVh85C6jnCQtQbE/edit?usp=drivesdk"
CSV_URL = SHEET_URL.replace("/edit?usp=drivesdk", "/gviz/tq?tqx=out:csv&sheet=Απαντήσεις φόρμας 1")

@st.cache_data(ttl=2)
def load_data():
    try:
        # Διαβάζουμε το ιστορικό των κινήσεων
        df_entries = pd.read_csv(CSV_URL)
        df_entries.columns = df_entries.columns.str.strip()
        return df_entries
    except:
        return pd.DataFrame()

df_raw = load_data()

# Λίστα με τα μοντέλα σου (μπορείς να προσθέσεις όποιο θέλεις εδώ)
MODELS = ["iPhone 11", "iPhone 12", "iPhone 13", "iPhone 14"]

for model in MODELS:
    # Υπολογισμός στατιστικών live μέσα από τον κώδικα για να μην κολλάει το Excel
    total_stock = 0
    sold = 0
    total_cost = 0.0
    sold_profit = 0.0
    
    if not df_raw.empty and 'Model' in df_raw.columns:
        # Φιλτράρουμε τις κινήσεις για το συγκεκριμένο μοντέλο
        df_model = df_raw[df_raw['Model'] == model]
        
        for _, row in df_model.iterrows():
            # Έλεγχος αν οι στήλες έχουν δεδομένα
            qty = int(row['Qty']) if not pd.isna(row['Qty']) else 0
            amount = float(row['Amount']) if not pd.isna(row['Amount']) else 0.0
            type_move = str(row['Type']).strip()
            
            if type_move == 'Restock':
                total_stock += qty
                total_cost += amount
            elif type_move == 'Πώληση':
                sold += qty
                sold_profit += amount

    stock = total_stock - sold
    net_profit = sold_profit - total_cost
    
    with st.container():
        st.markdown(f"### 📱 {model}")
        
        col1, col2 = st.columns(2)
        col1.metric("Στοκ Αποθήκης", stock)
        col2.metric("Πουλήθηκαν (Sold)", sold)
        
        col3, col4 = st.columns(2)
        col3.metric("Συνολικά Αγορασμένα", total_stock)
        col4.metric("Καθαρό Κέρδος", f"{net_profit:.2f}€")
        
        action = st.radio(f"Ενέργεια για {model}", ["Αναμονή", "🔄 Restock (Αγορά)", "💰 Καταγραφή Πώλησης"], key=f"act_{model}")
        
        if action == "🔄 Restock (Αγορά)":
            qty_in = st.number_input("Πόσα κομμάτια αγόρασες;", min_value=1, step=1, key=f"q_{model}")
            cost_in = st.number_input("Συνολικό Κόστος Νέας Αγοράς (€)", min_value=0.0, step=0.5, key=f"c_{model}")
            
            if st.button("🚀 Επιβεβαίωση Restock", key=f"b_r_{model}"):
                form_data = {
                    'entry.1147572793': model,
                    'entry.2127271810': 'Restock',
                    'entry.2064099496': qty_in,
                    'entry.174246835': cost_in
                }
                requests.post(FORM_URL, data=form_data)
                st.success("Καταγράφηκε!")
                st.rerun()
                
        elif action == "💰 Καταγραφή Πώλησης":
            qty_out = st.number_input("Πόσα τεμάχια πούλησες;", min_value=1, step=1, key=f"qo_{model}")
            price_out = st.number_input("Συνολική Τιμή Πώλησης (€)", min_value=0.0, step=0.5, key=f"p_{model}")
            
            if st.button("🚀 Επιβεβαίωση Πώλησης", key=f"b_s_{model}"):
                if stock >= qty_out:
                    form_data = {
                        'entry.1147572793': model,
                        'entry.2127271810': 'Πώληση',
                        'entry.2064099496': qty_out,
                        'entry.174246835': price_out
                    }
                    requests.post(FORM_URL, data=form_data)
                    st.success("Καταγράφηκε!")
                    st.rerun()
                else:
                    st.error("❌ Δεν έχεις τόσο στοκ στην αποθήκη!")
        st.markdown("---")
