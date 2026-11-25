# Naloga 7 – Poimenovane cevi

BookTracker uporablja poimenovano cev za komunikacijo med aplikacijo Streamlit in ločenim strežniškim procesom. Strežnik uporablja obstoječe podatke XML in vrne analizo knjig glede na status branja, najmanjše število strani in najmanjšo oceno. Aplikacija prikaže število knjig, skupno število strani, povprečno oceno ter tabelo zadetkov.

## Zagon

V mapi projekta namestimo knjižnice:

```powershell
python -m pip install -r requirements.txt
```

V prvem terminalu zaženemo strežnik za poimenovano cev:

```powershell
python pipe_server.py
```

V drugem terminalu zaženemo aplikacijo:

```powershell
python -m streamlit run app_naloga5.py
```

V razdelku **Analiza knjižnice prek poimenovane cevi** izberemo status branja, najmanjše število strani in najmanjšo oceno ter kliknemo **Analiziraj knjižnico**. Status je skupen z izbiro na vrhu aplikacije.

Običajne funkcije iz naloge 5 še vedno uporabljajo gRPC. Zanje lahko v tretjem terminalu zaženemo `python grpc_server.py`. Za analizo prek poimenovane cevi gRPC strežnik ni potreben.

## Preverjanje nedosegljivega strežnika

Najprej kliknemo **Analiziraj knjižnico** brez zagnanega `pipe_server.py`. Aplikacija med čakanjem ostane odzivna in po omejenem številu poskusov prikaže opozorilo. Če strežnik zaženemo med ponovnimi poskusi, aplikacija samodejno pridobi rezultat.

V Windows se uporablja poimenovana cev `\\.\pipe\booktracker`. Na Linux/macOS se za lokalni preizkus uporablja Unix vtičnica `/tmp/booktracker_naloga7.sock`.
