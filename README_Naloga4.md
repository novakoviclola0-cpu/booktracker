# Naloga 4 – uporaba LLM

Aplikacija BookTracker predlaga tri knjige glede na žanr, vzdušje, dolžino knjige in dodatne želje uporabnika. Pri izbiri upošteva tudi obstoječo knjižnico iz datotek `data/knjige.xml`, `data/avtorji.xml` in `data/branja.xml`.

## Zagon

V mapi projekta:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app_naloga4.py
```

V stranskem meniju vnesemo API ključ iz [Google AI Studio](https://aistudio.google.com/apikey), izberemo želje in kliknemo **Poišči knjige**. Ključa ne shranjujemo v repozitorij.

## Implementacija

- `app_naloga4.py` vsebuje spletni obrazec in prikaz rezultatov.
- `book_llm.py` prebere XML podatke, sestavi prompt, pridobi seznam modelov, pošlje zahtevo ponudniku Gemini in obdela odgovor.
- Prompt nastane iz izbranih vrednosti obrazca, prostega vnosa in podatkov XML. Pri vsakem zahtevku je drugačen glede na te podatke.
- Zahteva uporablja `responseMimeType: application/json` ter `responseSchema`. Odgovor je JSON objekt z natanko tremi knjigami. Podatke pretvorimo v razreda `Priporocila` in `PriporocenaKnjiga`.
- Model ni vnaprej določen: aplikacija preko API-ja pridobi modele, ki podpirajo `generateContent`, ter izbere ustreznega. Če vrne HTTP 404, poskusi naslednjega.

Primer oblike odgovora:

```json
{
  "knjige": [
    {"naslov": "Naslov 1", "avtor": "Avtor 1", "razlog": "Razlog 1"},
    {"naslov": "Naslov 2", "avtor": "Avtor 2", "razlog": "Razlog 2"},
    {"naslov": "Naslov 3", "avtor": "Avtor 3", "razlog": "Razlog 3"}
  ]
}
```

## Preizkus

```powershell
python -m unittest discover -s tests -p "test_naloga4.py"
```

Za dejanski preizkus povezave z Gemini je potreben veljaven API ključ in dostop do storitve.
