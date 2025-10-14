import streamlit as st
import json
import os
from datetime import datetime

# =============================
# PDF optional importieren
# =============================
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ModuleNotFoundError:
    PDF_AVAILABLE = False

def export_pdf(data, filename="Einkaufsliste.pdf"):
    if not PDF_AVAILABLE:
        st.warning("📄 PDF-Export nicht verfügbar. Installiere fpdf, wenn genügend Speicher vorhanden ist.")
        return
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
    st.success(f"PDF '{filename}' wurde erstellt!")

# =============================
# Hilfsfunktionen
# =============================
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

# =============================
# Passwortschutz
# =============================
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

# =============================
# Hauptseite
# =============================
st.title("🛒 Familien Einkaufsliste")
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    safe_rerun()

DATA_FILE = "einkaufsliste.json"
ARCHIV_DIR = "archiv"
os.makedirs(ARCHIV_DIR, exist_ok=True)

data = load_data(DATA_FILE)

# Alte Daten kompatibel machen
for item in data:
    if "Produktkategorie" not in item:
        item["Produktkategorie"] = "⚙️ Sonstiges"

# =============================
# Kategorien + Produkte
# =============================
KATEGORIEN = {
    "🍎 Obst": ["Apfel","Banane","Birne","Pfirsich","Kirsche","Traube","Erdbeere","Himbeere","Blaubeere",
                "Melone","Wassermelone","Mango","Ananas","Orange","Mandarine","Zitrone","Limette",
                "Kiwi","Granatapfel","Feige","Aprikose","Passionsfrucht","Avocado","Cantaloupe",
                "Papaya","Johannisbeere","Holunderbeere","Preiselbeere","Rhabarber","Clementine",
                "Blutorange","Physalis","Nektarine","Brombeere","Boysenbeere","Kumquat","Sternfrucht",
                "Guave","Drachenfrucht","Kaki","Maracuja","Pomelo","Erdbeer-Nutella Mix","Pflaume",
                "Mandarinen","Heidelbeere","Stachelbeere","Traube rot","Traube grün","Kaki","Litschi",
                "Granatapfelkern"],
    "🥦 Gemüse": ["Tomate","Gurke","Paprika","Zwiebel","Knoblauch","Kartoffel","Karotte","Brokkoli",
                 "Blumenkohl","Zucchini","Aubergine","Lauch","Sellerie","Radieschen","Rote Beete",
                 "Kohl","Spinat","Feldsalat","Fenchel","Chili","Rucola","Kürbis","Mais","Erbsen",
                 "Spargel","Okra","Artischocke","Mangold","Wirsing","Rettich","Pak Choi","Chinakohl",
                 "Bohnen","Linsen","Rosenkohl","Süßkartoffel","Pilze","Shiitake","Champignon"],
    "🥩 Fleisch": ["Rindfleisch","Hähnchen","Schweinefleisch","Hackfleisch","Steak","Wurst",
                   "Hähnchenbrust","Pute","Kotelett","Speck","Hacksteak"],
    "🐟 Fisch": ["Lachs","Forelle","Thunfisch","Seelachs","Garnelen","Kabeljau","Sardinen",
                 "Makrele","Heilbutt","Hering","Scholle","Rotbarsch"],
    "🧀 Käse": ["Gouda","Emmentaler","Mozzarella","Camembert","Feta","Parmesan","Edamer",
                "Tilsiter","Bergkäse","Frischkäse","Ziegenkäse"],
    "🌭 Wurst": ["Salami","Schinken","Mortadella","Lyoner","Bratwurst","Weißwurst","Leberwurst",
                "Cervelat","Bauernwurst","Mettwurst"],
    "🥛 Molkereiprodukte": ["Milch","Joghurt","Sahne","Quark","Butter","Schmand","Kefir","Buttermilch",
                            "Lassi","Molke","Frischmilch","Schlagsahne"],
    "🥨 Backwaren": ["Brot","Vollkornbrot","Weizenbrot","Roggenbrot","Brötchen","Croissant","Brezel",
                     "Toast","Ciabatta","Baguette","Kaiserbrötchen","Laugensemmel","Schwarzbrot",
                     "Dinkelbrot","Rosinenbrötchen","Focaccia","Pain de Campagne","Fladenbrot",
                     "Pita","Bagel","Muffin"],
    "🍓 Brotaufstrich": ["Nutella","Honig","Marmelade","Erdbeermarmelade","Konfitüre","Marmeladenglas",
                         "Pflaumenmus","Aprikosenmarmelade","Kirschmarmelade","Orangenmarmelade",
                         "Erdnussbutter","Haselnusscreme","Schokocreme","Fruchtaufstrich","Nuss-Nougat"],
    "🍫 Süßwaren": ["Schokolade","Milka","Kinderriegel","Gummibärchen","Bonbons","Mars","Snickers",
                   "Twix","Riegel","Lakritz","Smarties","KitKat","Ferrero Rocher","Toffifee","Pralinen"],
    "🍟 Salzgebäck": ["Chips","Erdnussflips","Salzstangen","Cracker","Brezelsticks","Cheeseballs",
                     "Käsecracker","Popcorn gesalzen","Käsechips","Maischips"],
    "🧴 Drogerie": ["Zahnpasta","Zahnbürste","Shampoo","Nivea","Seife","Duschgel","Rasiergel",
                   "Deodorant","Haarspülung","Handcreme","Sonnencreme","Lotion"],
    "🥤 Getränke": ["Cola","Coca-Cola","Bier","Wasser","Saft","Tee","Kaffee","Wein","Limo",
                   "Orangensaft","Apfelsaft","Eistee","Mineralwasser"],
    "🧼 Wasch- und Reinigungsmittel": ["Waschpulver","Glasreiniger","Badreiniger","Spülmaschinentabs",
                                       "Allzweckreiniger","Spülmittelflasche","Bodenreiniger",
                                       "WC-Reiniger","Fleckenentferner","Desinfektionsmittel"],
    "🥫 (Trocken-)Konserven": ["Linsen","Bohnen","Wildreis","Langkornreis","Risotto Reis","Spaghetti",
                               "Tagliatelle","Spätzle","Mais","Tomaten ganz","Tomaten gestückelt",
                               "Kichererbsen","Erbsen","Kidneybohnen","Bulgur","Quinoa","Couscous",
                               "Rote Linsen","Gelbe Linsen","Haferflocken","Kokosmilch","Tomatenmark"]
}

