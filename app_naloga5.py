import grpc
import streamlit as st

import booktracker_pb2 as pb
import booktracker_pb2_grpc as rpc


st.set_page_config(page_title="BookTracker", layout="centered")
st.title("BookTracker")
st.subheader("Moja knjižnica")


@st.cache_resource
def odjemalec():
    kanal = grpc.insecure_channel("localhost:50051")
    return rpc.BookServiceStub(kanal)


def vrstica(knjiga):
    return {"Naslov": knjiga.naslov, "Avtor": knjiga.avtor, "Status": knjiga.status}


status = st.selectbox("Status branja", ["Vse", "Prebrano", "Trenutno berem", "Želim prebrati"])
filter_status = "" if status == "Vse" else status

if st.session_state.get("filter_status") != filter_status:
    st.session_state["filter_status"] = filter_status
    st.session_state["knjige"] = []

if st.button("Prikaži knjige"):
    try:
        odgovor = odjemalec().GetBooks(pb.BooksRequest(status=filter_status), timeout=5)
        st.session_state["knjige"] = list(odgovor.knjige)
    except grpc.RpcError:
        st.error("Povezava s strežnikom ni uspela. Zaženi grpc_server.py.")

knjige = st.session_state.get("knjige", [])
if knjige:
    st.dataframe([vrstica(k) for k in knjige], hide_index=True, use_container_width=True)
    naslovi = {k.id: k.naslov for k in knjige}
    izbira = st.selectbox("Izberi knjigo", list(naslovi), format_func=lambda id: naslovi[id])
    if st.button("Podrobnosti knjige"):
        try:
            knjiga = odjemalec().GetBook(pb.BookRequest(id=izbira), timeout=5)
            st.write(f"**{knjiga.naslov}** — {knjiga.avtor}")
            st.write(f"Leto izdaje: {knjiga.leto_izdaje}")
            st.write(f"Število strani: {knjiga.stevilo_strani}")
            st.write(f"Status: {knjiga.status}")
            st.write(f"Ocena: {knjiga.ocena if knjiga.ocena else '-'}")
            if knjiga.datum_zakljucka:
                st.write(f"Datum zaključka: {knjiga.datum_zakljucka}")
        except grpc.RpcError:
            st.error("Podrobnosti knjige ni mogoče pridobiti.")

st.divider()
if st.button("Prikaži statistiko"):
    try:
        podatki = odjemalec().GetStatistics(pb.StatisticsRequest(), timeout=5)
        st.write(f"Skupaj knjig: {podatki.skupaj}")
        st.write(f"Prebrano: {podatki.prebrano}")
        st.write(f"Trenutno berem: {podatki.trenutno_berem}")
        st.write(f"Želim prebrati: {podatki.zelim_prebrati}")
        st.write(f"Povprečna ocena: {podatki.povprecna_ocena:.2f}")
    except grpc.RpcError:
        st.error("Statistike ni mogoče pridobiti. Preveri strežnik.")

st.divider()
st.subheader("Sprotni prenos knjig")
if st.button("Pretakaj knjige"):
    prikaz = st.empty()
    vrstice = []
    try:
        for knjiga in odjemalec().StreamBooks(pb.BooksRequest(status=filter_status), timeout=15):
            vrstice.append(vrstica(knjiga))
            prikaz.dataframe(vrstice, hide_index=True, use_container_width=True)
        st.write(f"Prenesenih knjig: {len(vrstice)}")
    except grpc.RpcError:
        st.error("Pretakanje ni uspelo. Preveri strežnik.")

st.divider()
st.subheader("Analiza knjižnice prek poimenovane cevi")
min_strani = st.number_input("Najmanjše število strani", min_value=0, step=50)
min_ocena = st.selectbox("Najmanjša ocena", [0, 1, 2, 3, 4, 5], format_func=lambda x: "Vse" if x == 0 else str(x))


@st.cache_resource
def pipe_izvajalnik():
    from concurrent.futures import ThreadPoolExecutor
    return ThreadPoolExecutor(max_workers=2)


if st.button("Analiziraj knjižnico", disabled=bool(st.session_state.get("pipe_opravilo") and not st.session_state["pipe_opravilo"].done())):
    from pipe_client import poslji_zahtevo
    st.session_state.pop("pipe_rezultat", None)
    st.session_state["pipe_opravilo"] = pipe_izvajalnik().submit(
        poslji_zahtevo,
        {"status": filter_status, "min_strani": min_strani, "min_ocena": min_ocena},
    )


@st.fragment(run_every="1s")
def prikazi_pipe_rezultat():
    opravilo = st.session_state.get("pipe_opravilo")
    if opravilo:
        if not opravilo.done():
            st.info("Čakam na odgovor strežnika ...")
            return
        st.session_state.pop("pipe_opravilo", None)
        try:
            st.session_state["pipe_rezultat"] = opravilo.result()
        except (ConnectionError, TimeoutError, RuntimeError, EOFError, OSError) as napaka:
            st.error(str(napaka))
            return
    rezultat = st.session_state.get("pipe_rezultat")
    if rezultat is not None:
        st.write(f"Knjig: {rezultat['stevilo']}")
        st.write(f"Skupno strani: {rezultat['skupaj_strani']}")
        ocena = rezultat["povprecna_ocena"]
        st.write(f"Povprečna ocena: {ocena if ocena is not None else '-'}")
        if rezultat["knjige"]:
            st.dataframe(rezultat["knjige"], hide_index=True, use_container_width=True)
        else:
            st.info("Ni knjig, ki ustrezajo izbranim filtrom.")


prikazi_pipe_rezultat()
