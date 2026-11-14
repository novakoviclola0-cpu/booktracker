# Naloga 5 – gRPC

BookTracker uporablja gRPC za prenos podatkov o knjigah iz strežnika v spletno aplikacijo Streamlit. Strežnik bere obstoječe datoteke XML v mapi `data`, odjemalec pa podatke pridobi izključno prek gRPC.

## Zagon

V mapi projekta najprej namestimo knjižnice:

```powershell
python -m pip install -r requirements.txt
```

V prvem terminalu zaženemo strežnik:

```powershell
python grpc_server.py
```

V drugem terminalu, v isti mapi, zaženemo aplikacijo:

```powershell
python -m streamlit run app_naloga5.py
```

Aplikacija se odpre na `http://localhost:8501`. Strežnik uporablja `localhost:50051`. Terminal s strežnikom mora ostati odprt.

## RPC storitev

Datoteka `booktracker.proto` vsebuje eno storitev `BookService` s štirimi metodami:

| Metoda | Tip | Namen |
| --- | --- | --- |
| `GetBooks` | Unary | Filtriranje in prikaz knjig po statusu. |
| `GetBook` | Unary | Pridobivanje podrobnosti izbrane knjige. |
| `GetStatistics` | Unary | Prikaz števila knjig po statusih in povprečne ocene. |
| `StreamBooks` | Server streaming | Postopen prenos knjig in sprotno posodabljanje tabele. |

Sporočilo `Book` vsebuje ID, naslov, avtorja, leto izdaje, število strani, status, oceno in datum zaključka. Zahtevki in odgovori so definirani v isti datoteki `.proto`.

## Preizkus

Izberemo status in kliknemo **Prikaži knjige**. Nato izberemo knjigo in kliknemo **Podrobnosti knjige**. Gumb **Prikaži statistiko** pridobi statistiko vseh knjig. Ob kliku **Pretakaj knjige** strežnik pošilja knjige eno po eno, tabela pa se posodablja med prenosom.

Če spremenimo katero od datotek XML in ponovimo poizvedbo, strežnik prebere nove podatke.

Generirani datoteki `booktracker_pb2.py` in `booktracker_pb2_grpc.py` sta že vključeni. Ob spremembi `.proto` ju lahko ponovno ustvarimo z:

```powershell
python -m pip install grpcio-tools
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. booktracker.proto
```

Prejšnje naloge ostanejo dostopne prek svojih datotek, npr. `app_naloga4.py`.
