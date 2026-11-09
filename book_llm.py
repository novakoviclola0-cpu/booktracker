from dataclasses import dataclass
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import requests


POT = Path(__file__).resolve().parent
API = "https://generativelanguage.googleapis.com/v1beta"

SHEMA = {
    "type": "OBJECT",
    "properties": {
        "knjige": {
            "type": "ARRAY",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "OBJECT",
                "properties": {
                    "naslov": {"type": "STRING"},
                    "avtor": {"type": "STRING"},
                    "razlog": {"type": "STRING"},
                },
                "required": ["naslov", "avtor", "razlog"],
            },
        }
    },
    "required": ["knjige"],
}

PREDNOSTNI_MODELI = (
    "gemini-2.5-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
)


class NapakaPriporocil(Exception):
    pass


@dataclass(frozen=True)
class PriporocenaKnjiga:
    naslov: str
    avtor: str
    razlog: str

    @classmethod
    def iz_podatkov(cls, podatki: dict) -> "PriporocenaKnjiga":
        if not isinstance(podatki, dict):
            raise ValueError("Neveljavna oblika priporočila.")
        vrednosti = (podatki.get("naslov"), podatki.get("avtor"), podatki.get("razlog"))
        if any(not isinstance(v, str) or not v.strip() for v in vrednosti):
            raise ValueError("V priporočilu manjkajo podatki o knjigi.")
        return cls(*(v.strip() for v in vrednosti))


@dataclass(frozen=True)
class Priporocila:
    knjige: list[PriporocenaKnjiga]

    @classmethod
    def iz_json(cls, besedilo: str) -> "Priporocila":
        podatki = json.loads(besedilo)
        if not isinstance(podatki, dict) or not isinstance(podatki.get("knjige"), list):
            raise ValueError("Neveljavna oblika odgovora.")
        if len(podatki["knjige"]) != 3:
            raise ValueError("Odgovor mora vsebovati tri knjige.")
        knjige = [PriporocenaKnjiga.iz_podatkov(k) for k in podatki["knjige"]]
        return cls(knjige)


def preberi_knjiznico() -> list[dict]:
    mapa = POT / "data"
    avtorji = {
        a.get("id"): (a.findtext("ime") or "Neznan avtor")
        for a in ET.parse(mapa / "avtorji.xml").getroot().findall("avtor")
    }
    branja = {
        b.findtext("knjigaId"): b
        for b in ET.parse(mapa / "branja.xml").getroot().findall("branje")
    }

    knjiznica = []
    for knjiga in ET.parse(mapa / "knjige.xml").getroot().findall("knjiga"):
        zapis = branja.get(knjiga.get("id"))
        status = zapis.findtext("status") if zapis is not None else None
        ocena = zapis.findtext("ocena") if zapis is not None else None
        knjiznica.append({
            "naslov": knjiga.findtext("naslov") or "",
            "avtor": avtorji.get(knjiga.findtext("avtorId"), "Neznan avtor"),
            "status": status or "Brez statusa",
            "ocena": int(ocena) if ocena and ocena.isdigit() else None,
        })
    return knjiznica


def sestavi_prompt(zanr: str, vzdusje: str, dolzina: str,
                   dodatno: str, knjiznica: list[dict]) -> str:
    return (
        "Za uporabnika aplikacije BookTracker predlagaj natanko tri različne resnične knjige. "
        "Izberi knjige, ki jih še nima v knjižnici. Upoštevaj že prebrane knjige, "
        "njihove ocene in želje uporabnika. Odgovori v slovenščini. "
        "Za vsako knjigo napiši kratek razlog za priporočilo. "
        "Odgovor naj bo JSON objekt s poljem 'knjige', ki vsebuje tri objekte "
        "s polji 'naslov', 'avtor' in 'razlog'.\n\n"
        f"Žanr: {zanr}\n"
        f"Vzdušje: {vzdusje}\n"
        f"Dolžina: {dolzina}\n"
        f"Dodatne želje: {dodatno.strip() or 'Brez'}\n"
        "Knjige v uporabnikovi knjižnici:\n"
        f"{json.dumps(knjiznica, ensure_ascii=False)}"
    )


def _sporocilo_napake(odgovor: requests.Response) -> str:
    koda = odgovor.status_code
    if koda in (401, 403):
        return "API ključ nima dostopa. Preveri ključ in projekt v Google AI Studio."
    if koda == 400:
        return "Strežnik ni sprejel zahteve. Preveri nastavitve API ključa."
    if koda == 429:
        return "Dosežena je omejitev zahtev. Poskusi pozneje."
    if koda >= 500:
        return "Storitev trenutno ni dosegljiva. Poskusi pozneje."
    return f"Zahteve ni bilo mogoče izvesti (HTTP {koda})."


def _razpolozljivi_modeli(api_kljuc: str) -> list[str]:
    modeli = []
    zeton = None
    for _ in range(5):
        parametri = {"pageSize": 100}
        if zeton:
            parametri["pageToken"] = zeton
        odgovor = requests.get(
            f"{API}/models",
            params=parametri,
            headers={"x-goog-api-key": api_kljuc},
            timeout=20,
        )
        if not odgovor.ok:
            raise NapakaPriporocil(_sporocilo_napake(odgovor))
        try:
            podatki = odgovor.json()
        except ValueError as napaka:
            raise NapakaPriporocil("Seznama modelov ni bilo mogoče prebrati.") from napaka
        for model in podatki.get("models", []):
            ime = model.get("name", "")
            metode = model.get("supportedGenerationMethods", [])
            if (
                re.fullmatch(r"models/gemini-[a-zA-Z0-9_.-]+", ime)
                and "generateContent" in metode
                and not any(x in ime for x in ("image", "tts", "audio", "live", "embedding"))
            ):
                modeli.append(ime)
        zeton = podatki.get("nextPageToken")
        if not zeton:
            break

    prednostni = [f"models/{ime}" for ime in PREDNOSTNI_MODELI]
    return sorted(set(modeli), key=lambda ime: (
        prednostni.index(ime) if ime in prednostni else len(prednostni), ime
    ))


def pridobi_priporocila(api_kljuc: str, prompt: str) -> Priporocila:
    try:
        modeli = _razpolozljivi_modeli(api_kljuc)
        if not modeli:
            raise NapakaPriporocil("Za ta API ključ ni na voljo primernega modela.")

        vsebina = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": SHEMA,
            },
        }
        for ime_modela in modeli:
            odgovor = requests.post(
                f"{API}/{ime_modela}:generateContent",
                headers={"x-goog-api-key": api_kljuc, "Content-Type": "application/json"},
                json=vsebina,
                timeout=65,
            )
            if odgovor.status_code == 404:
                continue
            if not odgovor.ok:
                raise NapakaPriporocil(_sporocilo_napake(odgovor))
            try:
                podatki = odgovor.json()
                deli = podatki["candidates"][0]["content"]["parts"]
                besedilo = "".join(deo["text"] for deo in deli if "text" in deo)
                return Priporocila.iz_json(besedilo)
            except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as napaka:
                raise NapakaPriporocil("Priporočil ni bilo mogoče prebrati. Poskusi znova.") from napaka

        raise NapakaPriporocil("Za ta ključ ni bilo mogoče uporabiti nobenega razpoložljivega modela.")
    except requests.Timeout as napaka:
        raise NapakaPriporocil("Povezava je trajala predolgo. Poskusi znova.") from napaka
    except requests.RequestException as napaka:
        raise NapakaPriporocil("Povezava s storitvijo ni uspela.") from napaka
