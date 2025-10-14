import streamlit as st
import json
import os

# -------- Streamlit Seiteneinstellungen --------
st.set_page_config(page_title="Familien Einkaufsliste", page_icon="🛒")

# -------- Passwortschutz --------
PASSWORD = "geheim123"  # <-- dein Passwort hier

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------- Login-Ansicht --------
if not st.session_state.logged_in:
    st.title("🛒 Familien Einkaufsliste")
    user_password = st.text_input("Passwort eingeben", type="password")
    if st.button("Login"):
        if user_password == PASSWORD:
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Falsches Passwort!")

# -------- Hauptseite nach Login --------
else:
    st.title("🛒 Familien Einkaufsliste")
    st.success("Willkommen! ✅")
    st.caption("Tipp: Diese App läuft komplett lokal – keine Cloud nötig!")

    DATA_FILE = "einkaufsliste.json"

    # -------- JSON-Datei laden --------
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # -------- Neues Produkt hinzufügen --------
    with st.form("add_item", clear_on_submit=True):
        produkt = st.text_input("Produktname")
        menge = st.text_input("Menge (z.B. 1 Stück, 500 g)", "1")
        symbol = st.selectbox("Symbol", ["🥦", "🍞", "🥛", "🍫", "🍅", "🧻", "🧴", "🍎]()
