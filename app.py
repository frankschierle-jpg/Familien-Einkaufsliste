import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF

# ==================================================
# Streamlit-Einstellungen
# ==================================================
st.set_page_config(page_title="Familien Einkaufsliste", page_icon="🛒")

# ==================================================
# Hilfsfunktionen
# ==================================================
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []


def export_pdf(data, filename="Einkaufsliste.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(200, 10, txt="🛒 Familien Einkaufsliste", ln=True, align="C")
    pdf.ln(10)

    if not data:
        pdf.cell(200, 10, txt="Liste ist leer.", ln=True)
    else:
        kategorien = sorted(set(item["Produktkategorie"] for item in data))
        for kat in kategorien:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(200, 10, txt=kat, ln=True)
            pdf.set_font("Helvetica", size=11)
            for item in [x for x in data if x["Produktkategorie"] == kat]:
                status = "✅" if item["Erledigt"] else "⬜"
                line = f"{status} {item['Produkt']} — {item['Menge']} ({item['Einkaufsstätte']})"
                pdf.cell(200, 8, txt=line, ln=True)
            pdf.ln(5)
    pdf.output(filename)
    return filename


# ==================================================
# Passwortschutz
# ==================================================
PASSWORD = "geheim123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛒 Familien Einkaufsliste")
    pw = st.text_input("🔑 Passwort eingeben", type="password")
    if pw == PASSWORD or st.button("Login"):
        if pw == PASSWORD:
            st.session_state.logged_in = True
            safe_rerun()
        else:
            st.error("❌ Falsches Passwort!")
    st.stop()

# ==================================================
# Hauptseite
# ==================================================
st.title("🛒 Familien Einkaufsliste")

if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    safe_rerun()

DATA_FILE = "einkaufsliste.json"
ARCHIV_DIR = "archiv"

os.makedirs(ARCHIV_DIR, exist_ok=True)

data = load_data(DATA_FILE)

# ==================================================
# Kategorisierung mit Marken + Texterkennung
# ==================================================
KATEGORIEN = {
    "🍎 Obst": [
        "Apfel", "Banane", "Birne", "Pfirsich", "Pflaume", "Kirsche", "Traube", "Erdbeere", "Himbeere",
        "Blaubeere", "Melone", "Wassermelone", "Mango", "Ananas", "Orange", "Mandarine", "Zitrone",
        "Limette", "Kiwi", "Granatapfel", "Feige", "Aprikose", "Passionsfrucht", "Avocado"
    ],
    "🥦 Gemüse": [
        "Tomate", "Gurke", "Paprika", "Zwiebel", "Knoblauch", "Kartoffel", "Karotte", "Brokkoli", "Blumenkohl",
        "Zucchini", "Aubergine", "Lauch", "Sellerie", "Radieschen", "Rote Beete", "Kohl", "Spinat", "Feldsalat"
    ],
    "🥩 Fleisch": ["Rindfleisch", "Hähnchen", "Schweinefleisch", "Hackfleisch", "Steak", "Wurst"],
    "🐟 Fisch": ["Lachs", "Forelle", "Thunfisch", "Seelachs", "Garnelen", "Kabeljau"],
    "🧀 Käse": ["Gouda", "Emmentaler", "Mozzarella", "Camembert", "Feta"],
    "🌭 Wurst": ["Salami", "Schinken", "Mortadella", "Lyoner"],
    "🥛 Molkereiprodukte": ["Milch", "Joghurt", "Sahne", "Quark", "Butter"],
    "🥨 Backwaren": ["Brot", "Brötchen", "Croissant", "Brezel", "Toast"],
    "🍓 Brotaufstrich": ["Nutella", "Honig", "Marmelade", "Erdbeermarmelade", "Konfitüre"],
    "🍫 Süßwaren": ["Schokolade", "Milka", "Kinderriegel", "Gummibärchen", "Bonbons"],
    "🍟 Salzgebäck": ["Chips", "Erdnussflips", "Salzstangen", "Cracker"],
    "🧴 Drogerie": ["Zahnpasta", "Zahnbürste", "Shampoo", "Nivea", "Seife", "Duschgel"],
    "🧻 Papierwaren": ["Toilettenpapier", "Küchenrolle", "Servietten", "Taschentücher"],
    "🧺 Non Food": ["Waschmittel", "Spülmittel", "Waschmaschine", "Batterien", "Kerzen"],
    "🥤 Getränke": ["Cola", "Coca-Cola", "Bier", "Wasser", "Saft", "Tee", "Kaffee", "Wein"],
}

