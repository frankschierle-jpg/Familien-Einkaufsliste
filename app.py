import streamlit as st
import json
import os

# -------- Streamlit Seiteneinstellungen --------
st.set_page_config(page_title="Familien Einkaufsliste", page_icon="🛒")

# -------- Passwortschutz --------
PASSWORD = "geheim123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛒 Familien Einkaufsliste")
    user_password = st.text_input("Passwort eingeben", type="password")
    if st.button("Login"):
        if user_password == PASSWORD:
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Falsches Passwort!")
else:
    st.title("🛒 Familien Einkaufsliste")
    st.success("Willkommen! ✅")
    st.caption("Tipp: Diese App läuft komplett lokal – keine Cloud nötig!")

    DATA_FILE = "einkaufsliste.json"

    # -------- JSON Datei laden --------
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    else:
        data = []

    # -------- Neues Produkt hinzufügen --------
    with st.form("add_item", clear_on_submit=True):
        produkt = st.text_input("Produktname")
        menge = st.text_input("Menge (z.B. 1 Stück, 500 g)", "1")
        # <-- hier ist das Emoji-Array korrekt geschlossen
        symbol = st.selectbox(
            "Symbol",
            ["🥦", "🍞", "🥛", "🍫", "🍅", "🧻", "🧴", "🍎", "⚙️"]
        )
        laden = st.selectbox(
            "Einkaufsstätte",
            ["Rewe", "Aldi", "Lidl", "DM", "Edeka", "Kaufland", "Sonstiges"]
        )
        submitted = st.form_submit_button("Hinzufügen")

        if submitted and produkt.strip():
            neues_item = {
                "Produkt": produkt.strip(),
                "Menge": menge.strip(),
                "Symbol": symbol,
                "Einkaufsstätte": laden,
                "Erledigt": False
            }
            data.append(neues_item)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            st.success(f"{symbol} {produkt} wurde hinzugefügt!")

    # -------- Einkaufsliste anzeigen --------
    st.subheader("🧾 Einkaufsliste")

    if not data:
        st.info("Die Liste ist noch leer. Füge etwas hinzu!")
    else:
        for i, item in enumerate(data):
            cols = st.columns([4, 2, 1])
            erledigt = cols[0].checkbox(
                f"{item['Symbol']} {item['Produkt']} — {item['Menge']}",
                value=item.get("Erledigt", False),
                key=f"chk{i}"
            )
            cols[1].write(item["Einkaufsstätte"])

            if cols[2].button("❌", key=f"del{i}"):
                # Merke, was gelöscht werden soll
                st.session_state["to_delete"] = {"index": i, "produkt": item["Produkt"], "symbol": item["Symbol"]}

            item["Erledigt"] = erledigt

    # -------- Löschbestätigung (Expander-Fallback, zuverlässig) --------
    if "to_delete" in st.session_state:
        td = st.session_state["to_delete"]
        with st.expander("❗Löschen bestätigen", expanded=True):
            st.warning(f"{td['symbol']} **{td['produkt']}** wirklich löschen?")
            c1, c2 = st.columns(2)
            if c1.button("✅ Ja, löschen", key="confirm_delete"):
                # Versuche sicher per Index zu löschen
                if 0 <= td["index"] < len(data):
                    # prüfe zusätzlich Produktname zum Schutz vor Race-Conditions
                    if data[td["index"]].get("Produkt") == td["produkt"]:
                        data.pop(td["index"])
                    else:
                        # fallback: suche nach dem Produktnamen
                        for idx, it in enumerate(data):
                            if it.get("Produkt") == td["produkt"]:
                                data.pop(idx)
                                break
                else:
                    # fallback: suche nach dem Produktnamen
                    for idx, it in enumerate(data):
                        if it.get("Produkt") == td["produkt"]:
                            data.pop(idx)
                            break

                wit
