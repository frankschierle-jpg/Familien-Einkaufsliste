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
# PDF optional importieren
# ============================================
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ModuleNotFoundError:
    PDF_AVAILABLE = False

# ============================================
# Kategorien & Stichwörter
# ============================================
KATEGORIEN = {
    "🍎 Obst": ["apfel", "banane", "birne", "orange", "traube", "kiwi", "zitrone"],
    "🥦 Gemüse": ["tomate", "gurke", "salat", "karotte", "zwiebel", "paprika", "kartoffel"],
    "🥩 Fleisch": ["rind", "schwein", "hähnchen", "fleisch", "hack"],
    "🐟 Fisch": ["lachs", "thunfisch", "fisch", "forelle"],
    "🧻 Papierwaren": ["toilettenpapier", "küchenrolle", "taschentuch", "serviette"],
    "🧴 Drogerie": ["shampoo", "zahnpasta", "seife", "deo", "duschgel", "creme"],
    "🧺 Non Food": ["batterie", "kerze", "reiniger", "putzmittel", "schwamm"],
    "🧀 Käse": ["käse", "gouda", "camembert", "emmentaler"],
    "🌭 Wurst": ["wurst", "salami", "schinken", "leberwurst"],
    "🥛 Molkereiprodukte": ["milch", "joghurt", "butter", "sahne"],
    "🍫 Süßwaren": ["schokolade", "bonbon", "keks", "gummibär", "riegel"],
    "🥨 Salzgebäck": ["chips", "brezel", "cracker", "salzstange"],
    "🍯 Brotaufstrich": ["marmelade", "honig", "nutella", "aufstrich"],
    "🥐 Backwaren": ["brot", "brötchen", "croissant", "kuchen", "baguette"]
}

def erkenne_kategorie(produktname: str):
    name = produktname.lower()
    for kategorie, stichwoerter in KATEGORIEN.items():
        if any(wort in name for wort in stichwoerter):
            return kategorie
    return "⚙️ Sonstiges"

# ============================================
# PDF Export
# ============================================
def export_pdf(data, filename="Einkaufsliste.pdf"):
    if not PDF_AVAILABLE:
        st.warning("PDF-Export nicht verfügbar. Installiere fpdf, um diese Funktion zu nutzen.")
        return
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Familien Einkaufsliste", ln=True, align="C")
    pdf.set_font("Arial", "", 12)

    kategorien_sortiert = sorted(set(item["Kategorie"] for item in data))
    for kat in kategorien_sortiert:
        pdf.ln(8)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, kat, ln=True)
        pdf.set_font("Arial", "", 12)
        for item in [x for x in data if x["Kategorie"] == kat]:
            status = "✅" if item["Erledigt"] else "❌"
            pdf.cell(0, 8, f"{status} {item['Symbol']} {item['Produkt']} — {item['Menge']} ({item['Einkaufsstätte']})", ln=True)
    pdf.output(filename)
    st.success(f"📄 PDF exportiert als '{filename}'")

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

# ============================================
# Neues Produkt hinzufügen (mit Erkennung)
# ============================================
with st.form("add_item", clear_on_submit=True):
    produkt = st.text_input("Produktname (automatische Erkennung)")
    menge = st.text_input("Menge (z.B. 1 Stück, 500 g)", "1")
    symbol = st.selectbox("Symbol", ["🥦","🍞","🥛","🍫","🍅","🧻","🧴","🍎","⚙️"])
    laden = st.selectbox("Einkaufsstätte", ["Rewe","Aldi","Lidl","DM","Edeka","Kaufland","Sonstiges"])
    submitted = st.form_submit_button("Hinzufügen")
    if submitted and produkt.strip():
        kategorie = erkenne_kategorie(produkt)
        neues_item = {
            "Produkt": produkt.strip(),
            "Menge": menge.strip(),
            "Symbol": symbol,
            "Einkaufsstätte": laden,
            "Kategorie": kategorie,
            "Erledigt": False
        }
        data.append(neues_item)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        st.success(f"{symbol} {produkt} wurde unter **{kategorie}** hinzugefügt!")

# ============================================
# Einkaufsliste anzeigen
# ============================================
st.subheader("🧾 Einkaufsliste")

if not data:
    st.info("Die Liste ist noch leer. Füge etwas hinzu!")
else:
    # Checkbox oben links
    alles_markieren = st.checkbox("Alles markieren / abhaken")

    # Nach Kategorie sortieren
    kategorien_sortiert = sorted(set(item["Kategorie"] for item in data))
    for kat in kategorien_sortiert:
        st.markdown(f"### {kat}")
        for i, item in enumerate([x for x in data if x["Kategorie"] == kat]):
            idx = data.index(item)
            erledigt = st.checkbox(
                f"{item['Symbol']} {item['Produkt']} — {item['Menge']} ({item['Einkaufsstätte']})",
                value=(alles_markieren or item["Erledigt"]),
                key=f"chk{idx}"
            )
            item["Erledigt"] = erledigt

    # Buttons am Ende
    c1, c2 = st.columns(2)
    if c1.button("✅ Alles erledigt"):
        for item in data:
            item["Erledigt"] = True
        st.success("Alle Artikel als erledigt markiert.")
    if c2.button("🗑️ Alles löschen"):
        if st.confirm("Willst du wirklich alles löschen?"):
            data = []
            st.warning("Alle Artikel gelöscht!")

# ============================================
# Speichern, Archiv, PDF
# ============================================
if st.button("💾 Einkaufsliste archivieren"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_file = os.path.join(ARCHIVE_FOLDER, f"{timestamp}.json")
    with open(archive_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.success(f"✅ Einkaufsliste archiviert: {timestamp}")

st.subheader("🗂️ Frühere Einkäufe")
for file in sorted(os.listdir(ARCHIVE_FOLDER), reverse=True):
    if file.endswith(".json"):
        st.markdown(f"- [{file}]({os.path.join(ARCHIVE_FOLDER, file)})")

if PDF_AVAILABLE:
    if st.button("📄 PDF exportieren"):
        export_pdf(data)
else:
    st.info("📄 PDF-Export derzeit nicht verfügbar (fpdf nicht installiert).")

# ============================================
# Automatisches Speichern
# ============================================
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

st.markdown("---")
