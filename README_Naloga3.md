# BookTracker – Naloga 3: Odprti podatki

## Opis

Aplikacija `naloga3.py` prikazuje javne podatke o izposoji knjižničnega gradiva v šolskih knjižnicah v Sloveniji za leta 2006, 2009 in 2012. Podatki so povezani s tematiko projekta BookTracker (knjige in branje).

## Vir podatkov

- OPSI: https://podatki.gov.si/dataset/surs1059411s
- Izvirna datoteka PC-Axis: https://pxweb.stat.si/SiStatData/Resources/PX/Databases/Data/1059411S.PX
- Izdajatelj: Statistični urad Republike Slovenije (SURS).

## Funkcionalnosti

1. Knjižnica `pyaxis` ob zagonu pridobi in prebere podatke iz datoteke PC-Axis (`.PX`).
2. Dva filtra omogočata izbiro vrste gradiva in vrste izposoje. Prvi ima pet razumljivih možnosti, drugi tri.
3. Podatki se filtrirajo in združijo po letih (agregacija).
4. Streamlit prikaže dinamični stolpčni graf, ki se ob spremembi filtrov samodejno posodobi.

**Opomba:** Leposlovje je del kategorije knjig in brošur, zato izbranih kategorij ni smiselno seštevati med seboj.

## Zagon

V korenski mapi projekta BookTracker izvedite:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run naloga3.py
```

Spletna aplikacija se običajno odpre na `http://localhost:8501`. Za pridobivanje podatkov je potrebna internetna povezava.