# =============================
# Autocomplete-Funktion ab 3 Buchstaben
# =============================
def autocomplete_vorschlaege(text):
    text = text.lower()
    vorschlaege = []
    if len(text) >= 3:
        for kat_items in KATEGORIEN.values():
            for prod in kat_items:
                if text in prod.lower():
                    vorschlaege.append(prod)
    return list(set(vorschlaege))[:10]  # max 10 Vorschläge

# =============================
# Neues Produkt hinzufügen mit Autocomplete
# =============================
with st.form("add_item", clear_on_submit=True):
    produkt_input = st.text_input("Produktname")
    menge = st.text_input("Menge (z. B. 1 Stück, 500 g)", "1")
    laden = st.selectbox("Einkaufsstätte", ["Rewe", "Aldi", "Lidl", "DM", "Edeka", "Kaufland", "Sonstiges"])

    # Vorschläge anzeigen
    if produkt_input.strip() and len(produkt_input.strip()) >= 3:
        vorschlaege = autocomplete_vorschlaege(produkt_input)
        if vorschlaege:
            st.info("Vorschläge: " + ", ".join(vorschlaege))

    submitted = st.form_submit_button("Hinzufügen")
    if submitted and produkt_input.strip():
        # Kategorie finden
        kategorie = "⚙️ Sonstiges"
        for kat, items in KATEGORIEN.items():
            if any(produkt_input.lower() in p.lower() for p in items):
                kategorie = kat
                break
        neues_item = {
            "Produkt": produkt_input.strip(),
            "Menge": menge.strip(),
            "Produktkategorie": kategorie,
            "Einkaufsstätte": laden,
            "Erledigt": False
        }
        data.append(neues_item)
        save_data(DATA_FILE, data)
        st.success(f"{kategorie} {produkt_input} hinzugefügt!")

# =============================
# Einkaufsliste anzeigen
# =============================
st.subheader("🧾 Einkaufsliste")
if not data:
    st.info("Liste ist leer.")
else:
    alle_markieren = st.checkbox("✅ Alles markieren/entmarkieren")
    for i, item in enumerate(data):
        if alle_markieren:
            item["Erledigt"] = True
        cols = st.columns([4,2,1])
        erledigt = cols[0].checkbox(
            f"{item['Produktkategorie']} {item['Produkt']} — {item['Menge']}",
            value=item["Erledigt"],
            key=f"chk{i}"
        )
        cols[1].write(item["Einkaufsstätte"])
        if cols[2].button("❌", key=f"del{i}"):
            st.session_state["to_delete"] = {"index": i, "produkt": item["Produkt"], "kategorie": item["Produktkategorie"]}
        item["Erledigt"] = erledigt

# =============================
# Löschbestätigung
# =============================
if "to_delete" in st.session_state:
    td = st.session_state["to_delete"]
    st.warning(f"Soll **{td['kategorie']} {td['produkt']}** wirklich gelöscht werden?")
    c1,c2 = st.columns(2)
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

# =============================
# Buttons: Alles erledigen / Alles löschen / Archiv / PDF
# =============================
st.markdown("---")
c1,c2,c3,c4 = st.columns(4)
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
    export_pdf(data)

save_data(DATA_FILE, data)
