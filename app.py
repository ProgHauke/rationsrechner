import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="fodjan-style Rationsrechner", layout="wide")

RATIONS_FILE = "rations_db.json"

# ---------------------------------------------------------
# 1. STANDARDFUTTERMITTEL
# ---------------------------------------------------------
default_data = [
    {
        "Name": "Gras-Silage 1. Schnitt", "Typ": "Grundfutter", 
        "TM_Prozent": 35.0, "Menge_kg_TM": 7.5,
        "NEL": 6.4, "XP": 160, "nXP": 140, "RNB": 3.2, "NDF": 450, "uNDF240": 160, "peNDF": 380, "Staarke": 20
    },
    {
        "Name": "Mais-Silage", "Typ": "Grundfutter", 
        "TM_Prozent": 33.0, "Menge_kg_TM": 6.5,
        "NEL": 6.7, "XP": 80, "nXP": 135, "RNB": -8.8, "NDF": 360, "uNDF240": 110, "peNDF": 290, "Staarke": 320
    },
    {
        "Name": "NG TMR Raps", "Typ": "Kraftfutter", 
        "TM_Prozent": 88.0, "Menge_kg_TM": 2.5,
        "NEL": 7.0, "XP": 380, "nXP": 240, "RNB": 22.4, "NDF": 280, "uNDF240": 120, "peNDF": 100, "Staarke": 30
    },
    {
        "Name": "NG AF Frey", "Typ": "Kraftfutter", 
        "TM_Prozent": 88.0, "Menge_kg_TM": 3.5,
        "NEL": 8.1, "XP": 110, "nXP": 165, "RNB": -8.8, "NDF": 120, "uNDF240": 30, "peNDF": 40, "Staarke": 520
    },
    {
        "Name": "Wasser (TMR-Befeuchtung)", "Typ": "Grundfutter", 
        "TM_Prozent": 0.0, "Menge_kg_TM": 2.0,
        "NEL": 0.0, "XP": 0, "nXP": 0, "RNB": 0.0, "NDF": 0, "uNDF240": 0, "peNDF": 0, "Staarke": 0
    },
]

# ---------------------------------------------------------
# SPEICHER-FUNKTIONEN FÜR MEHRERE RATIONEN (JSON-DATENBANK)
# ---------------------------------------------------------
def get_saved_rations():
    if os.path.exists(RATIONS_FILE):
        try:
            with open(RATIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"Standard Ration": default_data}
    else:
        return {"Standard Ration": default_data}

