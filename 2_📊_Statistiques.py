import streamlit as st

import utils

st.set_page_config(page_title="Statistiques — QR Studio", page_icon="📊", layout="wide")

st.title("📊 Statistiques de scans")
st.caption(
    "Ce tableau ne montre que les QR codes générés avec le suivi activé "
    "(page Générateur, section 5)."
)

stats = utils.statistiques_scans()

if stats.empty:
    st.info("Aucun QR code tracké pour le moment. Active le suivi des scans lors de la génération.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("QR codes trackés", len(stats))
c2.metric("Scans au total", int(stats["nb_scans"].sum()))
c3.metric("QR jamais scannés", int((stats["nb_scans"] == 0).sum()))

st.dataframe(
    stats.sort_values("nb_scans", ascending=False).drop(columns=["id"]),
    use_container_width=True,
)

st.bar_chart(stats.set_index("nom")["nb_scans"])

st.caption(
    "⚠️ Les données sont stockées dans de simples fichiers CSV sur le serveur de l'app. "
    "Elles peuvent être réinitialisées lors d'un redéploiement — voir le README pour "
    "passer à un stockage persistant (Google Sheets, Supabase, Firebase...) avant un "
    "usage commercial à grande échelle."
)
