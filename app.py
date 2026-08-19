import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Rationsrechner Dairy", layout="wide")

st.title("🐄 Rationsberechner (Mit Futtermittel-Speicher)")
st.caption("Änderungen dauerhaft speichern oder als CSV exportieren")

CSV_FILE = "futtermittel.csv"

# ---------------------------------------------------------
# 1. STANDARDFUTTERMITTEL (Falls keine CSV existiert)
# ---------------------------------------------------------
default_data = [
    {"Name": "Gras-Silage 1. Schnitt", "Typ": "Grundfutter", "NEL": 6.4, "XP": 160, "NDF": 450, "Menge_kg_TM": 7.5},
    {"Name": "Mais-Silage", "Typ": "Grundfutter", "NEL": 6.7, "XP": 80, "NDF": 360, "Menge_kg_TM": 6.5},
    {"Name": "NG TMR Raps", "Typ": "Kraftfutter", "NEL": 7.0, "XP": 380, "NDF": 280, "Menge_kg_TM": 2.5},
    {"Name": "NG AF Frey", "Typ": "Kraftfutter", "NEL": 8.1, "XP": 110, "NDF": 120, "Menge_kg_TM": 3.5},
]

# Funktion zum Laden der Daten
def load_data():
    if os.path.exists(CSV_FILE):
        try:
            return pd.read_csv(CSV_FILE)
        except Exception:
            return pd.DataFrame(default_data)
    else:
        return pd.DataFrame(default_data)

# Initialisierung des Datenzustands
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
    nel_bedarf_ziel = 0.293 * gewicht**0.75 + 3.14 * (kgh_ziel / 10)
    st.metric("Orientierung NEL-Bedarf (MJ)", round(nel_bedarf_ziel, 1))

st.divider()

# ---------------------------------------------------------
# 3. INTERAKTIVE TABELLE
# ---------------------------------------------------------
st.header("2. Rationskomponenten & Nährstoffe")

edited_df = st.data_editor(
    st.session_state.df_futter,
    num_rows="dynamic",
    column_config={
        "Name": st.column_config.TextColumn("Futtermittel-Bezeichnung", required=True),
        "Typ": st.column_config.SelectboxColumn("Typ", options=["Grundfutter", "Kraftfutter"], required=True),
        "NEL": st.column_config.NumberColumn("NEL (MJ/kg TM)", min_value=0.0, max_value=12.0, format="%.2f"),
        "XP": st.column_config.NumberColumn("XP (g/kg TM)", min_value=0, max_value=600, format="%d"),
        "NDF": st.column_config.NumberColumn("NDF (g/kg TM)", min_value=0, max_value=800, format="%d"),
        "Menge_kg_TM": st.column_config.NumberColumn("Menge (kg TM/Tag)", min_value=0.0, max_value=30.0, format="%.2f"),
    },
    use_container_width=True,
    hide_index=True,
    key="editor"
)

# ---------------------------------------------------------
# SPEICHER- & VERWALTUNGS-BUTTONS
# ---------------------------------------------------------
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

with col_btn1:
    if st.button("💾 Als Standard speichern", help="Speichert den aktuellen Tabellenstand dauerhaft in der App"):
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
    # CSV-Download-Button für Rations-Sicherungen
    csv_buffer = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Ration als CSV herunterladen",
        data=csv_buffer,
        file_name="meine_ration.csv",
        mime="text/csv"
    )

st.divider()

# ---------------------------------------------------------
# 4. ECHTZEIT-BERECHNUNG DER GESAMTRATION
# ---------------------------------------------------------
tm_gesamt = 0.0
nel_gesamt = 0.0
xp_gesamt_g = 0.0
ndf_gesamt_g = 0.0
ndf_grundfutter_g = 0.0

for index, row in edited_df.iterrows():
    menge = float(row["Menge_kg_TM"] if pd.notnull(row["Menge_kg_TM"]) else 0)
    nel = float(row["NEL"] if pd.notnull(row["NEL"]) else 0)
    xp = float(row["XP"] if pd.notnull(row["XP"]) else 0)
    ndf = float(row["NDF"] if pd.notnull(row["NDF"]) else 0)
    typ = str(row["Typ"]) if pd.notnull(row["Typ"]) else "Grundfutter"

    tm_gesamt += menge
    nel_gesamt += menge * nel
    xp_gesamt_g += menge * xp
    ndf_gesamt_g += menge * ndf

    if typ == "Grundfutter":
        ndf_grundfutter_g += menge * ndf

if tm_gesamt > 0:
    nel_pro_kg_tm = nel_gesamt / tm_gesamt
    xp_pro_kg_tm = xp_gesamt_g / tm_gesamt
    ndf_pro_kg_tm = ndf_gesamt_g / tm_gesamt
    gf_ndf_pro_kg_tm = ndf_grundfutter_g / tm_gesamt
else:
    nel_pro_kg_tm = xp_pro_kg_tm = ndf_pro_kg_tm = gf_ndf_pro_kg_tm = 0.0

# ---------------------------------------------------------
# 5. ERGEBNIS-AUSGABE
# ---------------------------------------------------------
st.header("3. Ergebnisse der Ration")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Gesamt-TM-Aufnahme", f"{tm_gesamt:.2f} kg")
m2.metric("NEL-Dichte", f"{nel_pro_kg_tm:.2f} MJ/kg TM")
m3.metric("Rohprotein (XP)", f"{xp_pro_kg_tm:.1f} g/kg TM")
m4.metric("NDF gesamt", f"{ndf_pro_kg_tm:.1f} g/kg TM")
m5.metric("Grundfutter-NDF", f"{gf_ndf_pro_kg_tm:.1f} g/kg TM")

st.divider()

# Plausibilitäts-Check
st.subheader("🔍 Schnell-Check Plausibilität")
if tm_gesamt > 0:
    if gf_ndf_pro_kg_tm < 220:
        st.warning("⚠️ Grundfutter-NDF liegt unter 220 g/kg TM. Azidose-Risiko beachten!")
    else:
        st.success("✅ Grundfutter-NDF liegt im struktursicheren Bereich (> 220 g/kg TM).")
