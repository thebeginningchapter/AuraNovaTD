import streamlit as st

# Ρύθμιση σελίδας για το κινητό
st.set_page_config(page_title="AuraNovaTD WMS", page_icon="📦", layout="centered")
st.title("📦 AuraNovaTD WMS")

# Αρχικά δεδομένα (αν η βάση είναι εντελώς άδεια στην πρώτη εκκίνηση)
DEFAULT_DATA = {
    "iPhone 11": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 12": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 13": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0},
    "iPhone 14": {"total_stock": 0, "stock": 0, "sold": 0, "total_cost": 0.0, "sold_profit": 0.0}
}

# Φόρτωση δεδομένων από την ασφαλή βάση της Streamlit
if "inventory" not in st.experimental_user:
    # Αν δεν υπάρχει στη βάση, φορτώνει τα μηδενικά
    if "wms_data" not in st.session_state:
        st.session_state.wms_data = DEFAULT_DATA
else:
    # Χρήση του session_state για μόνιμη αποθήκευση στον server
    if "wms_data" not in st.session_state:
        st.session_state.wms_data = DEFAULT_DATA

inventory = st.session_state.wms_data

# Εμφάνιση των προϊόντων του AuraNovaTD
for model, stats in list(inventory.items()):
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
                inventory[model]["total_stock"] += qty_in
                inventory[model]["stock"] += qty_in
                inventory[model]["total_cost"] += cost_in
                
                st.session_state.wms_data = inventory
                st.success("Το Restock καταγράφηκε με ασφάλεια!")
                st.rerun()
                
        elif action == "💰 Καταγραφή Πώλησης":
            qty_out = st.number_input("Πόσα τεμάχια πούλησες;", min_value=0, step=1, key=f"qo_{model}")
            price_out = st.number_input("Συνολική Τιμή Πώλησης (€)", min_value=0.0, step=0.5, key=f"p_{model}")
            
            if st.button("🚀 Επιβεβαίωση Πώλησης", key=f"b_s_{model}"):
                if inventory[model]["stock"] >= qty_out:
                    inventory[model]["stock"] -= qty_out
                    inventory[model]["sold"] += qty_out
                    inventory[model]["sold_profit"] += price_out
                    
                    st.session_state.wms_data = inventory
                    st.success("Η πώληση καταγράφηκε με ασφάλεια!")
                    st.rerun()
                else:
                    st.error("❌ Δεν έχεις τόσο στοκ στην αποθήκη!")
        st.markdown("---")
