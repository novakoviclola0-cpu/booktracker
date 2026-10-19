# BookTracker - Naloga 1: XML in JSON

## Opis projekta

Projekt je poenostavljen primer aplikacije BookTracker za spremljanje branja knjig. Program prebere tri lokalne datoteke XML, podatke poveže prek ID-jev in omogoča filtriranje knjig po statusu branja ali po datumu zaključka branja. Filtrirane rezultate prikaže v konzoli ter jih shrani v JSON in XML. Za to nalogo uporaba zunanjih API-jev ni potrebna.

## Datoteke

- `data/avtorji.xml` - 13 avtorjev; vsak ima unikaten `id`.
- `data/knjige.xml` - 15 knjig; `avtorId` poveže knjigo z avtorjem.
- `data/branja.xml` - 15 zapisov; `knjigaId` poveže branje s knjigo. Vsebuje datum, status, oceno in tudi prazna ali manjkajoča polja (npr. zapis `B15` nima elementov `ocena` in `datumZakljucka`).
- `main.py` - program v Pythonu.
- `filtrirano.json` in `filtrirano.xml` - primera rezultatov za filter `Prebrano` (izbira 3).

## Zahteve

Potrebujete Python 3.9 ali novejši. Dodatnih knjižnic ni treba nameščati.

## Zagon

Odprite terminal v mapi projekta in zaženite:

```bash
python main.py
```

Če ukaz `python` ne deluje, poskusite `python3 main.py` (Linux/macOS) ali `py main.py` (Windows).

Program najprej vpraša po vrsti filtra:

- `1` - po statusu branja
- `2` - knjige, prebrane po določenem datumu

**Filter 1 (status)** nato vpraša za številko statusa:

- `1` - Želim prebrati
- `2` - Trenutno berem
- `3` - Prebrano

**Filter 2 (datum)** vpraša za datum v obliki `YYYY-MM-DD` in prikaže knjige, ki so bile prebrane (imajo `datumZakljucka`) po tem datumu.

**Primeri:**

- Vnos `1`, nato `3` → prikažejo se vse prebrane knjige.
- Vnos `2`, nato `2026-10-05` → prikažejo se knjige, prebrane po 5. 10. 2026.

Program prepiše izhodni datoteki `filtrirano.json` in `filtrirano.xml` z rezultati izbranega filtra. Priloženi primeri izhoda so pripravljeni za filter 1 → možnost 3 (Prebrano).

## Povezovanje in pretvorba podatkov

Program z `xml.etree.ElementTree` prebere in deserializira XML v Pythonove slovarje. Prek `avtorId` in `knjigaId` poveže avtorje, knjige in zapise branja. Podatka `letoIzdaje` in `ocena` po potrebi pretvori v celo število; prazna ocena ali datum zaključka se v JSON zapišeta kot `null`, v XML pa kot prazen element. JSON se zapiše z modulom `json`.
