import os

import streamlit as st

from book_llm import NapakaPriporocil, preberi_knjiznico, sestavi_prompt, pridobi_priporocila


st.set_page_config(page_title="BookTracker", layout="centered")

st.title("BookTracker")
st.subheader("Priporočila knjig")

with st.sidebar:
    st.subheader("Nastavitve")
    api_kljuc = st.text_input(
        "API ključ",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
    )

try:
    knjiznica = preberi_knjiznico()
except (OSError, ValueError) as napaka:
    st.error(f"Podatkov o knjigah ni mogoče prebrati: {napaka}")
    st.stop()

with st.form("priporocila"):
    zanr = st.selectbox("Žanr", [
        "Fantazija", "Kriminalka", "Romantika", "Znanstvena fantastika",
        "Zgodovinski roman", "Drama", "Klasika", "Poljubno",
    ])
    vzdusje = st.selectbox("Vzdušje", [
        "Napeto", "Sproščujoče", "Skrivnostno", "Navdihujoče", "Čustveno",
    ])
    dolzina = st.selectbox("Dolžina knjige", [
        "Kratka (do 200 strani)",
        "Srednja (200–400 strani)",
        "Dolga (nad 400 strani)",
        "Ni pomembno",
    ])
    dodatno = st.text_input("Dodatne želje", placeholder="Npr. brez žalostnega konca", max_chars=200)
    poslano = st.form_submit_button("Poišči knjige", type="primary")

if poslano:
    if not api_kljuc.strip():
        st.warning("V nastavitvah vnesi API ključ.")
        st.stop()

    prompt = sestavi_prompt(zanr, vzdusje, dolzina, dodatno, knjiznica)
    try:
        with st.spinner("Iščem knjige ..."):
            priporocila = pridobi_priporocila(api_kljuc.strip(), prompt)
    except NapakaPriporocil as napaka:
        st.error(str(napaka))
    else:
        st.divider()
        st.subheader("Predlogi za branje")
        for knjiga in priporocila.knjige:
            with st.container(border=True):
                st.markdown(f"**{knjiga.naslov}**")
                st.caption(knjiga.avtor)
                st.write(knjiga.razlog)
