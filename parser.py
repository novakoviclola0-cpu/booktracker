"""Naloga 2: razčlenjevanje podatkov o knjigah s spletne strani."""

import json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


SPLETNA_STRAN = "https://books.toscrape.com/"
IZHOD = Path(__file__).resolve().parent / "data" / "knjige_parser.json"
OCENE = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def razcleni_knjige(html):
    """Iz HTML-ja izlušči podatke o posameznih knjigah."""
    stran = BeautifulSoup(html, "html.parser")
    knjige = []

    for izdelek in stran.select("article.product_pod"):
        povezava = izdelek.select_one("h3 a")
        cena = izdelek.select_one(".price_color")
        ocena = izdelek.select_one(".star-rating")
        zaloga = izdelek.select_one(".availability")
        slika = izdelek.select_one(".image_container img")

        if not povezava or not cena:
            continue

        knjige.append({
            "naslov": povezava.get("title", povezava.get_text(strip=True)),
            "cena_GBP": float(cena.get_text(strip=True).replace("£", "")),
            "ocena_spletne_strani": next(
                (vrednost for razred, vrednost in OCENE.items()
                 if ocena and razred in ocena.get("class", [])), None
            ),
            "na_zalogi": bool(zaloga and "in stock" in zaloga.get_text(" ", strip=True).lower()),
            "povezava": urljoin(SPLETNA_STRAN, povezava["href"]),
            "naslovnica": urljoin(SPLETNA_STRAN, slika["src"]) if slika else None,
        })

    return knjige


def main():
    try:
        odgovor = requests.get(SPLETNA_STRAN, timeout=20)
        odgovor.raise_for_status()
    except requests.RequestException as napaka:
        raise SystemExit(f"Napaka pri pridobivanju spletne strani: {napaka}")

    odgovor.encoding = "utf-8"
    knjige = razcleni_knjige(odgovor.text)
    if not knjige:
        raise SystemExit("Napaka: na spletni strani ni bilo mogoče najti knjig.")

    IZHOD.parent.mkdir(parents=True, exist_ok=True)
    with IZHOD.open("w", encoding="utf-8") as datoteka:
        json.dump({"vir": SPLETNA_STRAN, "stevilo_knjig": len(knjige), "knjige": knjige},
                  datoteka, ensure_ascii=False, indent=4)

    print(f"Uspešno pridobljenih knjig: {len(knjige)}")
    print(f"Podatki so shranjeni v: {IZHOD}")


if __name__ == "__main__":
    main()