def save_rations_db(db):
    with open(RATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# Initialisierung
if "initial_df" not in st.session_state:
    rations_db = get_saved_rations()
    first_key = list(rations_db.keys())[0]
    st.session_state.initial_df = pd.DataFrame(rations_db[first_key])
    st.session_state.current_ration_name = first_key

# ---------------------------------------------------------
# NAVIGATION (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.title("🐄 Futter-Manager")
page = st.sidebar.radio("Navigation", ["📊 Rationsplanung (TM)", "🚚 Ladeliste Mischwagen"])

# =========================================================
# SEITE 1: RATIONSPLANUNG (TM-BASIS)
# =========================================================
if page == "📊 Rationsplanung (TM)":
    st.title("📊 Rationsplanung & Nährstoff-Check")
    st.caption("Planung auf Trockenmassebasis (kg TM/Kuh)")

    # 1. Tierdaten
    st.header("1. Tierdaten & Ziel-Bedarf")
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        kgh_ziel = st.number_input("Ziel-Milchleistung (kg ECM/Tag)", value=38.0, step=0.5)
        gewicht = st.number_input("Körpergewicht der Kuh (kg)", value=680, step=10)

    with col_t2:
        kg_075 = gewicht ** 0.75
        nel_bedarf_ziel = 0.293 * kg_075 + 3.14 * (kgh_ziel / 10)
        nxp_bedarf_ziel = 0.45 * kg_075 + 85 * (kgh_ziel / 10)
        
        st.metric("Orientierung NEL-Bedarf", f"{nel_bedarf_ziel:.1f} MJ")
        st.metric("Orientierung nXP-Bedarf", f"{nxp_bedarf_ziel:.0f} g/Tag")

    st.divider()

    # 2. Rations-Verwaltung (Laden / Speichern unter)
    st.header("2. Rationskomponenten & Speicher-Verwaltung")
    
    rations_db = get_saved_rations()
    ration_names = list(rations_db.keys())

    col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
    
    with col_m1:
        selected_ration = st.selectbox("Gespeicherte Ration wählen", ration_names, index=ration_names.index(st.session_state.current_ration_name) if st.session_state.current_ration_name in ration_names else 0)
        if st.button("📂 Gewählte Ration laden"):
            st.session_state.initial_df = pd.DataFrame(rations_db[selected_ration])
            st.session_state.current_ration_name = selected_ration
            st.rerun()

    with col_m2:
        new_name = st.text_input("Name zum Speichern / Ändern", value=st.session_state.current_ration_name)
        if st.button("💾 Ration speichern"):
            if new_name.strip():
                save_name = new_name.strip()
                current_data = st.session_state.active_df.to_dict("records") if "active_df" in st.session_state else st.session_state.initial_df.to_dict("records")
                rations_db[save_name] = current_data
                save_rations_db(rations_db)
                st.session_state.current_ration_name = save_name
                st.session_state.initial_df = pd.DataFrame(current_data)
                st.success(f"Ration '{save_name}' gespeichert!")
                st.rerun()

    with col_m3:
        st.write(" ")
        st.write(" ")
        if st.button("🗑️ Ration löschen") and len(ration_names) > 1:
            del rations_db[selected_ration]
            save_rations_db(rations_db)
            first_remaining = list(rations_db.keys())[0]
            st.session_state.initial_df = pd.DataFrame(rations_db[first_remaining])
            st.session_state.current_ration_name = first_remaining
            st.success(f"Ration '{selected_ration}' gelöscht!")
            st.rerun()

    # Interaktive Tabelle
    edited_df = st.data_editor(
        st.session_state.initial_df,
        num_rows="dynamic",
        column_config={
            "Name": st.column_config.TextColumn("Bezeichnung", required=True),
            "Typ": st.column_config.SelectboxColumn("Typ", options=["Grundfutter", "Kraftfutter"], required=True),
            "Menge_kg_TM": st.column_config.NumberColumn("Menge (kg TM / Liter)", min_value=0.0, max_value=60.0, format="%.2f"),
            "TM_Prozent": st.column_config.NumberColumn("TM (%)", min_value=0.0, max_value=100.0, format="%.1f"),
            "NEL": st.column_config.NumberColumn("NEL (MJ/kg)", min_value=0.0, max_value=12.0, format="%.2f"),
            "XP": st.column_config.NumberColumn("XP (g/kg)", min_value=0, max_value=600, format="%d"),
            "nXP": st.column_config.NumberColumn("nXP (g/kg)", min_value=0, max_value=500, format="%d"),
            "RNB": st.column_config.NumberColumn("RNB (g/kg)", min_value=-50.0, max_value=50.0, format="%.1f"),
            "NDF": st.column_config.NumberColumn("NDF (g/kg)", min_value=0, max_value=800, format="%d"),
            "uNDF240": st.column_config.NumberColumn("uNDF240 (g/kg)", min_value=0, max_value=400, format="%d"),
            "peNDF": st.column_config.NumberColumn("peNDF (g/kg)", min_value=0, max_value=800, format="%d"),
            "Staarke": st.column_config.NumberColumn("Stärke (g/kg)", min_value=0, max_value=800, format="%d"),
        },
        use_container_width=True,
        hide_index=True,
        key="editor"
    )

    st.session_state.active_df = edited_df

    st.divider()

    # 3. Nährstoffberechnung
    tm_gesamt = 0.0
    fm_gesamt = 0.0
    nel_gesamt = 0.0
    xp_gesamt_g = 0.0
    nxp_gesamt_g = 0.0
    rnb_gesamt_g = 0.0
    ndf_gesamt_g = 0.0
    undf240_gesamt_g = 0.0
    pendf_gesamt_g = 0.0
    staarke_gesamt_g = 0.0

    for index, row in edited_df.iterrows():
        tm_wert = float(row["Menge_kg_TM"] if pd.notnull(row["Menge_kg_TM"]) else 0)
        tm_prozent = float(row["TM_Prozent"] if pd.notnull(row["TM_Prozent"]) else 0)
        
        if tm_prozent == 0:
            fm = tm_wert
            tm = 0.0
        else:
            tm = tm_wert
            fm = tm / (tm_prozent / 100.0)
        
        tm_gesamt += tm
        fm_gesamt += fm
        
        nel_gesamt += tm * float(row["NEL"] if pd.notnull(row["NEL"]) else 0)
        xp_gesamt_g += tm * float(row["XP"] if pd.notnull(row["XP"]) else 0)
        nxp_gesamt_g += tm * float(row["nXP"] if pd.notnull(row["nXP"]) else 0)
        rnb_gesamt_g += tm * float(row["RNB"] if pd.notnull(row["RNB"]) else 0)
        ndf_gesamt_g += tm * float(row["NDF"] if pd.notnull(row["NDF"]) else 0)
        undf240_gesamt_g += tm * float(row["uNDF240"] if pd.notnull(row["uNDF240"]) else 0)
        pendf_gesamt_g += tm * float(row["peNDF"] if pd.notnull(row["peNDF"]) else 0)
        staarke_gesamt_g += tm * float(row["Staarke"] if pd.notnull(row["Staarke"]) else 0)

    if tm_gesamt > 0:
        nel_dichte = nel_gesamt / tm_gesamt
        nxp_dichte = nxp_gesamt_g / tm_gesamt
        pendf_dichte = pendf_gesamt_g / tm_gesamt
        staarke_dichte = staarke_gesamt_g / tm_gesamt
        tm_gehalt_tmr = (tm_gesamt / fm_gesamt * 100.0) if fm_gesamt > 0 else 0.0
        
        undf240_kg = undf240_gesamt_g / 1000.0
        undf240_prozent_kg = (undf240_kg / gewicht) * 100.0
    else:
        nel_dichte = nxp_dichte = pendf_dichte = staarke_dichte = tm_gehalt_tmr = undf240_prozent_kg = 0.0

    st.header("3. Ergebnisse pro Kuh & Tag")

    r1_1, r1_2, r1_3, r1_4, r1_5 = st.columns(5)
    r1_1.metric("Gesamt-TM", f"{tm_gesamt:.2f} kg TM")
    r1_2.metric("Errechnete FM", f"{fm_gesamt:.2f} kg FM")
    r1_3.metric("TM-Gehalt TMR", f"{tm_gehalt_tmr:.1f} %")
    r1_4.metric("NEL-Dichte", f"{nel_dichte:.2f} MJ/kg TM")
    r1_5.metric("nXP gesamt", f"{nxp_gesamt_g:.0f} g/Tag")

    r2_1, r2_2, r2_3, r2_4, r2_5 = st.columns(5)
    r2_1.metric("RNB gesamt", f"{rnb_gesamt_g:+.1f} g/Tag")
    r2_2.metric("peNDF (Struktur)", f"{pendf_dichte:.1f} g/kg TM")
    r2_3.metric("uNDF240 % KG", f"{undf240_prozent_kg:.2f} %")
    r2_4.metric("Stärke-Dichte", f"{staarke_dichte:.1f} g/kg TM")
    r2_5.metric("NEL gesamt", f"{nel_gesamt:.1f} MJ")

    st.divider()

    st.subheader("🔍 Praxis-Check")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        if rnb_gesamt_g < 0:
            st.warning(f"⚠️ **RNB negativ ({rnb_gesamt_g:.1f} g):** Stickstoffmangel im Pansen.")
        else:
            st.success(f"✅ **RNB im Zielbereich ({rnb_gesamt_g:.1f} g).**")
        if undf240_prozent_kg > 0.40:
            st.error(f"🛑 **uNDF240 zu hoch ({undf240_prozent_kg:.2f} % des KG):** Pansenüberfüllung!")
        else:
            st.success(f"✅ **Pansenfüllung im Optimum.**")

    with col_w2:
        if pendf_dichte < 190 and tm_gesamt > 0:
            st.warning(f"⚠️ **peNDF niedrig ({pendf_dichte:.1f} g/kg TM):** SARA-Risiko.")
        else:
            st.success(f"✅ **peNDF ausreichend.**")
        if tm_gehalt_tmr < 38.0 and tm_gesamt > 0:
            st.warning(f"⚠️ **TMR sehr nass ({tm_gehalt_tmr:.1f} % TM).**")
        elif tm_gehalt_tmr > 55.0 and tm_gesamt > 0:
            st.warning(f"⚠️ **TMR sehr trocken ({tm_gehalt_tmr:.1f} % TM):** Selektionsgefahr.")
        else:
            st.success(f"✅ **TM-Gehalt der TMR optimal.**")


# =========================================================
# SEITE 2: LADELISTE FÜR DEN FUTTERMISCHWAGEN
# =========================================================
elif page == "🚚 Ladeliste Mischwagen":
    st.title("🚚 Ladeliste für den Futtermischwagen")
    st.caption(f"Aktuell geladene Ration: **{st.session_state.current_ration_name}**")

    df_futter = st.session_state.get("active_df", st.session_state.initial_df)

    # Eingaben für Herde & Fütterungsaufteilung
    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    with col_l1:
        kuh_anzahl = st.number_input("Anzahl Kühe in der Gruppe", value=120, step=1, min_value=1)
    with col_l2:
        zuschlag = st.number_input("Sicherheitszuschlag (%)", value=2.0, step=0.5, min_value=0.0)
    with col_l3:
        fuetterungen_tag = st.number_input("Fütterungen pro Tag", value=2, min_value=1, max_value=6, step=1)
    with col_l4:
        if fuetterungen_tag > 1:
            anteil_prozent = st.number_input("Anteil DIESER Mischung (%)", value=round(100.0 / fuetterungen_tag, 1), step=5.0, min_value=1.0, max_value=100.0)
        else:
            anteil_prozent = 100.0

    # Faktor für die Mischerladung
    kuh_faktor_mischung = kuh_anzahl * (1.0 + (zuschlag / 100.0)) * (anteil_prozent / 100.0)
    kuh_faktor_tag = kuh_anzahl * (1.0 + (zuschlag / 100.0))

    st.info(f"💡 **Mischauftrag:** Berechnet für **{kuh_faktor_mischung:.1f} Kuh-Portionen** ({anteil_prozent:.1f}% der Tagesration für {kuh_anzahl} Kühe inkl. {zuschlag}% Zuschlag).")

    st.divider()

    ladeliste = []
    kumuliert_fm = 0.0
    gesamt_tm_mischung = 0.0

    for index, row in df_futter.iterrows():
        tm_wert = float(row.get("Menge_kg_TM", 0) or 0)
        tm_proz = float(row.get("TM_Prozent", 0) or 0)
        
        if tm_proz == 0:
            fm_kuh_tag = tm_wert
            tm_kuh_tag = 0.0
        else:
            tm_kuh_tag = tm_wert
            fm_kuh_tag = tm_kuh_tag / (tm_proz / 100.0)
        
        # Einwiegemenge für diese spezielle Mischung
        fm_mischung = fm_kuh_tag * kuh_faktor_mischung
        tm_mischung = tm_kuh_tag * kuh_faktor_mischung
        
        kumuliert_fm += fm_mischung
        gesamt_tm_mischung += tm_mischung

        ladeliste.append({
            "Futtermittel": row.get("Name", "Unbenannt"),
            "Typ": row.get("Typ", "Grundfutter"),
            "TM %": f"{tm_proz:.1f} %",
            "kg TM / Kuh (Tag)": round(tm_kuh_tag, 2),
            "kg FM / Kuh (Tag)": round(fm_kuh_tag, 2),
            "EINWIEGEN (kg FM Mischung)": round(fm_mischung, 0),
            "Waage-Stand Kumuliert (kg)": round(kumuliert_fm, 0)
        })

    df_ladeliste = pd.DataFrame(ladeliste)

    st.subheader(f"📋 Ladeliste Einwiege-Reihenfolge ({anteil_prozent:.0f}% Tagesanteil)")
    
    st.dataframe(
        df_ladeliste,
        column_config={
            "EINWIEGEN (kg FM Mischung)": st.column_config.NumberColumn("👉 EINWIEGEN DIESE MISCHUNG (kg FM)", format="%d kg"),
            "Waage-Stand Kumuliert (kg)": st.column_config.NumberColumn("📊 Waage Kumuliert (kg)", format="%d kg"),
        },
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    m1, m2, m3 = st.columns(3)
    m1.metric("Mischwagen Gewicht DIESE Ladung", f"{round(kumuliert_fm, 0):,.0f} kg".replace(",", "."))
    m2.metric("Gesamtgewicht TAG (alle Fütterungen)", f"{round(kumuliert_fm * (100.0 / anteil_prozent), 0):,.0f} kg".replace(",", "."))
    m3.metric("Durchschnittlicher TM-Gehalt", f"{(gesamt_tm_mischung / kumuliert_fm * 100.0 if kumuliert_fm > 0 else 0):.1f} %")
