import streamlit as st
import pandas as pd

# Ρύθμιση σελίδας
st.set_page_config(page_title="AuraNovaTD WMS", page_icon="📦", layout="centered")
st.title("📦 My Resell WMS")

# Το δικό σου Google Sheet Link
SHEET_URL = "https://docs.google.com/spreadsheets/d/1sHsvJ4Lac5MuKV221QDpbJ-GfjRBNVh85C6jnCQtQbE/edit?usp=drivesdk"

# Μετατροπή του link σε μορφή που η Python διαβάζει απευθείας σαν πίνακα
CSV_URL = SHEET_URL.replace("/edit?usp=drivesdk", "/gviz/tq?tqx=out:csv&sheet=Stock")

@st.cache_data(ttl=10)  # Ανανέωση δεδομένων κάθε 10 δευτερόλεπτα
def load_data():
    return pd.read_csv(CSV_URL)

try:
    df = load_data()
except Exception as e:
    st.error("⚠️ Πρόβλημα με την ανάγνωση του Google Sheet. Βεβαιώσου ότι η κοινοποίηση είναι 'Οποιοσδήποτε με τον σύνδεσμο'.")
    st.stop()

if not df.empty:
    # Καθαρισμός δεδομένων
    df.columns = df.columns.str.strip()
    
    for index, row in df.iterrows():
        model = row['Iphone Model']
        stock = int(row['Stock'])
        sold = int(row['Sold'])
        total_stock = int(row['Total Stock'])
        net_profit = float(row['Sold Profit']) - float(row['Total Cost'])
        
        with st.container():
            st.markdown(f"### 📱 {model}")
            
            col1, col2 = st.columns(2)
            col1.metric("Στοκ Αποθήκης", stock)
            col2.metric("Θέλουν Restock (Sold)", sold)
            
            col3, col4 = st.columns(2)
            col3.metric("Συνολικά Αγορασμένα", total_stock)
            col4.metric("Καθαρό Κέρδος", f"{net_profit:.2f}€")
            
            # Επειδή το γράψιμο στο Google Sheets απαιτεί κλειδιά ασφαλείας,
            # εδώ σου βγάζει έτοιμο τον οδηγό για το τι πρέπει να γράψεις στο Sheet
            # ώστε να μην κάνεις ποτέ λάθος στις προσθέσεις!
            action = st.selectbox(f"⚙️ Υπολογιστής για {model}", ["Επιλογή ενέργειας...", "🔄 Θέλω να κάνω Restock", "💰 Έκανα Πώληση"], key=f"select_{model}")
            
            if action == "🔄 Θέλω να κάνω Restock":
                qty = st.number_input("Πόσα κομμάτια αγόρασες;", min_value=1, step=1, key=f"q_{model}")
                cost = st.number_input("Συνολικό Κόστος (€)", min_value=0.0, step=0.5, key=f"c_{model}")
                if st.button("Υπολόγισε νέες τιμές", key=f"b1_{model}"):
                    st.info(f"📊 **Γράψε αυτά στο Google Sheet σου:**\n"
                            f"* Το **Total Stock** να γίνει: `{total_stock + qty}`\n"
                            f"* Το **Stock** να γίνει: `{stock + qty}`\n"
                            f"* Το **Total Cost** να γίνει: `{row['Total Cost'] + cost}`")
            
            elif action == "💰 Έκανα Πώληση":
                price = st.number_input("Τιμή Πώλησης (€)", min_value=0.0, step=0.5, key=f"p_{model}")
                if st.button("Υπολόγισε νέες τιμές", key=f"b2_{model}"):
                    if stock > 0:
                        st.info(f"📊 **Γράψε αυτά στο Google Sheet σου:**\n"
                                f"* Το **Stock** να γίνει: `{stock - 1}`\n"
                                f"* Το **Sold** να γίνει: `{sold + 1}`\n"
                                f"* Το **Sold Profit** να γίνει: `{row['Sold Profit'] + price}`")
                    else:
                        st.error("Δεν έχεις στοκ!")
            st.markdown("---")
