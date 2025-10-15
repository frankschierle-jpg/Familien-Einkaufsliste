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
    """PDF Export der Einkaufsliste"""
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
            "🍎 Obst","🥦 Gemüse","🥐 Frühstück","🍯 Brotaufstrich","🍫 Süßwaren","🥨 Backwaren",
            "🌭 Wurst","🧀 Käse","🥛 Molkereiprodukte","🥩 Fleisch","🐟 Fisch",
            "🫘 (Trocken-)Konserven","🍟 Salzgebäck","🥤 Getränke",
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

# Alte Daten ergänzen
for item in data:
    item.setdefault("Produktkategorie", "⚙️ Sonstiges")
    item.setdefault("Besteller", "Unbekannt")
    item.setdefault("Erledigt", False)

# =============================
# Kategorien + Produkte
# =============================
KATEGORIEN = {
    "🍎 Obst": ["Apfel", "Banane", "Birne", "Pfirsich", "Traube", "Erdbeere", "Himbeere"],
    "🥦 Gemüse": ["Tomate", "Gurke", "Paprika", "Zwiebel", "Kartoffel", "Karotte", "Brokkoli"],
    "🥐 Frühstück": ["Müsli", "Haferflocken", "Cornflakes"],
    "🥨 Backwaren": ["Brot", "Brötchen", "Baguette", "Toast", "Croissant"],
    "🌭 Wurst": ["Salami", "Schinken", "Lyoner"],
    "🧀 Käse": ["Gouda", "Mozzarella", "Feta"],
    "🥛 Molkereiprodukte": ["Milch", "Joghurt", "Butter"],
    "🥩 Fleisch": ["Rindfleisch", "Hähnchen", "Schweinefleisch"],
    "🐟 Fisch": ["Lachs", "Thunfisch"],
    "🫘 (Trocken-)Konserven": ["Reis", "Linsen", "Bohnen", "Spaghetti"],
    "🍯 Brotaufstrich": ["Honig", "Marmelade", "Nutella"],
    "🍫 Süßwaren": ["Schokolade", "Gummibärchen", "Riegel"],
    "🍟 Salzgebäck": ["Chips", "Salzstangen"],
    "🥤 Getränke": ["Wasser", "Bier", "Cola"],
    "🧴 Drogerie": ["Zahnpasta", "Shampoo", "Seife"],
    "🧼 Wasch- und Reinigungsmittel": ["Waschpulver", "Glasreiniger"],
    "⚙️ Sonstiges": []
}

ALL_PRODUCTS = sorted({p.lower(): p for items in KATEGORIEN.values() for p in items}.values())

# =============================
# Neues Produkt hinzufügen
# =============================
with st.form("add_item", clear_on_submit=True):
    produkt_input = st.text_input("Produktname (ab 3 Buchstaben)").strip()
    menge = st.text_input("Menge (z. B. 1 Stück, 500 g)", "1")
    laden = st.selectbox("Einkaufsstätte", sorted(["Aldi", "DM", "Edeka", "Kaufland", "Lidl", "Rewe", "Rossmann", "Sonstiges"]))

    produkt = produkt_input.capitalize()
    if len(produkt) >= 3:
        matches = difflib.get_close_matches(produkt.lower(), [p.lower() for p in ALL_PRODUCTS], n=1, cutoff=0.6)
        if matches:
            produkt = next((p for p in ALL_PRODUCTS if p.lower() == matches[0]), produkt)

    submitted = st.form_submit_button("Hinzufügen")
    if submitted and produkt:
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
# Einkaufsliste anzeigen
# =============================
st.subheader("🧾 Einkaufsliste")

if not data:
    st.info("Liste ist leer.")
