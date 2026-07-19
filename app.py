"""
Accueil de l'application + gestionnaire de redirection.

Quand un QR code "tracké" est scanné, il pointe vers l'URL de cette app
avec un paramètre ?rid=... . Cette page détecte ce paramètre, enregistre
le scan, puis redirige (ou affiche) le contenu réel.
"""

import streamlit as st
import streamlit.components.v1 as components

import utils

st.set_page_config(page_title="QR Studio", page_icon="🔳", layout="centered")

params = st.query_params
rid = params.get("rid")

# ------------------------------------------------------------------
# Cas 1 : un QR tracké vient d'être scanné
# ------------------------------------------------------------------
if rid:
    utils.enregistrer_scan(rid)
    lien = utils.lire_lien(rid)

    if lien is None:
        st.error("Ce QR code est invalide ou a expiré.")
        st.stop()

    contenu = str(lien["contenu"])

    if contenu.startswith("http://") or contenu.startswith("https://"):
        st.write("Redirection en cours...")
        components.html(f"<script>window.location.href = {contenu!r};</script>", height=0)
        st.markdown(f"Si la redirection ne se fait pas automatiquement, [clique ici]({contenu}).")

    elif contenu.startswith("BEGIN:VCARD"):
        st.subheader(f"📇 Contact : {lien['nom']}")
        st.download_button(
            "Télécharger le contact (.vcf)",
            contenu,
            file_name=f"{lien['nom']}.vcf",
            mime="text/vcard",
        )

    else:
        st.subheader(lien["nom"])
        st.write(contenu)

    st.stop()

# ------------------------------------------------------------------
# Cas 2 : page d'accueil normale
# ------------------------------------------------------------------
st.title("🔳 QR Studio")
st.write(
    "Bienvenue ! Utilise le menu à gauche pour :\n\n"
    "- **Générateur** : créer des QR codes en masse depuis un fichier Excel\n"
    "- **Statistiques** : suivre les scans de tes QR codes trackés\n"
    "- **Comment ça marche** : guide rapide, du QR code simple au QR code avancé"
)
