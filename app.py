import streamlit as st
import json
import os
from datetime import datetime

# ============================================
# Seiteneinstellungen
# ============================================
st.set_page_config(page_title="Familien Einkaufsliste", page_icon="🛒")

# ============================================
# Hilfsfunktion für sicheres Rerun
# ============================================
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# ============================================
# PDF Import optional
# ============================================
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ModuleNotFoundError:
    PDF_AVAILABLE = False

def export_pdf(data, filename="Einkaufsliste.pdf"):
    if not PDF_AVAILABLE:
        st.warning("PDF-Export nicht verfügbar. Installiere fpdf, um diese Funktion zu nutzen.")
        return
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Familien Einkaufsliste", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    for item in data:
        status = "✅" if item["Erledigt"] else "❌"
        pdf.cell(0, 8, f"{status} {item['Symbol']} {item['Produkt']} — {item['Menge']} ({item['Einkaufsstätte']})", ln=True)
    pdf.output(filename)
    st.success(f"PDF exportiert als '{filename}'")

# ============================================
# Passwortschutz
# ============================================
PASSWORD = "geheim123"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login_form"):
        pw = st.text_input("🔑 Passwort eingeben", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if pw == PASSWORD:
                st.session_state.logged_in = True
                safe_rerun()
            else:
                st.error("❌ Falsches Passwort! Bitte erneut versuchen.")
    st.stop()

# ============================================
# Hauptseite
# ============================================
st.title("🛒 Familien Einkaufsliste")
st.success("Willkommen! ✅")
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    safe_rerun()

DATA_FILE = "einkaufsliste.json"
ARCHIVE_FOLDER = "archive"
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

# JSON laden
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            data = []
else:
    data = []

# Neues Produkt hinzufügen
with st.form("add_item", clear_on_submit=True):
    produkt = st.text_input("Produktname")
    menge = st.text_input("Menge (z.B. 1 Stück, 500 g)", "1")
    symbol = st.selectbox("Symbol", ["🥦","🍞","🥛","🍫","🍅","🧻","🧴","🍎","⚙️"])
    laden = st.selectbox("Einkaufsstätte", ["Rewe","Aldi","Lidl","DM","Edeka","Kaufland","Sonstiges"])
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

# Alles markieren / Alles erledigen
st.subheader("🧾 Einkaufsliste")
all_done = st.checkbox("Alles markieren / Alles erledigen")
if all_done:
    for item in data:
        item["Erledigt"] = True

# Buttons Alles löschen / Alles abhaken
c1, c2 = st.columns(2)
if c1.button("🗑️ Alles löschen"):
    if st.confirm("Willst du wirklich alles löschen?"):
        data = []
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        st.success("✅ Alle Artikel gelöscht!")
        safe_rerun()
if c2.button("✅ Alles abhaken"):
    for item in data:
        item["Erledigt"] = True
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.success("✅ Alle Artikel als erledigt markiert!")

# Einkaufsliste anzeigen
if not data:
    st.info("Die Liste ist noch leer. Füge etwas hinzu!")
else:
    for i, item in enumerate(data):
        cols = st.columns([4,2,1])
        erledigt = cols[0].checkbox(f"{item['Symbol']} {item['Produkt']} — {item['Menge']}",
                                    value=item.get("Erledigt", False), key=f"chk{i}")
        cols[1].write(item["Einkaufsstätte"])
        if cols[2].button("❌", key=f"del{i}"):
            st.session_state["to_delete"] = {"index": i, "produkt": item["Produkt"], "symbol": item["Symbol"]}
        item["Erledigt"] = erledigt

# Löschbestätigung
if "to_delete" in st.session_state:
    td = st.session_state["to_delete"]
    st.warning(f"Soll **{td['symbol']} {td['produkt']}** wirklich gelöscht werden?")
    c1,c2 = st.columns(2)
    if c1.button("✅ Ja, löschen"):
        idx = td["index"]
        if 0 <= idx < len(data):
            data.pop(idx)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        del st.session_state["to_delete"]
        st.success("Artikel gelöscht ✅")
        safe_rerun()
    if c2.button("❌ Abbrechen"):
        del st.session_state["to_delete"]
        st.info("Löschen abgebrochen.")

# Archivierung
if st.button("💾 Einkaufsliste speichern (Archiv)"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_file = os.path.join(ARCHIVE_FOLDER, f"{timestamp}.json")
    with open(archive_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.success(f"✅ Einkaufsliste archiviert: {timestamp}")

# Archivierte Listen anzeigen
st.subheader("🗂️ Frühere Einkäufe")
archived_files = sorted(os.listdir(ARCHIVE_FOLDER), reverse=True)
for file in archived_files:
    if file.endswith(".json"):
        st.markdown(f"- [{file}]({os.path.join(ARCHIVE_FOLDER, file)})")

# PDF Export (optional)
if PDF_AVAILABLE:
    if st.button("📄 PDF exportieren"):
        export_pdf(data)
else:
    st.info("📄 PDF-Export nicht verfügbar. Installiere fpdf, wenn genügend Speicher vorhanden ist.")

# Automatisches Speichern
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

st.markdown("---")
