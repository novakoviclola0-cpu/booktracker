from concurrent import futures
from pathlib import Path
import time
import xml.etree.ElementTree as ET

import grpc

import booktracker_pb2 as pb
import booktracker_pb2_grpc as rpc


PODATKI = Path(__file__).parent / "data"


def preberi_knjige():
    avtorji = {
        avtor.get("id"): avtor.findtext("ime", "")
        for avtor in ET.parse(PODATKI / "avtorji.xml").getroot()
    }
    branja = {
        branje.findtext("knjigaId"): branje
        for branje in ET.parse(PODATKI / "branja.xml").getroot()
    }
    knjige = []
    for knjiga in ET.parse(PODATKI / "knjige.xml").getroot():
        id_knjige = knjiga.get("id")
        branje = branja.get(id_knjige)
        knjige.append(pb.Book(
            id=id_knjige,
            naslov=knjiga.findtext("naslov", ""),
            avtor=avtorji.get(knjiga.findtext("avtorId"), ""),
            leto_izdaje=int(knjiga.findtext("letoIzdaje", "0")),
            stevilo_strani=int(knjiga.findtext("steviloStrani", "0")),
            status=branje.findtext("status", "") if branje is not None else "",
            ocena=int(branje.findtext("ocena") or 0) if branje is not None else 0,
            datum_zakljucka=branje.findtext("datumZakljucka", "") or "" if branje is not None else "",
        ))
    return knjige


class BookService(rpc.BookServiceServicer):
    def GetBooks(self, request, context):
        knjige = [k for k in preberi_knjige() if not request.status or k.status == request.status]
        return pb.BooksResponse(knjige=knjige)

    def GetBook(self, request, context):
        for knjiga in preberi_knjige():
            if knjiga.id == request.id:
                return knjiga
        context.abort(grpc.StatusCode.NOT_FOUND, "Knjiga ne obstaja.")

    def GetStatistics(self, request, context):
        knjige = preberi_knjige()
        ocene = [k.ocena for k in knjige if k.ocena]
        return pb.StatisticsResponse(
            skupaj=len(knjige),
            prebrano=sum(k.status == "Prebrano" for k in knjige),
            trenutno_berem=sum(k.status == "Trenutno berem" for k in knjige),
            zelim_prebrati=sum(k.status == "Želim prebrati" for k in knjige),
            povprecna_ocena=sum(ocene) / len(ocene) if ocene else 0,
        )

    def StreamBooks(self, request, context):
        for knjiga in preberi_knjige():
            if not context.is_active():
                return
            if not request.status or knjiga.status == request.status:
                yield knjiga
                time.sleep(0.25)


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    rpc.add_BookServiceServicer_to_server(BookService(), server)
    server.add_insecure_port("127.0.0.1:50051")
    server.start()
    print("gRPC strežnik deluje na localhost:50051")
    server.wait_for_termination()


if __name__ == "__main__":
    main()
