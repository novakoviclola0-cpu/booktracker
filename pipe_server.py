import os
from multiprocessing.connection import Listener
from pathlib import Path

from grpc_server import preberi_knjige
from pipe_client import POT_CEVI, DRUZINA


def analiziraj(zahteva):
    knjige = [
        knjiga for knjiga in preberi_knjige()
        if (not zahteva["status"] or knjiga.status == zahteva["status"])
        and knjiga.stevilo_strani >= zahteva["min_strani"]
        and knjiga.ocena >= zahteva["min_ocena"]
    ]
    ocene = [knjiga.ocena for knjiga in knjige if knjiga.ocena]
    knjige.sort(key=lambda knjiga: (-knjiga.ocena, knjiga.naslov))
    return {
        "stevilo": len(knjige),
        "skupaj_strani": sum(knjiga.stevilo_strani for knjiga in knjige),
        "povprecna_ocena": round(sum(ocene) / len(ocene), 2) if ocene else None,
        "knjige": [
            {
                "Naslov": knjiga.naslov,
                "Avtor": knjiga.avtor,
                "Strani": knjiga.stevilo_strani,
                "Ocena": knjiga.ocena if knjiga.ocena else "-",
            }
            for knjiga in knjige
        ],
    }


def main():
    if os.name != "nt":
        Path(POT_CEVI).unlink(missing_ok=True)
    try:
        with Listener(POT_CEVI, family=DRUZINA) as streznik:
            print(f"BookTracker strežnik posluša: {POT_CEVI}", flush=True)
            while True:
                with streznik.accept() as povezava:
                    try:
                        zahteva = povezava.recv()
                        print(f"Prejeta zahteva: {zahteva}", flush=True)
                        povezava.send(analiziraj(zahteva))
                    except (ValueError, KeyError, TypeError) as napaka:
                        povezava.send({"napaka": str(napaka)})
                    except (EOFError, BrokenPipeError, ConnectionResetError):
                        pass
    finally:
        if os.name != "nt":
            Path(POT_CEVI).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
