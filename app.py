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
            "🍎 Obst","🥦 Gemüse","🥐 Frühstück","🍯 Brotaufstrich","🍫 Süßwaren",
            "🥨 Backwaren","🌭 Wurst","🧀 Käse","🥛 Molkereiprodukte",
            "🥩 Fleisch","🐟 Fisch","🫘 (Trocken-)Konserven",
            "🍟 Salzgebäck","🥤 Getränke","🧴 Drogerie",
            "🧼 Wasch- und Reinigungsmittel","⚙️ Sonstiges"
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
    st.success(f"📄 PDF '{filename}' wurde erstellt!")


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
# Login
# =============================
PASSWORD = "geheim123"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛒 Schierles Smart Shopper")
    with st.form("login_form", clear_on_submit=False):
        user_input = st.text_input("👤 Benutzername")
        pw = st.text_input("🔑 Passwort", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if pw == PASSWORD and user_input.strip():
                st.session_state.logged_in = True
                st.session_state.user = user_input.strip()
                safe_rerun()
            else:
                st.error("❌ Falsches Passwort oder Benutzername fehlt")
    st.stop()

# =============================
# Hauptseite
# =============================
st.title("🛒 Schierles Smart Shopper")
st.write(f"👤 Angemeldet als: **{st.session_state.user}**")
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    safe_rerun()

DATA_FILE = "einkaufsliste.json"
ARCHIV_DIR = "archiv"
os.makedirs(ARCHIV_DIR, exist_ok=True)
data = load_data(DATA_FILE)

# Daten absichern
for item in data:
    item.setdefault("Produktkategorie", "⚙️ Sonstiges")
    item.setdefault("Besteller", "Unbekannt")
    item.setdefault("Erledigt", False)

# =============================
# Kategorien
# =============================
KATEGORIEN = {
    "🍎 Obst": ["Apfel","Banane","Birne","Traube","Erdbeere"],
    "🥦 Gemüse": ["Tomate","Gurke","Paprika","Zwiebel","Kartoffel"],
    "🥐 Frühstück": ["Müsli","Haferflocken","Hefegebäck"],
    "🥨 Backwaren": ["Brot","Brötchen","Baguette","Toast"],
    "🌭 Wurst": ["Salami","Schinken","Lyoner"],
    "🧀 Käse": ["Gouda","Mozzarella","Feta"],
    "🥛 Molkereiprodukte": ["Milch","Joghurt","Butter"],
    "🥩 Fleisch": ["Rindfleisch","Hähnchen","Schweinefleisch"],
    "🐟 Fisch": ["Lachs","Thunfisch"],
    "🫘 (Trocken-)Konserven": ["Reis","Linsen","Bohnen","Spaghetti"],
    "⚙️ Sonstiges": []
}
ALL_PRODUCTS = sorted(list({p for items in KATEGORIEN.values() for p in items}))

# =============================
# Neues Produkt
# =============================
with st.form("add_item", clear_on_submit=True):
    produkt_input = st.text_input("Produktname (ab 3 Buchstaben)")
    menge = st.text_input("Menge", "1")
    laden = st.selectbox("Einkaufsstätte", sorted(["Aldi","DM","Edeka","Kaufland","Lidl","Rewe","Rossmann","Sonstiges"]))
    produkt = produkt_input.strip()
    if len(produkt) >= 3:
        matches = difflib.get_close_matches(produkt.lower(), [p.lower() for p in ALL_PRODUCTS], n=1, cutoff=0.6)
        if matches:
            produkt = next(p for p in ALL_PRODUCTS if p.lower() == matches[0])

    if st.form_submit_button("Hinzufügen") and produkt:
        kategorie = next((kat for kat, items in KATEGORIEN.items() if produkt in items), "⚙️ Sonstiges")
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
# Einkaufsliste
# =============================
st.subheader("🧾 Einkaufsliste")

if not data:
    st.info("Liste ist leer.")
else:
    kategorien_order = [
        "🍎 Obst","🥦 Gemüse","🥐 Frühstück","🥨 Backwaren",
        "🌭 Wurst","🧀 Käse","🥛 Molkereiprodukte",
        "🥩 Fleisch","🐟 Fisch","🫘 (Trocken-)Konserven","⚙️ Sonstiges"
    ]
    unique_stores = sorted(list({x["Einkaufsstätte"] for x in data}))

    for store in unique_stores:
        store_items = [x for x in data if x["Einkaufsstätte"] == store]
        store_items.sort(key=lambda x: kategorien_order.index(x["Produktkategorie"]))
        cols = st.columns([0.9, 0.1])
        cols[0].subheader(f"🛍 {store}")
        store_check = cols[1].checkbox("Alles markiert", key=f"all_{store}")

        for i, item in enumerate(store_items):
            cols = st.columns([3, 1, 1, 1])
            bg_color = "#d4edda" if item["Erledigt"] else "#ffffff"
            cols[0].markdown(f"<div style='background-color:{bg_color};padding:4px'>{item['Produktkategorie']} {item['Produkt']} — {item['Menge']}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div style='background-color:{bg_color};padding:4px'>{item['Besteller']}</div>", unsafe_allow_html=True)

            # ✅ Haken (Einzeln oder Alle)
            if cols[2].button("✅", key=f"done_{store}_{i}"):
                if store_check:
                    all_done = all(it["Erledigt"] for it in store_items)
                    for it in store_items:
                        it["Erledigt"] = not all_done
                else:
                    item["Erledigt"] = not item["Erledigt"]
                save_data(DATA_FILE, data)
                safe_rerun()

            # ❌ Löschen (Einzeln oder Alle)
            if cols[3].button("❌", key=f"del_{store}_{i}"):
                if store_check:
                    st.warning(f"❗ Sollen **alle Produkte in {store}** gelöscht werden?")
                    c1, c2 = st.columns(2)
                    if c1.button(f"Ja, alle {store}-Produkte löschen", key=f"yes_all_{store}_{i}"):
                        data = [x for x in data if x["Einkaufsstätte"] != store]
                        save_data(DATA_FILE, data)
                        safe_rerun()
                    if c2.button("Nein", key=f"no_all_{store}_{i}"):
                        safe_rerun()
                else:
                    st.warning(f"❗ Produkt **{item['Produkt']}** löschen?")
                    c1, c2 = st.columns(2)
                    if c1.button("Ja", key=f"yes_{store}_{i}"):
                        data.remove(item)
                        save_data(DATA_FILE, data)
                        safe_rerun()
                    if c2.button("Nein", key=f"no_{store}_{i}"):
                        safe_rerun()

# =============================
# Archiv & PDF
# =============================
st.markdown("---")
c1, c2, c3 = st.columns(3)

if c1.button("💾 Einkauf speichern"):
    if data:
        datum = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(ARCHIV_DIR, f"einkauf_{datum}.json")
        save_data(filename, data)
        st.success(f"Einkaufsliste als {filename} gespeichert!")

if c2.button("📄 PDF exportieren"):
    export_pdf(data)

if c3.button("✅ Einkauf abschließen"):
    if data:
        datum = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(ARCHIV_DIR, f"abgeschlossen_{datum}.json")
        save_data(filename, data)
        data.clear()
        save_data(DATA_FILE, data)
        st.success("🛍 Einkauf abgeschlossen und archiviert!")
        safe_rerun()

# Archiv anzeigen
st.markdown("---")
st.subheader("📚 Abgeschlossene Einkäufe")
files = sorted(os.listdir(ARCHIV_DIR), reverse=True)
for f in files:
    if f.startswith("abgeschlossen_"):
        with st.expander(f.replace(".json", "")):
            try:
                with open(os.path.join(ARCHIV_DIR, f), "r", encoding="utf-8") as fh:
                    past = json.load(fh)
                for p in past:
                    st.write(f"- {p['Einkaufsstätte']}: {p['Produkt']} ({p['Menge']}) – {p['Produktkategorie']}")
            except:
                st.error("Archivdatei beschädigt.")
