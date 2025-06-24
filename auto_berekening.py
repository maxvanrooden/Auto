
import streamlit as st

st.set_page_config(page_title="Auto: Privé vs Zakelijk", layout="centered")

st.title("🚗 Bereken: Auto Privé of Zakelijk Aanschaffen")

# Invoer
aanschafprijs = st.number_input("Aanschafprijs van de auto (incl. btw)", min_value=0.0)
cataloguswaarde = st.number_input("Cataloguswaarde (voor bijtelling)", min_value=0.0)
restwaarde = st.number_input("Geschatte restwaarde na gebruiksduur", min_value=0.0)
gebruiksjaren = st.number_input("Gebruiksduur (in jaren)", min_value=1, step=1, value=5)
bijtelling_percentage = st.number_input("Bijtellingspercentage (%)", min_value=0.0, max_value=25.0, value=22.0)
belastingtarief = st.number_input("Belastingtarief (%)", min_value=0.0, max_value=60.0, value=37.07)
zakelijk_km_per_jaar = st.number_input("Zakelijke kilometers per jaar", min_value=0)
prive_km_per_jaar = st.number_input("Privé kilometers per jaar", min_value=0)
jaarlijkse_kosten = st.number_input("Jaarlijkse kosten (brandstof, onderhoud etc.)", min_value=0.0)
btw_aftrekbaar = st.number_input("Btw-aftrekbaar percentage", min_value=0.0, max_value=100.0, value=100.0)

if st.button("Bereken"):
    # Btw en afschrijving
    btw_bedrag = aanschafprijs * (21 / 121)
    netto_aankoopprijs = aanschafprijs - btw_bedrag
    btw_terug = btw_bedrag * (btw_aftrekbaar / 100)
    afschrijving = (netto_aankoopprijs - restwaarde) / gebruiksjaren

    # Privé
    vergoeding_per_km = 0.23
    prive_totaal_vergoeding = zakelijk_km_per_jaar * vergoeding_per_km * gebruiksjaren
    prive_totaal_kosten = aanschafprijs - restwaarde + jaarlijkse_kosten * gebruiksjaren - prive_totaal_vergoeding

    # Zakelijk
    bijtelling_netto = cataloguswaarde * (bijtelling_percentage / 100) * (belastingtarief / 100)
    totale_bijtelling = bijtelling_netto * gebruiksjaren
    zakelijk_totaal_kosten = afschrijving * gebruiksjaren + jaarlijkse_kosten * gebruiksjaren + totale_bijtelling - btw_terug

    st.subheader("📊 Resultaten")

    st.write(f"**Totale kosten privé:** €{round(prive_totaal_kosten, 2)}")
    st.write(f"**Totale kosten zakelijk:** €{round(zakelijk_totaal_kosten, 2)}")

    verschil = prive_totaal_kosten - zakelijk_totaal_kosten
    if verschil > 0:
        st.success(f"💼 Zakelijk is €{round(verschil, 2)} voordeliger.")
    else:
        st.info(f"🏠 Privé is €{round(-verschil, 2)} voordeliger.")
