import streamlit as st
import json
import os

st.set_page_config(page_title="Familien Einkaufsliste", page_icon="🛒")

DATA_FILE = "einkaufsliste.json"

# Daten laden oder neue Liste erstellen
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []
else:
    data = []

st.title("🛒 Familien Einkaufsliste")

# Neues Produkt hinzufügen
with st.form("add_item", clear_on_submit=True):
    produkt = st.text_input("Produktname")
    menge = st.text_input("Menge (z.B. 1 Stück, 500 g)", "1")
    symbol = st.selectbox("Symbol", ["🥦","🍞","🥛","🍫","🍅","🧻","🧴","🍎","⚙️"])
    laden = st.selectbox("Einkaufsstätte", ["Rewe","Aldi","Lidl","DM","Edeka","Sonstiges"])
    submitted = st.form_submit_button("Hinzufügen")

    if submitted and produkt.strip():
        data.append({
            "Produkt": produkt.strip(),
            "Menge": menge.strip(),
            "Symbol": symbol,
            "Einkaufsstätte": laden,
            "Erledigt": False
        })
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        st.success(f"{symbol} {produkt} wurde hinzugefügt!")

st.subheader("🧾 Einkaufsliste")

if not data:
    st.info("Die Liste ist noch leer. Füge etwas hinzu!")
else:
    for i, item in enumerate(data):
        cols = st.columns([4,2,1])
        erledigt = cols[0].checkbox(
            f"{item['Symbol']} {item['Produkt']} — {item['Menge']}",
            value=item["Erledigt"],
            key=f"chk{i}"
        )
        cols[1].write(item["Einkaufsstätte"])
        if cols[2].button("❌", key=f"del{i}"):
            data.pop(i)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            st.experimental_rerun()
        item["Erledigt"] = erledigt

st.markdown("---")
st.caption("Tipp: Diese App läuft komplett lokal – keine Cloud nötig!")import streamlit as st

# -------- Passwortschutz --------
PASSWORD = "geheim123"  # <-- hier dein Passwort

st.title("🛒 Familien Einkaufsliste")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    user_password = st.text_input("Passwort eingeben", type="password")
    if st.button("Login"):
        if user_password == PASSWORD:
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Falsches Passwort!")
else:
    st.success("Willkommen! ✅")
    # Hier kommt dein bisheriger App-Code
    st.write("Hier ist deine Einkaufsliste ...")

