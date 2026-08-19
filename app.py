import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Rationsrechner Dairy", layout="wide")

st.title("🐄 Rationsberechner (Praxis-Version mit FM & TM %)")
st.caption("Eingabe über Frischmasse (FM) und Trockenmasse-Gehalt (TM %)")

CSV_FILE = "futtermittel.csv"

# ---------------------------------------------------------
# 1. STANDARDFUTTERMITTEL (Inklusive TM % und kg FM)
# ---------------------------------------------------------
default_data = [
    {
        "Name": "Gras-Silage 1. Schnitt", "Typ": "Grundfutter", 
        "TM_Prozent": 35.0, "Menge_kg_FM": 21.43,
        "NEL": 6.4, "XP": 160, "nXP": 140, "RNB": 3.2, "NDF": 450, "uNDF240": 160, "peNDF": 380, "Staarke": 20
    },
    {
        "Name": "Mais-Silage", "Typ": "Grundfutter", 
        "TM_Prozent": 33.0, "Menge_kg_FM": 19.70,
        "NEL": 6.7, "XP": 80, "nXP": 135, "RNB": -8.8, "NDF": 360, "uNDF240": 110, "peNDF": 290, "Staarke": 320
    },
    {
        "Name": "NG TMR Raps", "Typ": "Kraftfutter", 
        "TM_Prozent": 88.0, "Menge_kg_FM": 2.84,
        "NEL": 7.0, "XP": 380, "nXP": 240, "RNB": 22.4, "NDF": 280, "uNDF240": 120, "peNDF": 100, "Staarke": 30
    },
    {
        "Name": "NG AF Frey", "Typ": "Kraftfutter", 
        "TM_Prozent": 88.0, "Menge_kg_FM": 3.98,
        "NEL": 8.1, "XP": 110, "nXP": 165, "RNB": -8.8, "NDF": 120, "uNDF240": 30, "peNDF": 40, "Staarke": 520
    },
]

def load_data():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            for col in default_data[0].keys():
                if col not in df.columns:
                    return pd.DataFrame(default_data)
            return df
        except Exception:
            return pd.DataFrame(default_data)
    else:
        return pd.DataFrame(default_data)

if "df_futter" not in st.session_state:
    st.session_state.df_futter = load_data()

# ---------------------------------------------------------
# 2. TIERDATEN & ZIELWERTE
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 3. INTERAKTIVE TABELLE
# ---------------------------------------------------------
st.header("2. Rationskomponenten & Nährstoffe")

edited_df = st.data_editor(
    st.session_state.df_futter,
    num_rows="dynamic",
    column_config={
        "Name": st.column_config.TextColumn("Bezeichnung", required=True),
        "Typ": st.column_config.SelectboxColumn("Typ", options=["Grundfutter", "Kraftfutter"], required=True),
        "TM_Prozent": st.column_config.NumberColumn("TM (%)", min_value=10.0, max_value=100.0, format="%.1f"),
        "Menge_kg_FM": st.column_config.NumberColumn("Menge (kg FM)", min_value=0.0, max_value=60.0, format="%.2f"),
        "NEL": st.column_config.NumberColumn("NEL (MJ/kg TM)", min_value=0.0, max_value=12.0, format="%.2f"),
        "XP": st.column_config.NumberColumn("XP (g/kg TM)", min_value=0, max_value=600, format="%d"),
        "nXP": st.column_config.NumberColumn("nXP (g/kg TM)", min_value=0, max_value=500, format="%d"),
        "RNB": st.column_config.NumberColumn("RNB (g/kg TM)", min_value=-50.0, max_value=50.0, format="%.1f"),
        "NDF": st.column_config.NumberColumn("NDF (g/kg TM)", min_value=0, max_value=800, format="%d"),
        "uNDF240": st.column_config.NumberColumn("uNDF240 (g/kg TM)", min_value=0, max_value=400, format="%d"),
        "peNDF": st.column_config.NumberColumn("peNDF (g/kg TM)", min_value=0, max_value=800, format="%d"),
        "Staarke": st.column_config.NumberColumn("Stärke (g/kg TM)", min_value=0, max_value=800, format="%d"),
    },
    use_container_width=True,
    hide_index=True,
    key="editor"
)

# Speicherverwaltung
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
with col_btn1:
    if st.button("💾 Als Standard speichern"):
        edited_df.to_csv(CSV_FILE, index=False)
        st.session_state.df_futter = edited_df
        st.success("Erfolgreich gespeichert!")

with col_btn2:
    if st.button("🔄 Auf Standard zurücksetzen"):
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        st.session_state.df_futter = pd.DataFrame(default_data)
        st.rerun()

with col_btn3:
    csv_buffer = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Ration als CSV herunterladen", csv_buffer, "meine_ration.csv", "text/csv")

st.divider()

# ---------------------------------------------------------
# 4. BERECHNUNG DER GESAMTRATION (Umrechnung FM -> TM)
# ---------------------------------------------------------
fm_gesamt = 0.0
tm_gesamt = 0.0
nel_gesamt = 0.0
xp_gesamt_g = 0.0
nxp_gesamt_g = 0.0
rnb_gesamt_g = 0.0
ndf_gesamt_g = 0.0
undf240_gesamt_g = 0.0
pendf_gesamt_g = 0.0
staarke_gesamt_g = 0.0
ndf_grundfutter_g = 0.0

