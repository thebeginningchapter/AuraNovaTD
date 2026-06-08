import streamlit as st
import json

# Ρύθμιση σελίδας για το κινητό
st.set_page_config(page_title="AuraNovaTD WMS", page_icon="📦", layout="centered")
st.title("📦 AuraNovaTD WMS")

# Η λίστα μοντέλων του AuraNovaTD
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

# Φόρτωση δεδομένων από τα ασφαλή Secrets του Streamlit Cloud
if "saved_data" in st.secrets:
    try:
        initial_data = json.loads(st.secrets["saved_data"])
        # Συγχρονισμός αν λείπει κάποιο μοντέλο
        for model in DEFAULT_DATA:
            if model not in initial_data:
                initial_data[model] = DEFAULT_DATA[model]
    except:
        initial_data = DEFAULT_DATA
else:
    initial_data = DEFAULT_DATA

if "wms_data" not in st.session_state:
    st.session_state.wms_data = initial_data

inventory = st.session_state.wms_data

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
                    st.session_state.wms_data = inventory
                    st.success("Καταγράφηκε στη μνήμη! Θυμήσου να πατήσεις 'Οριστική Αποθήκευση' στο κάτω μέρος.")
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
                    st.success("Καταγράφηκε στη μνήμη! Θυμήσου να πατήσεις 'Οριστική Αποθήκευση' στο κάτω μέρος.")
                    st.rerun()
                else:
                    st.error("❌ Δεν έχεις τόσο στοκ στην αποθήκη!")
        st.markdown("---")

# 💾 ΚΟΥΜΠΙ ΜΟΝΙΜΗΣ ΑΠΟΘΗΚΕΥΣΗΣ ΣΤΟ ΚΑΤΩ ΜΕΡΟΣ
st.write("### 🔒 Ασφάλεια Δεδομένων AuraNovaTD")
json_string = json.dumps(inventory, ensure_ascii=False)
st.info("Για να μην χαθούν τα δεδομένα στο επόμενο reboot, αντέγραψε το παρακάτω κείμενο και βάλτο στα Secrets του Streamlit Cloud:")
st.code(f'saved_data = {repr(json_string)}')