def finde_kategorie(produkt):
    p = produkt.lower()
    for kat, items in KATEGORIEN.items():
        for i in items:
            if i.lower() in p:
                return kat
    return "⚙️ Sonstiges"

# ==================================================
# Neues Produkt hinzufügen
# ==================================================
with st.form("add_item", clear_on_submit=True):
    produkt = st.text_input("Produktname")
    menge = st.text_input("Menge (z. B. 1 Stück, 500 g)", "1")
    laden = st.selectbox("Einkaufsstätte", ["Rewe", "Aldi", "Lidl", "DM", "Edeka", "Kaufland", "Sonstiges"])
    submitted = st.form_submit_button("Hinzufügen")

    if submitted and produkt.strip():
        kategorie = finde_kategorie(produkt)
        neues_item = {
            "Produkt": produkt.strip(),
            "Menge": menge.strip(),
            "Produktkategorie": kategorie,
            "Einkaufsstätte": laden,
            "Erledigt": False
        }
        data.append(neues_item)
        save_data(DATA_FILE, data)
        st.success(f"{kategorie} {produkt} wurde hinzugefügt!")

# ==================================================
# Einkaufsliste anzeigen
# ==================================================
st.subheader("🧾 Einkaufsliste")

if not data:
    st.info("Die Liste ist leer. Füge etwas hinzu!")
else:
    # Checkbox: Alles markieren
    alle_markieren = st.checkbox("✅ Alles markieren/entmarkieren")

    for i, item in enumerate(data):
        if alle_markieren:
            item["Erledigt"] = True

        cols = st.columns([4, 2, 1])
        erledigt = cols[0].checkbox(
            f"{item['Produktkategorie']} {item['Produkt']} — {item['Menge']}",
            value=item["Erledigt"],
            key=f"chk{i}"
        )
        cols[1].write(item["Einkaufsstätte"])

        if cols[2].button("❌", key=f"del{i}"):
            st.session_state["to_delete"] = {"index": i, "produkt": item["Produkt"], "kategorie": item["Produktkategorie"]}
        item["Erledigt"] = erledigt

# ==================================================
# Löschbestätigung
# ==================================================
if "to_delete" in st.session_state:
    td = st.session_state["to_delete"]
    st.warning(f"Soll **{td['kategorie']} {td['produkt']}** wirklich gelöscht werden?")
    c1, c2 = st.columns(2)
    if c1.button("✅ Ja, löschen"):
        idx = td["index"]
        if 0 <= idx < len(data):
            data.pop(idx)
        save_data(DATA_FILE, data)
        del st.session_state["to_delete"]
        st.success("Artikel gelöscht ✅")
        safe_rerun()
    if c2.button("❌ Abbrechen"):
        del st.session_state["to_delete"]
        st.info("Löschen abgebrochen.")

# ==================================================
# Buttons: Alles erledigen / Alles löschen / Archiv / PDF
# ==================================================
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
if c1.button("✅ Alles erledigen"):
    for item in data:
        item["Erledigt"] = True
    save_data(DATA_FILE, data)
    safe_rerun()

if c2.button("🗑️ Alles löschen"):
    data = []
    save_data(DATA_FILE, data)
    safe_rerun()

if c3.button("💾 Einkauf speichern"):
    if data:
        datum = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(ARCHIV_DIR, f"einkauf_{datum}.json")
        save_data(filename, data)
        st.success(f"Einkaufsliste als {filename} gespeichert!")

if c4.button("📄 PDF exportieren"):
    pdfname = export_pdf(data)
    st.success(f"PDF '{pdfname}' wurde erstellt!")

save_data(DATA_FILE, data)