for index, row in edited_df.iterrows():
    fm = float(row["Menge_kg_FM"] if pd.notnull(row["Menge_kg_FM"]) else 0)
    tm_prozent = float(row["TM_Prozent"] if pd.notnull(row["TM_Prozent"]) else 100.0)
    
    # Trockenmasse der Komponente berechnen
    tm = fm * (tm_prozent / 100.0)
    
    fm_gesamt += fm
    tm_gesamt += tm
    
    nel_gesamt += tm * float(row["NEL"] if pd.notnull(row["NEL"]) else 0)
    xp_gesamt_g += tm * float(row["XP"] if pd.notnull(row["XP"]) else 0)
    nxp_gesamt_g += tm * float(row["nXP"] if pd.notnull(row["nXP"]) else 0)
    rnb_gesamt_g += tm * float(row["RNB"] if pd.notnull(row["RNB"]) else 0)
    ndf_gesamt_g += tm * float(row["NDF"] if pd.notnull(row["NDF"]) else 0)
    undf240_gesamt_g += tm * float(row["uNDF240"] if pd.notnull(row["uNDF240"]) else 0)
    pendf_gesamt_g += tm * float(row["peNDF"] if pd.notnull(row["peNDF"]) else 0)
    staarke_gesamt_g += tm * float(row["Staarke"] if pd.notnull(row["Staarke"]) else 0)
    
    if str(row["Typ"]) == "Grundfutter":
        ndf_grundfutter_g += tm * float(row["NDF"] if pd.notnull(row["NDF"]) else 0)

if tm_gesamt > 0:
    nel_dichte = nel_gesamt / tm_gesamt
    xp_dichte = xp_gesamt_g / tm_gesamt
    nxp_dichte = nxp_gesamt_g / tm_gesamt
    ndf_dichte = ndf_gesamt_g / tm_gesamt
    pendf_dichte = pendf_gesamt_g / tm_gesamt
    staarke_dichte = staarke_gesamt_g / tm_gesamt
    gf_ndf_dichte = ndf_grundfutter_g / tm_gesamt
    tm_gehalt_ration = (tm_gesamt / fm_gesamt * 100.0) if fm_gesamt > 0 else 0.0
    
    undf240_kg = undf240_gesamt_g / 1000.0
    undf240_prozent_kg = (undf240_kg / gewicht) * 100.0
else:
    nel_dichte = xp_dichte = nxp_dichte = ndf_dichte = pendf_dichte = staarke_dichte = gf_ndf_dichte = tm_gehalt_ration = undf240_prozent_kg = 0.0

# ---------------------------------------------------------
# 5. ERGEBNIS-AUSGABE
# ---------------------------------------------------------
st.header("3. Ergebnisse der Ration")

# Reihe 1: Massen & Energie
r1_1, r1_2, r1_3, r1_4, r1_5 = st.columns(5)
r1_1.metric("Gesamt-FM", f"{fm_gesamt:.2f} kg FM")
r1_2.metric("Gesamt-TM", f"{tm_gesamt:.2f} kg TM")
r1_3.metric("TM-Gehalt Ration", f"{tm_gehalt_ration:.1f} %")
r1_4.metric("NEL-Dichte", f"{nel_dichte:.2f} MJ/kg TM")
r1_5.metric("NEL gesamt", f"{nel_gesamt:.1f} MJ")

# Reihe 2: Protein & Struktur
r2_1, r2_2, r2_3, r2_4, r2_5 = st.columns(5)
r2_1.metric("nXP gesamt", f"{nxp_gesamt_g:.0f} g/Tag")
r2_2.metric("RNB gesamt", f"{rnb_gesamt_g:+.1f} g/Tag")
r2_3.metric("peNDF (Struktur)", f"{pendf_dichte:.1f} g/kg TM")
r2_4.metric("uNDF240 % KG", f"{undf240_prozent_kg:.2f} %")
r2_5.metric("Stärke-Dichte", f"{staarke_dichte:.1f} g/kg TM")

st.divider()

# ---------------------------------------------------------
# 6. PRAXIS-CHECK
# ---------------------------------------------------------
st.subheader("🔍 Praxis-Check & Warnsignale")

col_w1, col_w2 = st.columns(2)

with col_w1:
    if rnb_gesamt_g < 0:
        st.warning(f"⚠️ **RNB negativ ({rnb_gesamt_g:.1f} g/Tag):** Stickstoffmangel im Pansen!")
    elif rnb_gesamt_g > 50:
        st.info(f"ℹ️ **RNB hoch ({rnb_gesamt_g:.1f} g/Tag):** Hoher NH3-Überschuss.")
    else:
        st.success(f"✅ **RNB im Zielbereich ({rnb_gesamt_g:.1f} g/Tag).**")

    if undf240_prozent_kg > 0.40:
        st.error(f"🛑 **uNDF240 zu hoch ({undf240_prozent_kg:.2f} % des KG):** Pansenüberfüllung droht!")
    else:
        st.success(f"✅ **uNDF240 im Zielbereich.**")

with col_w2:
    if pendf_dichte < 190 and tm_gesamt > 0:
        st.warning(f"⚠️ **peNDF niedrig ({pendf_dichte:.1f} g/kg TM):** SARA- / Azidose-Risiko.")
    else:
        st.success(f"✅ **peNDF ausreichend ({pendf_dichte:.1f} g/kg TM).**")

    if tm_gehalt_ration < 38.0 and tm_gesamt > 0:
        st.warning(f"⚠️ **Ration sehr nass ({tm_gehalt_ration:.1f} % TM):** Kann Futteraufnahme hemmen.")
    elif tm_gehalt_ration > 55.0 and tm_gesamt > 0:
        st.warning(f"⚠️ **Ration sehr trocken ({tm_gehalt_ration:.1f} % TM):** Selektionsrisiko am Futtertisch.")
    else:
        st.success(f"✅ **TM-Gehalt der TMR optimal ({tm_gehalt_ration:.1f} % TM).**")
