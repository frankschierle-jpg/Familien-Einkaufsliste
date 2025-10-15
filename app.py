import streamlit as st
import json
import os
from datetime import datetime
import difflib

# =============================
# Optional: PDF Export
# =============================
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ModuleNotFoundError:
    PDF_AVAILABLE = False

# =============================
# Optional: Marktguru
# =============================
try:
    from marktguru import Marktguru
    MG_AVAILABLE = True
    mg = Marktguru()  # Direkt nutzbar, kein API-Key nötig
except ModuleNotFoundError:
    MG_AVAILABLE = False

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
            items_in_cat = [x for x in data if x.get("Produktkategorie") == kat]
            if items_in_cat:
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(200, 10, txt=kat, ln=True)
                pdf.set_font("Helvetica", size=11)
                for item in items_in_cat:
                    status = "✅" if item.get("Erledigt") else "⬜"
                    line = f"{status} {item.get('Produkt')} — {item.get('Menge')} ({item.get('Einkaufsstätte')}) von {item.get('Besteller')}"
                    pdf.cell(200, 8, txt=line, ln=True)
                pdf.ln(5)
    pdf.output(filename)
    st.success(f"📄 PDF '{filename}' wurde erstellt!")

# =============================
# Setup / Daten laden
# =============================
DATA_FILE = "einkaufsliste.json"
ARCHIV_DIR = "archiv"
os.makedirs(ARCHIV_DIR, exist_ok=True)
data = load_data(DATA_FILE)

# Session-Flags
if "confirm_delete_item" not in st.session_state:
    st.session_state.confirm_delete_item = None
if "confirm_delete_store" not in st.session_state:
    st.session_state.confirm_delete_store = None
if "all_marked_store" not in st.session_state:
    st.session_state.all_marked_store = {}

# Alte Einträge kompatibel machen
for item in data:
    item.setdefault("Produktkategorie", "⚙️ Sonstiges")
    item.setdefault("Besteller", "Unbekannt")
    item.setdefault("Erledigt", False)

# =============================
# Kategorien
# =============================
KATEGORIEN = {
    "🍎 Obst": ["Apfel","Banane","Birne","Pfirsich","Kirsche","Traube","Erdbeere","Himbeere","Blaubeere"],
    "🥦 Gemüse": ["Tomate","Gurke","Paprika","Zwiebel","Knoblauch","Kartoffel","Karotte","Brokkoli"],
    "🥩 Fleisch": ["Rindfleisch","Hähnchen","Schweinefleisch","Hackfleisch"],
    "🐟 Fisch": ["Lachs","Forelle","Thunfisch"],
    "🧀 Käse": ["Gouda","Emmentaler","Mozzarella","Feta"],
    "🌭 Wurst": ["Salami","Schinken","Mortadella","Lyoner"],
    "🥛 Molkereiprodukte": ["Milch","Joghurt","Sahne","Quark","Butter"],
    "🥨 Backwaren": ["Brot","Brötchen","Croissant","Baguette"],
    "🍯 Brotaufstrich": ["Nutella","Honig","Marmelade"],
    "🍫 Süßwaren": ["Schokolade","Milka","Kinderriegel"],
    "🍟 Salzgebäck": ["Chips","Salzstangen","Cracker"],
    "🧴 Drogerie": ["Zahnpasta","Shampoo","Seife","Duschgel"],
    "🥤 Getränke": ["Cola","Wasser","Saft","Tee"],
    "🧼 Wasch- und Reinigungsmittel": ["Waschpulver","Glasreiniger","Allzweckreiniger"],
    "🫘 (Trocken-)Konserven": ["Linsen","Bohnen","Reis","Spaghetti"],
    "⚙️ Sonstiges": []
}
ALL_PRODUCTS = sorted({p.lower(): p for items in KATEGORIEN.values() for p in items}.values())

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

# =============================
# Neues Produkt hinzufügen
# =============================
with st.form("add_item", clear_on_submit=True):
    produkt_input = st.text_input("Produktname (ab 3 Buchstaben)").strip()
    menge = st.text_input("Menge (z. B. 1 Stück, 500 g)", "1")
    laden = st.selectbox("Einkaufsstätte", sorted(["Aldi","DM","Edeka","Kaufland","Lidl","Rewe","Rossmann","Sonstiges"]))

    produkt = produkt_input
    if len(produkt) >= 3:
        matches = difflib.get_close_matches(produkt.lower(), [p.lower() for p in ALL_PRODUCTS], n=1, cutoff=0.6)
        if matches:
            produkt = next((p for p in ALL_PRODUCTS if p.lower() == matches[0]), produkt)

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
        # Marktguru Preisschau
        # =============================
        if MG_AVAILABLE:
            st.info("💰 Preise von Marktguru:")
            try:
                results = mg.search(produkt)  # Suche nach Produkt
                if results:
                    for r in results[:5]:  # max. 5 Ergebnisse
                        st.markdown(f"- {r['product_name']} ({r['store_name']}) — {r['price']} €")
                else:
                    st.write("Keine aktuellen Preise gefunden.")
            except Exception as e:
                st.error(f"Fehler beim Abrufen der Preise: {e}")
        else:
            st.warning("Installiere 'marktguru', um Preise anzuzeigen: pip install marktguru")

# =============================
# Einkaufsliste anzeigen
# =============================
st.subheader("🧾 Einkaufsliste")
if not data:
    st.info("Liste ist leer.")
