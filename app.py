import streamlit as st
import json
import os
from datetime import datetime
import difflib

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
    pdf.cell(200, 10, txt="🛒 Schierles Smart Shopper", ln=True, align="C")
    pdf.ln(10)
    if not data:
        pdf.cell(200, 10, txt="Liste ist leer.", ln=True)
    else:
        kategorien_order = [
            "🍎 Obst","🥦 Gemüse","🥐 Frühstück","🍯 Brotaufstrich","🍫 Süßwaren""🥨 Backwaren","🌭 Wurst","🧀 Käse","🥛 Molkereiprodukte",
            "🥩 Fleisch","🐟 Fisch","🫘 (Trocken-)Konserven","🍟 Salzgebäck","🥤 Getränke",
            "🧴 Drogerie","🧼 Wasch- und Reinigungsmittel","⚙️ Sonstiges"
        ]
        for kat in kategorien_order:
            items_in_cat = [x for x in data if x["Produktkategorie"] == kat]
            if items_in_cat:
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(200, 10, txt=kat, ln=True)
                pdf.set_font("Helvetica", size=11)
                for item in items_in_cat:
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
    st.title("🛒 Schierles Smart Shopper")
    with st.form("login_form", clear_on_submit=False):
        user_input = st.text_input("👤 User", key="login_user")
        pw = st.text_input("🔑 Passwort", type="password", key="login_pw")
        submitted = st.form_submit_button("Login")
        if submitted:
            if pw == PASSWORD and user_input.strip():
                st.session_state.logged_in = True
                st.session_state.user = user_input.strip()
                safe_rerun()
            else:
                st.error("❌ Falsches Passwort oder kein Benutzername angegeben")
    st.stop()

# =============================
# Hauptseite
# =============================
st.title("🛒 Schierles Smart Shopper")
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
    "🥐 Frühstück": ["Kekse","Müsli","Haferflocken","Hefegebäck","Cornflakes","Zimtbrötchen"],
    "🥨 Backwaren": ["Brot","Vollkornbrot","Weizenbrot","Roggenbrot","Brötchen","Croissant","Brezel",
                     "Toast","Ciabatta","Baguette","Kaiserbrötchen","Laugensemmel","Schwarzbrot",
                     "Dinkelbrot","Rosinenbrötchen","Focaccia","Pain de Campagne","Fladenbrot",
                     "Pita","Bagel","Muffin"],
    "🌭 Wurst": ["Salami","Schinken","Mortadella","Lyoner","Bratwurst","Weißwurst","Leberwurst",
                "Cervelat","Bauernwurst","Mettwurst"],
    "🧀 Käse": ["Gouda","Emmentaler","Mozzarella","Camembert","Feta","Parmesan","Edamer",
                "Tilsiter","Bergkäse","Frischkäse","Ziegenkäse"],
    "🥛 Molkereiprodukte": ["Milch","Joghurt","Sahne","Quark","Butter","Schmand","Kefir","Buttermilch",
                            "Lassi","Molke","Frischmilch","Schlagsahne"],
    "🥩 Fleisch": ["Rindfleisch","Hähnchen","Schweinefleisch","Hackfleisch","Steak","Wurst",
                   "Hähnchenbrust","Pute","Kotelett","Speck","Hacksteak"],
    "🐟 Fisch": ["Lachs","Forelle","Thunfisch","Seelachs","Garnelen","Kabeljau","Sardinen",
                 "Makrele","Heilbutt","Hering","Scholle","Rotbarsch"],
    "🫘 (Trocken-)Konserven": ["Linsen","Bohnen","Wildreis","Langkornreis","Risotto Reis","Spaghetti",
                               "Tagliatelle","Spätzle","Mais","Tomaten ganz","Tomaten gestückelt",
                               "Kichererbsen","Erbsen","Kidneybohnen","Bulgur","Quinoa","Couscous",
                               "Rote Linsen","Gelbe Linsen","Haferflocken","Kokosmilch","Tomatenmark"],
    "🍯 Brotaufstrich": ["Nutella","Honig","Marmelade","Erdbeermarmelade","Konfitüre","Marmeladenglas",
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
    "⚙️ Sonstiges": []
}

ALL_PRODUCTS = sorted(list({p for items in KATEGORIEN.values() for p in items}))

# =============================
# Neues Produkt hinzufügen
# =============================
with st.form("add_item", clear_on_submit=True):
    produkt_input = st.text_input("Produktname (ab 3 Buchstaben)")
    menge = st.text_input("Menge (z. B. 1 Stück, 500 g)", "1")
    laden = st.selectbox("Einkaufsstätte", sorted(["Aldi","DM","Edeka","Kaufland","Lidl","Rewe","Rossmann","Sonstiges"]))

    produkt = produkt_input.strip()
    if len(produkt) >= 3:
        matches = difflib.get_close_matches(produkt, ALL_PRODUCTS, n=1, cutoff=0.6)
        if matches:
            produkt = matches[0]

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

    # Checkbox pro Einkaufsstätte
    unique_stores = sorted(list({x["Einkaufsstätte"] for x in data}))
    store_checkbox_state = {}
    for store in unique_stores:
        store_checkbox_state[store] = st.checkbox(f"✅ Alles in {store} erledigen", key=f"store_{store}")
        if store_checkbox_state[store]:
            for item in data:
                if item["Einkaufsstätte"] == store:
                    item["Erledigt"] = True
        save_data(DATA_FILE, data)

    kategorien_order = [
        "🍎 Obst","🥦 Gemüse","🥐 Frühstück","🍯 Brotaufstrich","🍫 Süßwaren","🥨 Backwaren","🌭 Wurst","🧀 Käse","🥛 Molkereiprodukte",
        "🥩 Fleisch","🐟 Fisch","🫘 (Trocken-)Konserven","🍟 Salzgebäck","🥤 Getränke",
        "🧴 Drogerie","🧼 Wasch- und Reinigungsmittel","⚙️ Sonstiges"
    ]
    data.sort(key=lambda x: (x["Einkaufsstätte"], kategorien_order.index(x["Produktkategorie"])))

    for i, item in enumerate(data):
        cols = st.columns([3,1,1,1,1])
        bg_color = "#d4edda" if item["Erledigt"] else "#ffffff"
        cols[0].markdown(f"<div style='background-color:{bg_color};padding:4px'>{item['Produktkategorie']} {item['Produkt']} — {item['Menge']}</div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div style='background-color:{bg_color};padding:4px'>{item['Einkaufsstätte']}</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div style='background-color:{bg_color};padding:4px'>{item['Besteller']}</div>", unsafe_allow_html=True)

        # ✅ Toggle erledigt
        if cols[3].button("✅", key=f"done{i}"):
            item["Erledigt"] = not item["Erledigt"]
            save_data(DATA_FILE, data)
            safe_rerun()

        # ❌ Löschen
        delete_key = f"delete_{i}"
        if cols[4].button("❌", key=delete_key):
            st.session_state[f"modal_delete_{i}"] = True

        if st.session_state.get(f"modal_delete_{i}", False):
            modal = st.modal("Löschen bestätigen")
            with modal:
                st.write(f"Möchtest du **{item['Produkt']}** wirklich löschen?")
                if st.button("Ja, löschen", key=f"confirm_{i}"):
                    data.pop(i)
                    save_data(DATA_FILE, data)
                    st.session_state[f"modal_delete_{i}"] = False
                    safe_rerun()
                if st.button("Abbrechen", key=f"cancel_{i}"):
                    st.session_state[f"modal_delete_{i}"] = False
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

