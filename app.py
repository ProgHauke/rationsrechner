import streamlit as st

# Seite konfigurieren
st.set_page_config(page_title="Rationsrechner Dairy", layout="wide")

st.title("🐄 Rationsberechner (Basis-Version)")
st.caption("Prototyp zur Prüfung der Rechenlogik")

# ---------------------------------------------------------
# 1. TIERDATEN & ZIELWERTE
# ---------------------------------------------------------
st.header("1. Tierdaten & Ziel-Bedarf")
col_t1, col_t2 = st.columns(2)

with col_t1:
    kgh_ziel = st.number_input("Ziel-Milchleistung (kg ECM/Tag)", value=38.0, step=0.5)
    gewicht = st.number_input("Körpergewicht der Kuh (kg)", value=680, step=10)

with col_t2:
    # Grobe Orientierungswerte für den Plausibilitäts-Check
    nel_bedarf_ziel = 0.293 * gewicht**0.75 + 3.14 * (kgh_ziel / 10)  # Orientierungsformel
    st.metric("Orientierung NEL-Bedarf (MJ)", round(nel_bedarf_ziel, 1))

st.divider()

# ---------------------------------------------------------
# 2. FUTTERMITTEL-EINGABE (TM-Aufnahme in kg)
# ---------------------------------------------------------
st.header("2. Rationskomponenten (kg TM / Tag)")

col_f1, col_f2 = st.columns(2)

with col_f1:
    st.subheader("🌾 Grundfutter")
    tm_grassilage = st.number_input("Gras-Silage (kg TM)", value=7.5, step=0.5)
    tm_maissilage = st.number_input("Mais-Silage (kg TM)", value=6.5, step=0.5)

with col_f2:
    st.subheader("🌽 Kraftfutter")
    tm_rapsschrot = st.number_input("Rapsextraktionsschrot (kg TM)", value=2.5, step=0.5)
    tm_getreide = st.number_input("Körnermais / Getreide (kg TM)", value=3.5, step=0.5)

# Gesamte TM-Aufnahme
tm_gesamt = tm_grassilage + tm_maissilage + tm_rapsschrot + tm_getreide

st.divider()

# ---------------------------------------------------------
# 3. NÄHRSTOFFWERTE DER FUTTERMITTEL (Matrix)
# NEL in MJ/kg TM, XP & NDF in g/kg TM
# ---------------------------------------------------------
futter_daten = {
    "Gras-Silage":    {"NEL": 6.4, "XP": 160, "NDF": 450, "is_grundfutter": True},
    "Mais-Silage":    {"NEL": 6.7, "XP": 80,  "NDF": 360, "is_grundfutter": True},
    "Raps-Schrot":    {"NEL": 7.0, "XP": 380, "NDF": 280, "is_grundfutter": False},
    "Getreide-Mix":   {"NEL": 8.1, "XP": 110, "NDF": 120, "is_grundfutter": False},
}

# ---------------------------------------------------------
# 4. BERECHNUNG DER GESAMTRATION
# ---------------------------------------------------------
nel_gesamt = (
    tm_grassilage * futter_daten["Gras-Silage"]["NEL"] +
    tm_maissilage * futter_daten["Mais-Silage"]["NEL"] +
    tm_rapsschrot * futter_daten["Raps-Schrot"]["NEL"] +
    tm_getreide   * futter_daten["Getreide-Mix"]["NEL"]
)

xp_gesamt_g = (
    tm_grassilage * futter_daten["Gras-Silage"]["XP"] +
    tm_maissilage * futter_daten["Mais-Silage"]["XP"] +
    tm_rapsschrot * futter_daten["Raps-Schrot"]["XP"] +
    tm_getreide   * futter_daten["Getreide-Mix"]["XP"]
)

ndf_gesamt_g = (
    tm_grassilage * futter_daten["Gras-Silage"]["NDF"] +
    tm_maissilage * futter_daten["Mais-Silage"]["NDF"] +
    tm_rapsschrot * futter_daten["Raps-Schrot"]["NDF"] +
    tm_getreide   * futter_daten["Getreide-Mix"]["NDF"]
)

# NDF nur aus dem Grundfutter
ndf_grundfutter_g = (
    tm_grassilage * futter_daten["Gras-Silage"]["NDF"] +
    tm_maissilage * futter_daten["Mais-Silage"]["NDF"]
)

# Konzentrationen in der Trockenmasse berechnen
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
m1.metric("Gesamt-TM-Aufnahme", f"{tm_gesamt:.1f} kg")
m2.metric("NEL-Dichte", f"{nel_pro_kg_tm:.2f} MJ/kg TM")
m3.metric("Rohprotein (XP)", f"{xp_pro_kg_tm:.1f} g/kg TM")
m4.metric("NDF gesamt", f"{ndf_pro_kg_tm:.1f} g/kg TM")
m5.metric("Grundfutter-NDF", f"{gf_ndf_pro_kg_tm:.1f} g/kg TM")

st.divider()

# Plausibilitäts-Warnungen
st.subheader("🔍 Schnell-Check Plausibilität")
if gf_ndf_pro_kg_tm < 220:
    st.warning("⚠️ Grundfutter-NDF liegt unter 220 g/kg TM. Azidose-Risiko beachten!")
else:
    st.success("✅ Grundfutter-NDF liegt im struktursicheren Bereich (> 220 g/kg TM).")
