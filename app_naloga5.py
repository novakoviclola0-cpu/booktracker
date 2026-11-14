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
