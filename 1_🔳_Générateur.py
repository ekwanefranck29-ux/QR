import io
import zipfile

import pandas as pd
import streamlit as st

import utils

st.set_page_config(page_title="Générateur — QR Studio", page_icon="🔳", layout="wide")

st.title("🔳 Générateur de QR Codes depuis Excel")
st.caption(
    "Importez un fichier Excel, choisissez le type de QR code à générer, "
    "personnalisez le style et téléchargez le tout en un clic."
)

# ----------------------------------------------------------------------
# 1. Import du fichier Excel
# ----------------------------------------------------------------------
st.header("1. Importer le fichier Excel")
fichier_excel = st.file_uploader("Fichier Excel (.xlsx)", type=["xlsx", "xls"])

if fichier_excel is None:
    st.info("Importez un fichier Excel pour commencer.")
    st.stop()

df = pd.read_excel(fichier_excel)
st.success(f"{len(df)} lignes chargées depuis {fichier_excel.name}")
st.dataframe(df.head(10), use_container_width=True)

colonnes = list(df.columns)

# ----------------------------------------------------------------------
# 2. Choix du type de QR code
# ----------------------------------------------------------------------
st.header("2. Type de QR code")
type_qr = st.radio(
    "Que doit contenir chaque QR code ?",
    ["Lien direct (URL ou chemin de photo)", "Carte de contact (vCard)", "Texte personnalisé"],
    horizontal=True,
)

mapping_vcard = {}
gabarit_texte = None
col_lien = None

if type_qr == "Lien direct (URL ou chemin de photo)":
    col_lien = st.selectbox("Colonne contenant le lien / chemin de la photo", colonnes)

elif type_qr == "Carte de contact (vCard)":
    st.caption("Associez les champs de la vCard aux colonnes correspondantes (laissez vide si non disponible).")
    c1, c2 = st.columns(2)
    with c1:
        mapping_vcard["nom"] = st.selectbox("Nom complet", ["(aucune)"] + colonnes)
        mapping_vcard["telephone"] = st.selectbox("Téléphone", ["(aucune)"] + colonnes)
        mapping_vcard["organisation"] = st.selectbox("Organisation", ["(aucune)"] + colonnes)
    with c2:
        mapping_vcard["email"] = st.selectbox("Email", ["(aucune)"] + colonnes)
        mapping_vcard["photo"] = st.selectbox("Lien photo (URL uniquement)", ["(aucune)"] + colonnes)
    mapping_vcard = {k: (v if v != "(aucune)" else None) for k, v in mapping_vcard.items()}

else:  # Texte personnalisé
    st.caption(
        "Écrivez un gabarit en utilisant les noms de colonnes entre accolades, "
        "ex : `{nom} - {lien_photo}`."
    )
    st.code(", ".join(f"{{{c}}}" for c in colonnes), language=None)
    gabarit_texte = st.text_area("Gabarit du contenu", value="{" + colonnes[0] + "}")

# ----------------------------------------------------------------------
# 3. Nommage
# ----------------------------------------------------------------------
st.header("3. Nommage des fichiers")
col_nom_fichier = st.selectbox("Colonne à utiliser pour nommer chaque fichier QR code", colonnes, index=0)

# ----------------------------------------------------------------------
# 4. Personnalisation visuelle
# ----------------------------------------------------------------------
st.header("4. Personnalisation")
c1, c2, c3 = st.columns(3)
with c1:
    couleur_avant = st.color_picker("Couleur du QR code", "#000000")
with c2:
    couleur_fond = st.color_picker("Couleur de fond", "#FFFFFF")
with c3:
    fichier_logo = st.file_uploader("Logo à insérer au centre (optionnel)", type=["png", "jpg", "jpeg"])

logo_bytes = fichier_logo.read() if fichier_logo is not None else None

# ----------------------------------------------------------------------
# 5. Suivi des scans (optionnel)
# ----------------------------------------------------------------------
st.header("5. Suivi des scans (optionnel)")
activer_suivi = st.checkbox(
    "Activer le suivi des scans pour ces QR codes",
    help=(
        "Chaque QR code redirigera vers cette application, qui enregistrera le scan "
        "avant d'afficher/rediriger vers le contenu réel. Consulte la page "
        "'Statistiques' pour voir les résultats."
    ),
)

url_app = None
if activer_suivi:
    url_app = st.text_input(
        "URL publique de cette application (ex : https://ton-app.streamlit.app)",
        placeholder="https://ton-app.streamlit.app",
    )
    st.caption(
        "⚠️ Stockage léger basé sur des fichiers CSV : adapté aux tests et petits volumes. "
        "Pour un usage en production à grande échelle, prévoir une base de données externe "
        "(voir README)."
    )

# ----------------------------------------------------------------------
# 6. Génération
# ----------------------------------------------------------------------
st.header("6. Génération")

if st.button("🚀 Générer les QR codes", type="primary"):
    if activer_suivi and not url_app:
        st.error("Indique l'URL publique de l'application pour activer le suivi des scans.")
        st.stop()

    if type_qr == "Lien direct (URL ou chemin de photo)" and df[col_lien].isna().all():
        st.error("La colonne sélectionnée est vide.")
        st.stop()

    zip_buffer = io.BytesIO()
    apercus = []
    total = len(df)

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        barre = st.progress(0, text="Génération en cours...")

        for i, row in df.iterrows():
            if type_qr == "Lien direct (URL ou chemin de photo)":
                contenu_reel = str(row[col_lien])
            elif type_qr == "Carte de contact (vCard)":
                contenu_reel = utils.construire_contenu_vcard(row, mapping_vcard)
            else:
                contenu_reel = utils.construire_contenu_texte_libre(row, gabarit_texte)

            if not contenu_reel or contenu_reel.lower() == "nan":
                continue

            nom_ligne = str(row[col_nom_fichier])

            if activer_suivi:
                identifiant = utils.creer_lien_tracke(nom_ligne, type_qr, contenu_reel)
                contenu_qr = f"{url_app.rstrip('/')}/?rid={identifiant}"
            else:
                contenu_qr = contenu_reel

            img = utils.generer_qr_image(contenu_qr, couleur_avant, couleur_fond, logo_bytes)

            nom_fichier = utils.nettoyer_nom_fichier(nom_ligne) + f"_{i}.png"
            buffer_img = io.BytesIO()
            img.save(buffer_img, format="PNG")
            archive.writestr(nom_fichier, buffer_img.getvalue())

            if len(apercus) < 6:
                apercus.append((nom_fichier, img))

            barre.progress((i + 1) / total, text=f"Génération en cours... ({i + 1}/{total})")

        barre.empty()

    st.success("QR codes générés avec succès.")

    if apercus:
        st.subheader("Aperçu")
        cols_apercu = st.columns(len(apercus))
        for col, (nom, img) in zip(cols_apercu, apercus):
            with col:
                st.image(img, caption=nom, use_container_width=True)

    st.download_button(
        label="📦 Télécharger tous les QR codes (.zip)",
        data=zip_buffer.getvalue(),
        file_name="qr_codes.zip",
        mime="application/zip",
    )
