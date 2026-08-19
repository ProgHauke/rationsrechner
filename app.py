import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rationsrechner Dairy", layout="wide")

st.title("🐄 Rationsberechner (Flexible Komponenten)")
st.caption("Version mit anpassbarer Futtermittel-Datenbank")

# ---------------------------------------------------------
# 1. INITIALISIERUNG DER FUTTERMITTEL-DATENBANK (Session State)
# ---------------------------------------------------------
# Damit Änderungen im Browser erhalten bleiben, speichern wir die Daten in st.session_state
if "futter_liste" not in st.session_state:
    st.session_state.futter_liste = [
        {"Name": "Gras-Silage", "Typ": "Grundfutter", "NEL": 6.4, "XP": 160, "NDF": 450, "Menge_kg_TM": 7.5},
        {"Name": "Mais-Silage", "Typ": "Grundfutter", "NEL": 6.7, "XP": 80, "NDF": 360, "Menge_kg_TM": 6.5},
        {"Name": "NG TMR Raps", "Typ": "Kraftfutter", "NEL": 7.0, "XP": 380, "NDF": 280, "Menge_kg_TM": 2.5},
        {"Name": "NG AF Frey", "Typ": "Kraftfutter", "NEL": 8.1, "XP": 110, "NDF": 120, "Menge_kg_TM": 3.5},
    ]

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
# 3. VERWALTUNG & BERECHNUNG DER FUTTERMITTEL (Interaktive Tabelle)
# ---------------------------------------------------------
st.header("2. Rationskomponenten & Nährstoffe")
st.info("💡 **Tipp:** Sie können Namen, Nährstoffe (NEL in MJ, XP & NDF in g/kg TM) und Mengen direkt in der Tabelle bearbeiten.")

# Konvertierung in Pandas DataFrame für die interaktive Tabelle
df_futter = pd.DataFrame(st.session_state.futter_liste)

# Interaktive Tabelle (data_editor)
edited_df = st.data_editor(
    df_futter,
    num_rows="dynamic",  # Erlaubt das Hinzufügen und Löschen von Zeilen direkt in der Tabelle
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
)

# Aktualisierung des Session States mit den bearbeiteten Daten
st.session_state.futter_liste = edited_df.to_dict("records")

st.divider()

# ---------------------------------------------------------
# 4. BERECHNUNG DER GESAMTRATION
# ---------------------------------------------------------
tm_gesamt = 0.0
nel_gesamt = 0.0
xp_gesamt_g = 0.0
ndf_gesamt_g = 0.0
ndf_grundfutter_g = 0.0

for row in st.session_state.futter_liste:
    menge = float(row.get("Menge_kg_TM", 0) or 0)
    nel = float(row.get("NEL", 0) or 0)
    xp = float(row.get("XP", 0) or 0)
    ndf = float(row.get("NDF", 0) or 0)
    typ = row.get("Typ", "Grundfutter")

    tm_gesamt += menge
    nel_gesamt += menge * nel
    xp_gesamt_g += menge * xp
    ndf_gesamt_g += menge * ndf

    if typ == "Grundfutter":
        ndf_grundfutter_g += menge * ndf

# Konzentrationen in der Trockenmasse
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
