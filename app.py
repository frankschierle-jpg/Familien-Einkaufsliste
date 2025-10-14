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
        kategorien_order = ["🍎 Obst", "🥦 Gemüse", "🥐 Frühstück", "🥨 Backwaren", "🌭 Wurst",
                            "🧀 Käse", "🥛 Molkereiprodukte", "🥩 Fleisch", "🐟 Fisch",
                            "🫘 (Trocken-)Konserven", "🍯 Brotaufstrich", "🍫 Süßwaren", "🍟 Salzgebäck",
                            "🧴 Drogerie", "🥤 Getränke", "🧼 Wasch- und Reinigungsmittel", "⚙️ Sonstiges"]
        # Zunächst nach Einkaufsstätte sortieren
        data.sort(key=lambda x: (x["Einkaufsstätte"], kategorien_order.index(x["Produktkategorie"]) if x["Produktkategorie"] in kategorien_order else 999))
        current_shop = ""
        for item in data:
            if item["Einkaufsstätte"] != current_shop:
                current_shop = item["Einkaufsstätte"]
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(200, 10, txt=f"Einkaufsstätte: {current_shop}", ln=True)
            # Kategorie header
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(200, 10, txt=item["Produktkategorie"], ln=True)
            pdf.set_font("Helvetica", size=11)
            status = "✅" if item["Erledigt"] else "⬜"
            line = f"{status} {item['Produkt']} — {item['Menge']} von {item['Besteller']}"
            pdf.cell(200, 8, txt=line, ln=True)
            pdf.ln(2)
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
    "🥩 Fleisch": ["Rindfleisch","Hähnchen","Schweinefleisch","Hackfleisch","Steak","Hähnchenbrust","Pute","Kotelett","Speck","Hacksteak"],
    "🐟 Fisch": ["Lachs","Forelle","Thunfisch","Seelachs","Garnelen","Kabeljau","Sardinen","Makrele","Heilbutt","Hering","Scholle","Rotbarsch"],
    "🫘 (Trocken-)Konserven": ["Linsen","Bohnen","Wildreis","Langkornreis","Risotto Reis","Spaghetti","Tagliatelle","Spätzle","Mais","Tomaten ganz","Tomaten gestückelt","Kichererbsen","Erbsen","Kidneybohnen","Bulgur","Quinoa","Couscous","Rote Linsen","Gelbe Linsen","Haferflocken","Kokosmilch","Tomatenmark"],
    "🍯 Brotaufstrich": ["Nutella","Honig","Marmelade","Erdbeermarmelade","Konfitüre","Marmeladenglas","Pflaumenmus","Aprikosenmarmelade","Kirschmarmelade","Orangenmarmelade","Erdnussbutter","Haselnusscreme","Schokocreme","Fruchtaufstrich","Nuss-Nougat"],
    "🍫 Süßwaren": ["Schokolade","Milka","Kinderriegel","Gummibärchen","Bonbons","Mars","Snickers","Twix","Riegel","Lakritz","Smarties","KitKat","Ferrero Rocher","Toffifee","Pralinen"],
    "🍟 Salzgebäck": ["Chips","Erdnussflips","Salzstangen","Cracker","Brezelsticks","Cheeseballs","Käsecracker","Popcorn gesalzen","Käsechips","Maischips"],
    "🧴 Drogerie": ["Zahnpasta","Zahnbürste","Shampoo","Nivea","Seife","Duschgel","Rasiergel","Deodorant","Haarspülung","Handcreme","Sonnencreme","Lotion"],
    "🥤 Getränke": ["Cola","Coca-Cola","Bier","Wasser","Saft","Tee","Kaffee","Wein","Limo","Orangensaft","Apfelsaft","Eistee","Mineralwasser"],
    "🧼 Wasch- und Reinigungsmittel": ["Waschpulver","Glasreiniger","Badreiniger","Spülmaschinentabs","Allzweckreiniger","Spülmittelflasche","Bodenreiniger","WC-Reiniger","Fleckenentferner","Desinfektionsmittel"],
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
    kategorien_order = ["🍎 Obst", "🥦 Gemüse", "🥐 Frühstück", "🥨 Backwaren", "🌭 Wurst",
                        "🧀 Käse", "🥛 Molkereiprodukte", "🥩 Fleisch", "🐟 Fisch",
                        "🫘 (Trocken-)Konserven", "🍯 Brotaufstrich", "🍫 Süßwaren", "🍟 Salzgebäck",
                        "🧴 Drogerie", "🥤 Getränke", "🧼 Wasch- und Reinigungsmittel", "⚙️ Sonstiges"]

    # Sortieren nach Einkaufsstätte und Kategorienreihenfolge
    data.sort(key=lambda x: (x["Einkaufsstätte"], kategorien_order.index(x["Produktkategorie"]) if x["Produktkategorie"] in kategorien_order else 999))

    for i, item in enumerate(data):
        cols = st.columns([3,1,1,1,1])
        bg_color = "#d4edda" if item["Erledigt"] else "#ffffff"
        cols[0].markdown(f"<div style='background-color:{bg_color};padding:4px'>{item['Produktkategorie']} {item['Produkt']} — {item['Menge']}</div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div style='background-color:{bg_color};padding:4px'>{item['Einkaufsstätte']}</div>", unsafe_allow_html=True)
        cols[2].markdown(f"<div style='background-color:{bg_color};padding:4px'>{item['Besteller']}</div>", unsafe_allow_html=True)

        # ✅ Toggle erledigt
        if cols[3].button("✅", key=f"done{i}"):
            if alle_markieren:
                for it in data:
                    it["Erledigt"] = not it["Erledigt"]
            else:
                item["Erledigt"] = not item["Erledigt"]
            save_data(DATA_FILE, data)
            safe_rerun()

        # ❌ Löschen
        if cols[4].button("❌", key=f"del{i}"):
            if alle_markieren:
                data.clear()
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
        datum = datetime.now().strftime("%Y-%m-%d_%H-%
