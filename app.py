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
        st.warning("📄 PDF-Export nicht verfügbar. Installiere fpdf.")
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
                line = f"{status} {item['Produkt']} — {item['Menge']} ({item['Einkaufsstätte']}) von {item['Besteller']}"
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
# Passwort + User Login
# =============================
PASSWORD = "geheim123"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛒 Familien Einkaufsliste")
    with st.form("login_form", clear_on_submit=False):
        user = st.text_input("👤 User", key="login_user")
        pw = st.text_input("🔑 Passwort", type="password", key="login_pw")
        submitted = st.form_submit_button("Login")
        if submitted:
            if pw == PASSWORD and user.strip():
                st.session_state.logged_in = True
                st.session_state.user = user.strip()
                safe_rerun()
            else:
                st.error("❌ Falsches Passwort oder kein Benutzername angegeben")
    st.stop()

# =============================
# Hauptseite
# =============================
st.title("🛒 Familien-Einkaufsliste")
st.write(f"Angemeldet als: **{st.session_state.user}**")
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
    if "Besteller" not in item:
        item["Besteller"] = "Unbekannt"

# =============================
# Kategorien + Produkte
# =============================
KATEGORIEN = {
    "🍎 Obst": ["Apfel","Banane","Birne","Pfirsich","Kirsche","Traube","Erdbeere","Himbeere","Blaubeere",
                "Melone","Wassermelone","Mango","Ananas","Orange","Mandarine","Zitrone","Limette",
                "Kiwi","Granatapfel","Feige","Aprikose","Passionsfrucht","Avocado","Cantaloupe",
                "Papaya","Johannisbeere","Holunderbeere","Preiselbeere","Rhabarber","Clementine",
                "Blutorange","Physalis","Nektarine","Brombeere","Boysenbeere","Kumquat","Sternfrucht",
                "Guave","Drachenfrucht","Kaki","Maracuja","Pomelo","Pflaume","Mandarinen","Heidelbeere",
                "Stachelbeere","Traube rot","Traube grün","Litschi","Granatapfelkern"],
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
    "🥨 Backwaren": ["Brot","Vollkornbrot","Weizenbrot","Roggenbrot","Brötchen","Croissant","Brezel","Bretzel"
                     "Toast","Ciabatta","Baguette","Kaiserbrötchen","Laugensemmel","Schwarzbrot",
                     "Dinkelbrot","Rosinenbrötchen","Focaccia","Pain de Campagne","Fladenbrot",
                     "Pita","Bagel","Muffin"],
    "🍯 Brotaufstrich": ["Nutella","Honig","Marmelade","Erdbeermarmelade","Konfitüre","Pflaumenmus",
                         "Aprikosenmarmelade","Kirschmarmelade","Orangenmarmelade","Erdnussbutter",
                         "Haselnusscreme","Schokocreme","Fruchtaufstrich","Nuss-Nougat"],
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
    "🫘 (Trocken-)Konserven": ["Linsen","Bohnen","Wildreis","Langkornreis","Risotto Reis","Spaghetti",
                               "Tagliatelle","Spätzle","Mais","Tomaten ganz","Tomaten gestückelt",
                               "Kichererbsen","Erbsen","Kidneybohnen","Bulgur","Quinoa","Couscous",
                               "Rote Linsen","Gelbe Linsen","Haferflocken","Kokosmilch","Tomatenmark"],
    "⚙️ Sonstiges": []
}

# =============================
# Produktliste flach für Autovervollständigung
# =============================
ALL_PRODUCTS = sorted(list({p for items in KATEGORIEN.values() for p in items}))

# =============================
# Neues Produkt hinzufügen
# =============================
with st.form("add_item", clear_on_submit=True):
    produkt = st.text_input("Produktname (ab 3 Buchstaben)", key="produkt_autocomplete")
    menge = st.text_input("Menge (z. B. 1 Stück, 500 g)", "1")
    laden = st.selectbox("Einkaufsstätte", ["Aldi","DM","Edeka","Lidl","Kaufland","Rewe","Sonstiges"])

    # Autocomplete Filter direkt im Eingabefeld
    if len(produkt.strip()) >= 3:
        matches = [p for p in ALL_PRODUCTS if produkt.lower() in p.lower()]
        if matches:
            produkt = matches[0]  # automatisch das erste Match nehmen

    submitted = st.form_submit_button("Hinzufügen")
    if submitted and produkt:
        kategorie = "⚙️ Sonstiges"
        for kat, items in KATEGORIEN.items():
            if produkt in items:
                kategorie = kat
                break
        neues_item = {
            "Produkt": produkt,
            "Menge": menge,
            "Produktkategorie": kategorie,
            "Einkaufsstätte": laden,
            "Erledigt": False,
            "Besteller": st.session_state.user
        }
        data.append(neues_item)
        save_data(DATA_FILE, data)
        st.success(f"{kategorie} {produkt} hinzugefügt!")

# =============================
# Einkaufsliste anzeigen
# =============================
st.subheader("🧾 Einkaufsliste")
if not data:
    st.info("Liste ist leer.")
else:
    alle_markieren = st.checkbox("✅ Alle markieren")

    for i, item in enumerate(data):
        cols = st.columns([3,1,1,1,1])
        bg_color = "#d4edda" if item["Erledigt"] else "#ffffff"
        cols[0].markdown(f"<div style='background-color:{bg_color};padding:4px'>{item['Produktkategorie']} {item['Produkt']} — {item['Menge']}</div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div style='background-color:{bg_color};padding:4px'>{item['Einkaufsstätte']}</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div style='background-color:{bg_color};padding:4px'>{item['Besteller']}</div>", unsafe_allow_html=True)

        if cols[3].button("✅", key=f"done{i}"):
            if alle_markieren:
                if st.confirm("Willst du wirklich alle Produkte als erledigt markieren?"):
                    for it in data:
                        it["Erledigt"] = True
            else:
                item["Erledigt"] = True
            save_data(DATA_FILE, data)
            safe_rerun()

        if cols[4].button("❌", key=f"del{i}"):
            if alle_markieren:
                if st.confirm("Willst du wirklich alle Produkte löschen?"):
                    data = []
            else:
                data.pop(i)
            save_data(DATA_FILE, data)
            safe_rerun()

# =============================
# Archiv & PDF
# =============================
st.markdown("---")
c1,c2 = st.columns(2)
if c1.button("💾 Einkauf speichern"):
    if data:
        datum = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(ARCHIV_DIR, f"einkauf_{datum}.json")
        save_data(filename, data)
        st.success(f"Einkaufsliste als {filename} gespeichert!")

if c2.button("📄 PDF exportieren"):
    export_pdf(data)

save_data(DATA_FILE, data)