else:
    kategorien_order = [
        "🍎 Obst","🥦 Gemüse","🥐 Frühstück","🥨 Backwaren",
        "🌭 Wurst","🧀 Käse","🥛 Molkereiprodukte",
        "🥩 Fleisch","🐟 Fisch","🫘 (Trocken-)Konserven","🍯 Brotaufstrich",
        "🍫 Süßwaren","🍟 Salzgebäck","🥤 Getränke",
        "🧴 Drogerie","🧼 Wasch- und Reinigungsmittel","⚙️ Sonstiges"
    ]
    unique_stores = sorted({x["Einkaufsstätte"] for x in data})
    for store in unique_stores:
        store_items = [x for x in data if x["Einkaufsstätte"] == store]
        def cat_index(it):
            try:
                return kategorien_order.index(it.get("Produktkategorie", "⚙️ Sonstiges"))
            except ValueError:
                return len(kategorien_order)
        store_items.sort(key=cat_index)

        hcol, cbcol = st.columns([0.92, 0.08])
        hcol.markdown(f"### 🛍 {store}")
        if store not in st.session_state.all_marked_store:
            st.session_state.all_marked_store[store] = False
        new_val = cbcol.checkbox("", value=st.session_state.all_marked_store.get(store, False), key=f"all_marked_{store}")
        st.session_state.all_marked_store[store] = bool(new_val)

        if st.session_state.confirm_delete_store == store:
            warning_cols = st.columns([3,1,1])
            warning_cols[0].warning(f"SOLLEN ALLE PRODUKTE IN **{store}** GELÖSCHT WERDEN?")
            if warning_cols[1].button("Ja, alle löschen", key=f"confirm_del_store_yes_{store}"):
                data = [d for d in data if d["Einkaufsstätte"] != store]
                save_data(DATA_FILE, data)
                st.session_state.confirm_delete_store = None
                safe_rerun()
            if warning_cols[2].button("Nein", key=f"confirm_del_store_no_{store}"):
                st.session_state.confirm_delete_store = None
                safe_rerun()

        for local_i, item in enumerate(store_items):
            try:
                global_index = data.index(item)
            except ValueError:
                continue
            cols = st.columns([3,1,0.8,0.8])
            bg_color = "#d4edda" if item.get("Erledigt") else "#ffffff"
            border_color = "#28a745" if item.get("Erledigt") else "#e0e0e0"
            style = f"background-color:{bg_color};border:1px solid {border_color};padding:6px;border-radius:8px;"
            cols[0].markdown(f"<div style='{style}'>{item.get('Produktkategorie')} <b>{item.get('Produkt')}</b> — {item.get('Menge')}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div style='{style}'>{item.get('Besteller')}</div>", unsafe_allow_html=True)

            if cols[2].button("✅", key=f"done_{store}_{global_index}"):
                if st.session_state.all_marked_store.get(store, False):
                    currently_all = all(it.get("Erledigt") for it in store_items)
                    for it in store_items:
                        it["Erledigt"] = not currently_all
                else:
                    item["Erledigt"] = not bool(item.get("Erledigt"))
                save_data(DATA_FILE, data)
                safe_rerun()

            if cols[3].button("❌", key=f"del_{store}_{global_index}"):
                if st.session_state.all_marked_store.get(store, False):
                    st.session_state.confirm_delete_store = store
                    safe_rerun()
                else:
                    st.session_state.confirm_delete_item = global_index
                    safe_rerun()

            if st.session_state.confirm_delete_item == global_index:
                confirm_cols = st.columns([3,1,1])
                confirm_cols[0].warning(f"Produkt **{item.get('Produkt')}** wirklich löschen?")
                if confirm_cols[1].button("Ja, löschen", key=f"del_yes_{global_index}"):
                    if global_index < len(data) and data[global_index] == item:
                        data.pop(global_index)
                    else:
                        for idx, dd in enumerate(data):
                            if dd.get("Produkt") == item.get("Produkt") and dd.get("Einkaufsstätte") == item.get("Einkaufsstätte"):
                                data.pop(idx)
                                break
                    save_data(DATA_FILE, data)
                    st.session_state.confirm_delete_item = None
                    safe_rerun()
                if confirm_cols[2].button("Nein", key=f"del_no_{global_index}"):
                    st.session_state.confirm_delete_item = None
                    safe_rerun()

# =============================
# Archiv, Speichern, Abschließen
# =============================
st.markdown("---")
c1,c2,c3 = st.columns(3)
if c1.button("💾 Einkauf speichern"):
    if data:
        datum = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(ARCHIV_DIR, f"einkauf_{datum}.json")
        save_data(filename, data)
        st.success(f"Einkaufsliste als {filename} gespeichert!")

if c2.button("📄 PDF exportieren"):
    export_pdf(data)

if c3.button("🧾 Einkauf abschließen"):
    if data:
        datum = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(ARCHIV_DIR, f"abgeschlossen_{datum}.json")
        save_data(filename, data)
        data = []
        save_data(DATA_FILE, data)
        st.success("🧾 Einkauf abgeschlossen und archiviert!")
        safe_rerun()

# =============================
# Abgeschlossene Einkäufe
# =============================
st.markdown("---")
st.subheader("🧾 Abgeschlossene Einkäufe")
archiv_files = sorted([f for f in os.listdir(ARCHIV_DIR) if f.startswith("abgeschlossen_") or f.startswith("einkauf_")], reverse=True)
if not archiv_files:
    st.info("Noch keine abgeschlossenen Einkäufe.")
else:
    for f in archiv_files:
        date_str = f.replace("abgeschlossen_", "").replace("einkauf_", "").replace(".json", "")
        with st.expander(f"🧾 Einkauf vom {date_str}"):
            einkauf = load_data(os.path.join(ARCHIV_DIR, f))
            if not einkauf:
                st.write("_(leer)_")
            else:
                for item in einkauf:
                    st.markdown(f"- {item.get('Produktkategorie')} **{item.get('Produkt')}** — {item.get('Menge')} ({item.get('Einkaufsstätte')})")

save_data(DATA_FILE, data)
