import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Ρύθμιση της σελίδας για να φαίνεται τέλεια στο κινητό
st.set_page_config(page_title="My Resell WMS", page_icon="📦", layout="centered")
st.title("📦 My Resell WMS")

# Σύνδεση με το Google Sheet σου (το link σου είναι ήδη ενσωματωμένο)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1sHsvJ4Lac5MuKV221QDpbJ-GfjRBNVh85C6jnCQtQbE/edit?usp=drivesdk"

try:
    # Δημιουργία σύνδεσης με το Sheet
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Διάβασμα των δεδομένων από την καρτέλα "Stock"
    df = conn.read(spreadsheet=SHEET_URL, worksheet="Stock")
except Exception as e:
    st.error("⚠️ Πρόβλημα σύνδεσης με το Google Sheet. Βεβαιώσου ότι το έχεις κάνει 'Οποιοσδήποτε με τον σύνδεσμο -> Συντάκτης' (Editor).")
    st.stop()

# Έλεγχος αν ο πίνακας έχει δεδομένα
if not df.empty:
    # Μετατροπή των στηλών σε σωστούς τύπους δεδομένων για να μην γίνονται λάθη στα μαθηματικά
    df['Total Stock'] = df['Total Stock'].astype(int)
    df['Stock'] = df['Stock'].astype(int)
    df['Sold'] = df['Sold'].astype(int)
    df['Total Cost'] = df['Total Cost'].astype(float)
    df['Sold Profit'] = df['Sold Profit'].astype(float)

    # Επανάληψη για κάθε σειρά (μοντέλο) του πίνακα
    for index, row in df.iterrows():
        model = row['Iphone Model']
        total_stock = row['Total Stock']
        stock = row['Stock']
        sold = row['Sold']
        total_cost = row['Total Cost']
        sold_profit = row['Sold Profit']
        
        # Υπολογισμός Καθαρού Κέρδους (Έσοδα - Κόστος)
        net_profit = sold_profit - total_cost
        
        # Δημιουργία μιας όμορφης "κάρτας" για κάθε iPhone
        with st.container():
            st.markdown(f"### 📱 {model}")
            
            # Πρώτη σειρά στατιστικών
            col1, col2 = st.columns(2)
            col1.metric("Στοκ Αποθήκης", stock)
            col2.metric("Θέλουν Restock (Sold)", sold)
            
            # Δεύτερη σειρά στατιστικών
            col3, col4 = st.columns(2)
            col3.metric("Συνολικά Αγορασμένα", total_stock)
            
            # Το κέρδος γίνεται πράσινο αν είναι θετικό, κόκκινο αν είναι αρνητικό
            if net_profit >= 0:
                col4.metric("Καθαρό Κέρδος", f"{net_profit:.2f}€")
            else:
                col4.metric("Καθαρό Κέρδος", f"{net_profit:.2f}€")
            
            # Επιλογή ενέργειας με κουμπιά επιλογής (Radio)
            action = st.radio(
                f"Ενέργεια για {model}", 
                ["🏠 Αναμονή", "💰 Καταγραφή Πώλησης", "🔄 Restock (Αγορά)"], 
                key=f"action_{model}"
            )
            
            # Λειτουργία 1: Καταγραφή Πώλησης
            if action == "💰 Καταγραφή Πώλησης":
                price = st.number_input("Τιμή Πώλησης στο Vinted/Vendora (€)", min_value=0.0, step=0.5, key=f"price_{model}")
                if st.button("Επιβεβαίωση Πώλησης", key=f"btn_sell_{model}"):
                    if stock > 0:
                        # Αλλαγή των τιμών στον πίνακα
                        df.at[index, 'Stock'] = stock - 1
                        df.at[index, 'Sold'] = sold + 1
                        df.at[index, 'Sold Profit'] = sold_profit + price
                        
                        # Αποθήκευση live πίσω στο Google Sheet
                        conn.update(spreadsheet=SHEET_URL, worksheet="Stock", data=df)
                        st.success(f"🎉 Η πώληση καταγράφηκε! Το στοκ για το {model} μειώθηκε.")
                        st.rerun()
                    else:
                        st.error("❌ Δεν έχεις στοκ στην αποθήκη για αυτό το μοντέλο!")
                        
            # Λειτουργία 2: Restock (Αυτόματη Πρόσθεση)
            elif action == "🔄 Restock (Αγορά)":
                qty = st.number_input("Πόσα νέα κομμάτια αγόρασες;", min_value=1, step=1, key=f"qty_{model}")
                cost = st.number_input("Συνολικό Κόστος Νέας Αγοράς (€)", min_value=0.0, step=0.5, key=f"cost_{model}")
                if st.button("Επιβεβαίωση Restock", key=f"btn_res_{model}"):
                    
                    # ΕΔΩ ΓΙΝΕΤΑΙ Η ΑΥΤΟΜΑΤΗ ΠΡΟΣΘΕΣΗ ΠΟΥ ΖΗΤΗΣΕΣ
                    df.at[index, 'Total Stock'] = total_stock + qty  # Προσθέτει τα νέα στα συνολικά
                    df.at[index, 'Stock'] = stock + qty              # Αυξάνει το τρέχον στοκ
                    df.at[index, 'Total Cost'] = total_cost + cost    # Προσθέτει το νέο έξοδο στο συνολικό κόστος
                    
                    # Αποθήκευση live πίσω στο Google Sheet
                    conn.update(spreadsheet=SHEET_URL, worksheet="Stock", data=df)
                    st.success(f"🔄 Το Restock πέτυχε! Το στοκ ενημερώθηκε αυτόματα.")
                    st.rerun()
                    
            st.markdown("---")
else:
    st.warning("Η καρτέλα 'Stock' στο Google Sheet είναι άδεια. Πρόσθεσε τα μοντέλα σου στην πρώτη στήλη!")
