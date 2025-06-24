
import streamlit as st
import requests

st.set_page_config(page_title="Auto: Privé vs Zakelijk", layout="centered")

st.title("🚗 Bereken: Auto Privé of Zakelijk Aanschaffen")

def rdw_data_ophalen(kenteken):
    kenteken = kenteken.replace("-", "").upper()
    url = f"https://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken={kenteken}"
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        catalogusprijs = float(data.get('catalogusprijs', 0))
        return catalogusprijs
    return None

def rdw_brandstof_data(kenteken):
    kenteken = kenteken.replace("-", "").upper()
    url = f"https://opendata.rdw.nl/resource/8ys7-d773.json?kenteken={kenteken}"
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        brandstofsoort = data.get('brandstof_omschrijving', '')
        verbruik_stad = float(data.get('brandstofverbruik_stad', 0))
        verbruik_snelweg = float(data.get('brandstofverbruik_snelweg', 0))
        verbruik_gemiddeld = float(data.get('brandstofverbruik_gecombineerd', 0))
        return brandstofsoort, verbruik_gemiddeld
    return None, 0

# Invoer
kenteken_input = st.text_input("Voer kenteken in (bijv. XX999X)")

cataloguswaarde = 0
verbruik_l_per_100km = 0
brandstofprijs = 0

if kenteken_input:
    cataloguswaarde_rdw = rdw_data_ophalen(kenteken_input)
    brandstofsoort, verbruik = rdw_brandstof_data(kenteken_input)

    if cataloguswaarde_rdw:
        st.success(f"📦 RDW Catalogusprijs: €{cataloguswaarde_rdw}")
        cataloguswaarde = cataloguswaarde_rdw
    else:
        st.warning("Kon geen catalogusprijs vinden bij RDW.")

    if brandstofsoort and verbruik > 0:
        st.info(f"⛽ Brandstof: {brandstofsoort}, Verbruik: {verbruik} l/100km")
        verbruik_l_per_100km = verbruik
        # Stel automatisch brandstofprijs in
        if "DIESEL" in brandstofsoort.upper():
            brandstofprijs = 1.80
        elif "ELECTRICITEIT" in brandstofsoort.upper():
            brandstofprijs = 0.30
        else:
            brandstofprijs = 2.10
    else:
        st.warning("Kon geen brandstofgegevens vinden bij RDW.")

aanschafprijs = st.number_input("Aanschafprijs van de auto (incl. btw)", min_value=0.0)
if cataloguswaarde == 0:
    cataloguswaarde = st.number_input("Cataloguswaarde (voor bijtelling)", min_value=0.0)
restwaarde = st.number_input("Geschatte restwaarde na gebruiksduur", min_value=0.0)
gebruiksjaren = st.number_input("Gebruiksduur (in jaren)", min_value=1, step=1, value=5)
bijtelling_percentage = st.number_input("Bijtellingspercentage (%)", min_value=0.0, max_value=25.0, value=22.0)
belastingtarief = st.number_input("Belastingtarief (%)", min_value=0.0, max_value=60.0, value=37.07)
zakelijk_km_per_jaar = st.number_input("Zakelijke kilometers per jaar", min_value=0)
prive_km_per_jaar = st.number_input("Privé kilometers per jaar", min_value=0)
overige_kosten = st.number_input("Overige jaarlijkse kosten (verzekering, onderhoud etc.)", min_value=0.0)
btw_aftrekbaar = st.number_input("Btw-aftrekbaar percentage", min_value=0.0, max_value=100.0, value=100.0)

if st.button("Bereken"):
    # Btw en afschrijving
    btw_bedrag = aanschafprijs * (21 / 121)
    netto_aankoopprijs = aanschafprijs - btw_bedrag
    btw_terug = btw_bedrag * (btw_aftrekbaar / 100)
    afschrijving = (netto_aankoopprijs - restwaarde) / gebruiksjaren

    # Brandstofkosten berekenen
    totaal_km_per_jaar = zakelijk_km_per_jaar + prive_km_per_jaar
    jaarlijkse_brandstofkosten = 0
    if verbruik_l_per_100km > 0:
        jaarlijkse_brandstofkosten = (verbruik_l_per_100km / 100) * totaal_km_per_jaar * brandstofprijs

    totale_kosten_per_jaar = jaarlijkse_brandstofkosten + overige_kosten

    # Privé
    vergoeding_per_km = 0.23
    prive_totaal_vergoeding = zakelijk_km_per_jaar * vergoeding_per_km * gebruiksjaren
    prive_totaal_kosten = aanschafprijs - restwaarde + totale_kosten_per_jaar * gebruiksjaren - prive_totaal_vergoeding

    # Zakelijk
    bijtelling_netto = cataloguswaarde * (bijtelling_percentage / 100) * (belastingtarief / 100)
    totale_bijtelling = bijtelling_netto * gebruiksjaren
    zakelijk_totaal_kosten = afschrijving * gebruiksjaren + totale_kosten_per_jaar * gebruiksjaren + totale_bijtelling - btw_terug

    st.subheader("📊 Resultaten")

    st.write(f"**Totale kosten privé:** €{round(prive_totaal_kosten, 2)}")
    st.write(f"**Totale kosten zakelijk:** €{round(zakelijk_totaal_kosten, 2)}")

    verschil = prive_totaal_kosten - zakelijk_totaal_kosten
    if verschil > 0:
        st.success(f"💼 Zakelijk is €{round(verschil, 2)} voordeliger.")
    else:
        st.info(f"🏠 Privé is €{round(-verschil, 2)} voordeliger.")
