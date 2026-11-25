import os
import time
from multiprocessing.connection import Client


POT_CEVI = r"\\.\pipe\booktracker_naloga7" if os.name == "nt" else "/tmp/booktracker_naloga7.sock"
DRUZINA = "AF_PIPE" if os.name == "nt" else "AF_UNIX"


def poslji_zahtevo(zahteva):
    for poskus in range(12):
        try:
            with Client(POT_CEVI, family=DRUZINA) as povezava:
                povezava.send(zahteva)
                if not povezava.poll(4):
                    raise TimeoutError("Strežnik se ne odziva.")
                odgovor = povezava.recv()
                if "napaka" in odgovor:
                    raise RuntimeError(odgovor["napaka"])
                return odgovor
        except (FileNotFoundError, ConnectionRefusedError, OSError):
            if poskus == 11:
                raise ConnectionError("Strežnik ni dosegljiv. Zaženi pipe_server.py.")
            time.sleep(0.25)
