import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="My Resell WMS", page_icon="📦", layout="centered")
st.title("📦 My Resell WMS (Direct)")

# Σύνδεση με το Google Sheet (ανοιχτή πρόσβαση)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1sHsvJ4Lac5MuKV221QDpbJ-GfjRBNVh85C6jnCQtQbE/edit?usp=drivesdk"
CSV_URL = SHEET_URL.replace("/edit?usp=drivesdk", "/gviz/tq?tqx=out:csv&sheet=Stock")

def load_data():
    return pd.read_csv(CSV_URL)

try:
    df = load_data()
except:
    st.error("Πρόβλημα σύνδεσης με το Sheet.")
    st.stop()

# Σύνδεση για εγγραφή μέσω gspread (χρησιμοποιεί την ανοιχτή κοινοποίηση που έκανες)
try:
    gc = gspread.public_link(SHEET_URL)
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.worksheet("Stock")
except:
    pass

if not df.empty:
    df.columns = df.columns.str.strip()
    
    for index, row in df.iterrows():
        model = row['Iphone Model']
        total_stock = int(row['Total Stock'])
        stock = int(row['Stock'])
        sold = int(row['Sold'])
        total_cost = float(row['Total Cost'])
        sold_profit = float(row['Sold Profit'])
        net_profit = sold_profit - total_cost
        
        # Η γραμμή στο Google Sheets (το index ξεκινάει από το 0, οι τίτλοι είναι στη γραμμή 1, άρα τα δεδομένα στη γραμμή index + 2)
        sheet_row = index + 2
        
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
                qty = st.number_input("Πόσα κομμάτια αγόρασες;", min_value=1, step=1, key=f"q_{model}")
                cost = st.number_input("Συνολικό Κόστος Νέας Αγοράς (€)", min_value=0.0, step=0.5, key=f"c_{model}")
                
                if st.button("🚀 Επιβεβαίωση Restock", key=f"b_r_{model}"):
                    try:
                        # Ενημέρωση απευθείας στα κελιά του Google Sheet
                        worksheet.update_cell(sheet_row, 2, total_stock + qty) # Total Stock (Στήλη B)
                        worksheet.update_cell(sheet_row, 3, stock + qty)       # Stock (Στήλη C)
                        worksheet.update_cell(sheet_row, 5, total_cost + cost)   # Total Cost (Στήλη E)
                        st.success("Το Restock καταγράφηκε!")
                        st.rerun()
                    except:
                        st.error("Δεν δόθηκε πρόσβαση. Βεβαιώσου ότι το Sheet είναι 'Συντάκτης' για όλους.")
                    
            elif action == "💰 Καταγραφή Πώλησης":
                # ΤΩΡΑ ΖΗΤΑΕΙ ΚΑΙ ΤΕΜΑΧΙΑ ΚΑΙ ΤΙΜΗ
                qty_sold = st.number_input("Πόσα τεμάχια πούλησες;", min_value=1, max_value=stock if stock > 0 else 1, step=1, key=f"qs_{model}")
                price = st.number_input("Συνολική Τιμή Πώλησης (€)", min_value=0.0, step=0.5, key=f"p_{model}")
                
                if st.button("🚀 Επιβεβαίωση Πώλησης", key=f"b_s_{model}"):
                    if stock >= qty_sold:
                        try:
                            # Ενημέρωση απευθείας στα κελιά του Google Sheet
                            worksheet.update_cell(sheet_row, 3, stock - qty_sold)     # Stock (Στήλη C)
                            worksheet.update_cell(sheet_row, 4, sold + qty_sold)       # Sold (Στήλη D)
                            worksheet.update_cell(sheet_row, 6, sold_profit + price)   # Sold Profit (Στήλη F)
                            st.success("Η πώληση καταγράφηκε!")
                            st.rerun()
                        except:
                            st.error("Δεν δόθηκε πρόσβαση. Βεβαιώσου ότι το Sheet είναι 'Συντάκτης' για όλους.")
                    else:
                        st.error("❌ Δεν έχεις τόσο στοκ στην αποθήκη!")
            st.markdown("---")
