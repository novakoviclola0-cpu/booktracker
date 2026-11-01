"""Naloga 3: prikaz odprtih podatkov o izposoji knjižničnega gradiva (PC-Axis)."""

import pandas as pd
import streamlit as st
from pyaxis import pyaxis

VIR_PX = "https://pxweb.stat.si/SiStatData/Resources/PX/Databases/Data/1059411S.PX"
VIR_OPSI = "https://podatki.gov.si/dataset/surs1059411s"

st.set_page_config(page_title="Izposoja knjižničnega gradiva")
st.title("Izposoja knjižničnega gradiva")
st.write("Šolske knjižnice v Sloveniji (2006, 2009, 2012).")

try:
    # Podatke v obliki PC-Axis pridobimo iz izvirnega vira ob zagonu aplikacije.
    df = pyaxis.parse(VIR_PX, encoding="ISO-8859-2", timeout=20)["DATA"].copy()
    leto = next(c for c in df.columns if "LETO" in c.upper())
    gradivo = next(c for c in df.columns if "GRADIVA" in c.upper())
    izposoja = next(c for c in df.columns if "IZPOSOJE" in c.upper())
except Exception as napaka:
    st.error(f"Podatkov PC-Axis ni mogoče naložiti: {napaka}")
    st.stop()


def najdi(vrednosti, pogoj):
    """Poišče izvirno vrednost, četudi so šumniki v datoteki napačno kodirani."""
    return next((v for v in vrednosti if pogoj(str(v).lower())), None)


g = df[gradivo].dropna().unique().tolist()
i = df[izposoja].dropna().unique().tolist()

# Prikazujemo le smiselne skupne kategorije, ne vseh podkategorij.
vrste_gradiva = {
    "Vse knjižnično gradivo": najdi(g, lambda s: "skupaj" in s and "knjig in" not in s),
    "Knjige in brošure": najdi(g, lambda s: "knjig in" in s),
    "Leposlovje": najdi(g, lambda s: "leposlov" in s),
    "Serijske publikacije": najdi(g, lambda s: "serijsk" in s),
    "Neknjižno gradivo": najdi(g, lambda s: "neknji" in s),
}
vrste_izposoje = {
    "Skupna izposoja": najdi(i, lambda s: "skupaj" in s),
    "Izposoja na dom": najdi(i, lambda s: "na dom" in s and "skupaj" not in s
                              and "dijakom" not in s and "drugim" not in s),
    "Izposoja v knjižnici": najdi(i, lambda s: "v knji" in s and "skupaj" not in s
                                   and "dijakom" not in s and "drugim" not in s),
}

if any(v is None for v in (*vrste_gradiva.values(), *vrste_izposoje.values())):
    st.error("V izvirni datoteki PC-Axis niso na voljo vse pričakovane kategorije.")
    st.stop()

izbrano_gradivo = st.selectbox("Vrsta gradiva", list(vrste_gradiva), index=1)
izbrana_izposoja = st.selectbox("Vrsta izposoje", list(vrste_izposoje))

# Filtriranje po obeh izbirah in agregacija po letih.
izbrani = df[
    (df[gradivo] == vrste_gradiva[izbrano_gradivo])
    & (df[izposoja] == vrste_izposoje[izbrana_izposoja])
].copy()
izbrani["DATA"] = pd.to_numeric(
    izbrani["DATA"].astype(str).str.replace(",", ".", regex=False),
    errors="coerce",
)
po_letih = (izbrani.groupby(leto, as_index=False)["DATA"]
            .sum(min_count=1).dropna().sort_values(leto))

if po_letih.empty:
    st.warning("Za izbrani kategoriji ni podatkov.")
else:
    st.subheader("Število izposojenih enot po letih")
    st.bar_chart(po_letih.set_index(leto)["DATA"])

st.markdown(f"Vir: [OPSI – Odprti podatki Slovenije]({VIR_OPSI}) (SURS, PC-Axis).")
