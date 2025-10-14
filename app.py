import streamlit as st
import json
import os

# ===============================
# Seiteneinstellungen
# ===============================
st.set_page_config(page_title="Familien Einkaufsliste", page_icon="🛒")

# ===============================
# Passwortschutz
# ===============================
PASSWORD = "geheim123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛒 Familien Einkaufsliste")
    pw = st.text_input("🔑 Passwort eingeben", type="password")
    if st.button("Login"):
        if pw == PASSWORD:
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("❌ Falsches Passwort! Bitte erneut versuchen.")
    st.stop()

# ===============================
# Nach erfolgreichem Login
# ===============================
st.title("🛒 Familien Einkaufsliste")
st.success("Willkommen! ✅")
st.caption("Tipp: Diese App läuft komplett lokal – keine Cloud nötig!")

DATA_FILE = "einkaufsliste.json"

# ===============================
# Daten laden
# ===============================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            data = []
else:
    data = []

# ===============================
# Neues Produkt hinzufügen
# ===============================
with st.form("add_item", clear_on_submit=True):
    produkt = st.text_input("Produktname")
    menge = st.text_input("Menge (z.B. 1 Stück, 500 g)", "1")
    symbol = st.selectbox("Symbol", ["🥦", "🍞", "🥛", "🍫", "🍅", "🧻", "🧴", "🍎", "⚙️"])
    laden = st.selectbox("Einkaufsstätte", ["Rewe", "Aldi", "Lidl", "DM", "Edeka", "Kaufland", "Sonstiges"])
    submitted = st.form_submit_button("Hinzufügen")

    if submitted and produkt.strip():
        neues_item = {
            "Produkt": produkt.strip(),
            "Menge": menge.strip(),
            "Symbol": symbol,
            "Einkaufsstätte": laden,
            "Erledigt": False
        }
        data.append(neues_item)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        st.success(f"{symbol} {produkt} wurde hinzugefügt!")

# ===============================
# Einkaufsliste anzeigen
# ===============================
st.subheader("🧾 Einkaufsliste")

if not data:
    st.info("Die Liste ist noch leer. Füge etwas hinzu!")
else:
    for i, item in enumerate(data):
        cols = st.columns([4, 2, 1])
        erledigt = cols[0].checkbox(
            f"{item['Symbol']} {item['Produkt']} — {item['Menge']}",
            value=item.get("Erledigt", False),
            key=f"chk{i}"
        )
        cols[1].write(item["Einkaufsstätte"])

        # Klick auf ❌ löst Löschdialog aus
        if cols[2].button("❌", key=f"del{i}"):
            st.session_state["to_delete"] = {"index": i, "produkt": item["Produkt"], "symbol": item["Symbol"]}

        item["Erledigt"] = erledigt

# ===============================
# Bestätigung für Löschen
# ===============================
if "to_delete" in st.session_state:
    td = st.session_state["to_delete"]
    st.markdown("---")
    st.warning(f"Soll **{td['symbol']} {td['produkt']}** wirklich gelöscht werden?")
    c1, c2 = st.columns(2)

    if c1.button("✅ Ja, löschen"):
        idx = td["index"]
        if 0 <= idx < len(data):
            data.pop(idx)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        del st.session_state["to_delete"]
        st.success("Artikel gelöscht ✅")
        st.experimental_rerun()

    if c2.button("❌ Abbrechen"):
        del st.session_state["to_delete"]
        st.info("Löschen abgebrochen.")

# ===============================
# Liste speichern (Status)
# ===============================
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

st.markdown("---")