else:
    kategorien_order = [
        "🍎 Obst", "🥦 Gemüse", "🥐 Frühstück", "🍯 Brotaufstrich", "🍫 Süßwaren",
        "🥨 Backwaren", "🌭 Wurst", "🧀 Käse", "🥛 Molkereiprodukte", "🥩 Fleisch",
        "🐟 Fisch", "🫘 (Trocken-)Konserven", "🍟 Salzgebäck", "🥤 Getränke",
        "🧴 Drogerie", "🧼 Wasch- und Reinigungsmittel", "⚙️ Sonstiges"
    ]

    unique_stores = sorted({x["Einkaufsstätte"] for x in data})
    for store in unique_stores:
        store_items = [x for x in data if x["Einkaufsstätte"] == store]
        store_items.sort(key=lambda x: kategorien_order.index(x["Produktkategorie"]))

        # Überschrift + Checkbox nebeneinander
        header_col1, header_col2 = st.columns([4, 1])
        header_col1.markdown(f"### 🛍 {store}")
        store_done_key = f"store_done_{store}"
        all_done = all(item["Erledigt"] for item in store_items)
        mark_all = header_col2.checkbox("Alles erledigt", value=all_done, key=store_done_key)
        for item in store_items:
            item["Erledigt"] = mark_all
        save_data(DATA_FILE, data)

        for i, item in enumerate(store_items):
            cols = st.columns([3, 1, 0.7, 0.7])
            bg_color = "#d4edda" if item["Erledigt"] else "#ffffff"
            style = f"background-color:{bg_color};padding:6px;border-radius:8px;"
            cols[0].markdown(f"<div style='{style}'>{item['Produktkategorie']} {item['Produkt']} — {item['Menge']}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div style='{style}'>{item['Besteller']}</div>", unsafe_allow_html=True)

            if cols[2].button("✅", key=f"done_{store}_{i}"):
                item["Erledigt"] = not item["Erledigt"]
                save_data(DATA_FILE, data)
                safe_rerun()

            if cols[3].button("❌", key=f"delete_{store}_{i}"):
                # einfache Bestätigung mit Session-Flag
                if "confirm_delete" not in st.session_state:
                    st.session_state.confirm_delete = None
                if st.session_state.confirm_delete == i:
                    data.remove(item)
                    st.session_state.confirm_delete = None
                    save_data(DATA_FILE, data)
                    safe_rerun()
                else:
                    st.warning(f"Nochmals ❌ klicken, um **{item['Produkt']}** zu löschen!")
                    st.session_state.confirm_delete = i

# =============================
# Archiv & PDF & Abschluss
# =============================
st.markdown("---")
c1, c2, c3 = st.columns(3)
if c1.button("💾 Einkauf speichern"):
    if data:
        datum = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(ARCHIV_DIR, f"einkauf_{datum}.json")
        save_data(filename, data)
        st.success(f"Einkaufsliste gespeichert als **{filename}**")

if c2.button("📄 PDF exportieren"):
    export_pdf(data)

if c3.button("✅ Einkauf abschließen"):
    if data:
        datum = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(ARCHIV_DIR, f"abgeschlossen_{datum}.json")
        save_data(filename, data)
        data = []
        save_data(DATA_FILE, data)
        st.success("🛒 Einkauf abgeschlossen und archiviert!")
        safe_rerun()

# =============================
# Abgeschlossene Einkäufe anzeigen
# =============================
st.markdown("## 📦 Abgeschlossene Einkäufe")
archiv_files = sorted([f for f in os.listdir(ARCHIV_DIR) if f.startswith("abgeschlossen_")], reverse=True)
if not archiv_files:
    st.info("Noch keine abgeschlossenen Einkäufe.")
else:
    for f in archiv_files:
        date_str = f.replace("abgeschlossen_", "").replace(".json", "")
        with st.expander(f"📅 Einkauf vom {date_str}"):
            einkauf = load_data(os.path.join(ARCHIV_DIR, f))
            if not einkauf:
                st.write("_(leer)_")
            else:
                for item in einkauf:
                    st.markdown(f"- {item['Produktkategorie']} **{item['Produkt']}** — {item['Menge']} ({item['Einkaufsstätte']})")

save_data(DATA_FILE, data)
