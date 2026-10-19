from pathlib import Path
import json
from datetime import date
import xml.etree.ElementTree as ET

# Pot do mape projekta in XML datotek.
MAPA = Path(__file__).parent
PODATKI = MAPA / "data"


def main():
    # 1. Branje XML datotek in pretvorba v Pythonove slovarje.
    avtorji = {}
    for avtor in ET.parse(PODATKI / "avtorji.xml").getroot().findall("avtor"):
        avtorji[avtor.get("id")] = avtor.findtext("ime")

    knjige = {}
    for knjiga in ET.parse(PODATKI / "knjige.xml").getroot().findall("knjiga"):
        knjige[knjiga.get("id")] = {
            "naslov": knjiga.findtext("naslov"),
            "avtorId": knjiga.findtext("avtorId"),
            "letoIzdaje": int(knjiga.findtext("letoIzdaje"))
        }

    branja = ET.parse(PODATKI / "branja.xml").getroot().findall("branje")

    # 2. Uporabnik izbere filter.
    print("Izberite filter:")
    print("1 - Po statusu branja")
    print("2 - Knjige, prebrane po določenem datumu")
    vrsta = input("Vnesite številko (1-2): ").strip()

    if vrsta == "1":
        print("\nIzberite status knjig:")
        print("1 - Želim prebrati")
        print("2 - Trenutno berem")
        print("3 - Prebrano")
        izbira = input("Vnesite številko (1-3): ").strip()

        statusi = {"1": "Želim prebrati", "2": "Trenutno berem", "3": "Prebrano"}
        if izbira not in statusi:
            print("Napačna izbira. Zaženite program znova in izberite 1, 2 ali 3.")
            return
        izbrani_status = statusi[izbira]
        opis_filtra = izbrani_status

        def ustreza(branje):
            return branje.findtext("status") == izbrani_status

    elif vrsta == "2":
        vnos = input("Vnesite datum (YYYY-MM-DD): ").strip()
        try:
            meja = date.fromisoformat(vnos)
        except ValueError:
            print("Napačen datum. Uporabite obliko YYYY-MM-DD, npr. 2026-10-01.")
            return
        opis_filtra = "Prebrano po " + meja.isoformat()

        def ustreza(branje):
            zakljucek = branje.findtext("datumZakljucka")
            return bool(zakljucek) and date.fromisoformat(zakljucek) > meja

    else:
        print("Napačna izbira. Zaženite program znova in izberite 1 ali 2.")
        return

    # 3. Filtriranje in povezovanje datotek prek ID-jev.
    rezultati = []
    for branje in branja:
        if not ustreza(branje):
            continue

        knjiga_id = branje.findtext("knjigaId")
        knjiga = knjige[knjiga_id]
        ime_avtorja = avtorji[knjiga["avtorId"]]
        ocena = branje.findtext("ocena")
        datum_zakljucka = branje.findtext("datumZakljucka")

        rezultati.append({
            "id": branje.get("id"),
            "knjigaId": knjiga_id,
            "naslov": knjiga["naslov"],
            "avtor": ime_avtorja,
            "letoIzdaje": knjiga["letoIzdaje"],
            "status": branje.findtext("status"),
            "ocena": int(ocena) if ocena else None,
            "datumVnosa": branje.findtext("datumVnosa"),
            "datumZakljucka": datum_zakljucka if datum_zakljucka else None
        })

    # 4. Pregleden izpis v konzolo.
    print("\nFiltrirane knjige (" + opis_filtra + "):")
    for zapis in rezultati:
        ocena = zapis["ocena"] if zapis["ocena"] is not None else "-"
        print(zapis["naslov"] + " | " + zapis["avtor"] + " | Ocena: " + str(ocena))
    print("Skupaj:", len(rezultati))

    # 5. Izvoz istih rezultatov v JSON.
    with open(MAPA / "filtrirano.json", "w", encoding="utf-8") as datoteka:
        json.dump({"filter": opis_filtra, "rezultati": rezultati},
                  datoteka, ensure_ascii=False, indent=4)

    # 6. Izvoz istih rezultatov v nov XML.
    koren = ET.Element("filtriranaBranja", {"filter": opis_filtra})
    polja = ("knjigaId", "naslov", "avtor", "letoIzdaje", "status",
             "ocena", "datumVnosa", "datumZakljucka")
    for zapis in rezultati:
        element = ET.SubElement(koren, "branje", {"id": zapis["id"]})
        for polje in polja:
            vrednost = zapis[polje]
            ET.SubElement(element, polje).text = str(vrednost) if vrednost is not None else ""

    drevo = ET.ElementTree(koren)
    ET.indent(drevo, space="    ")
    drevo.write(MAPA / "filtrirano.xml", encoding="utf-8",
                xml_declaration=True, short_empty_elements=False)

    print("Rezultati so shranjeni v filtrirano.json in filtrirano.xml.")


if __name__ == "__main__":
    main()
