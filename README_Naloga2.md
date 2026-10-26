# BookTracker – Naloga 2: Parser

## Opis

Program `parser.py` je spletni razčlenjevalnik, napisan v Pythonu. S spletne strani [Books to Scrape](https://books.toscrape.com/) pridobi podatke o knjigah neposredno iz HTML-strani (ne prek API-ja) ter jih shrani v datoteko JSON za uporabo v projektu BookTracker.

Stran je namenjena preizkušanju spletnega razčlenjevanja; njene cene in ocene so izmišljene in ne predstavljajo dejanskih podatkov o knjigah. Ocene s strani niso osebne ocene uporabnika aplikacije BookTracker.

## Pridobljeni podatki

- `naslov`: naslov knjige
- `cena_GBP`: cena knjige v britanskih funtih
- `ocena_spletne_strani`: ocena zvezdic (1–5)
- `na_zalogi`: razpoložljivost knjige (`true` ali `false`)
- `povezava`: URL podrobnosti knjige
- `naslovnica`: URL slike naslovnice

## Zagon

Potreben je Python 3.9 ali novejši in internetna povezava.

Datoteke `parser.py`, `requirements.txt` in `README_Naloga2.md` postavite v korensko mapo obstoječega repozitorija BookTracker (poleg datoteke `main.py`). Nato v terminalu v tej mapi izvedite:

```bash
python -m pip install -r requirements.txt
python parser.py
```

Program prenese začetno stran s 20 knjigami, iz HTML-ja izlušči podatke in ustvari/posodobi `data/knjige_parser.json`. Zapis je strukturiran kot objekt s polji `vir`, `stevilo_knjig` in `knjige` (seznam knjig). Podatke bo mogoče uporabiti pri končnem prikazu knjig v projektu BookTracker.

## Postopek

1. `requests.get()` prenese HTML spletne strani preko HTTPS.
2. `BeautifulSoup` poišče vse elemente `article.product_pod`.
3. Iz vsakega elementa se preberejo podatki o knjigi.
4. Povezave do knjig in naslovnic se pretvorijo v absolutne URL-je.
5. Modul `json` shrani rezultate v `data/knjige_parser.json`.

## Oddaja

Glavna izvorna koda za nalogo je `parser.py`. Priporočeno je priložiti tudi `requirements.txt`, `README_Naloga2.md` in JSON, ki ga program ustvari po uspešnem zagonu.
