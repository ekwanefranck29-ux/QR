"""
Générateur de QR Codes depuis Excel
------------------------------------
Application Streamlit permettant de générer plusieurs types de QR codes
(lien direct, vCard, texte personnalisé) à partir des données d'un fichier
Excel, avec personnalisation des couleurs et ajout d'un logo au centre.
"""

import io
import re
import zipfile
from pathlib import Path

import pandas as pd
import qrcode
import streamlit as st
from PIL import Image
from qrcode.constants import ERROR_CORRECT_H

# ----------------------------------------------------------------------
# Configuration générale de la page
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Générateur de QR Codes",
    page_icon="🔳",
    layout="wide",
)

st.title("🔳 Générateur de QR Codes depuis Excel")
st.caption(
    "Importez un fichier Excel, choisissez le type de QR code à générer, "
    "personnalisez le style et téléchargez le tout en un clic."
)


# ----------------------------------------------------------------------
# Fonctions utilitaires
# ----------------------------------------------------------------------
def nettoyer_nom_fichier(texte: str) -> str:
    """Transforme une chaîne en nom de fichier sûr (sans caractères spéciaux)."""
    texte = str(texte).strip()
    texte = re.sub(r"[^\w\-]+", "_", texte)
    return texte[:60] if texte else "qr_code"


def construire_contenu_vcard(row, mapping: dict) -> str:
    """Construit une chaîne vCard 3.0 à partir des colonnes mappées."""
    nom = str(row.get(mapping.get("nom"), "")).strip() if mapping.get("nom") else ""
    tel = str(row.get(mapping.get("telephone"), "")).strip() if mapping.get("telephone") else ""
    email = str(row.get(mapping.get("email"), "")).strip() if mapping.get("email") else ""
    org = str(row.get(mapping.get("organisation"), "")).strip() if mapping.get("organisation") else ""
    photo_url = str(row.get(mapping.get("photo"), "")).strip() if mapping.get("photo") else ""

    lignes = ["BEGIN:VCARD", "VERSION:3.0"]
    if nom and nom.lower() != "nan":
        lignes.append(f"N:{nom}")
        lignes.append(f"FN:{nom}")
    if org and org.lower() != "nan":
        lignes.append(f"ORG:{org}")
    if tel and tel.lower() != "nan":
        lignes.append(f"TEL;TYPE=CELL:{tel}")
    if email and email.lower() != "nan":
        lignes.append(f"EMAIL:{email}")
    if photo_url and photo_url.lower() != "nan" and photo_url.startswith("http"):
        lignes.append(f"PHOTO;VALUE=URL:{photo_url}")
    lignes.append("END:VCARD")
    return "\n".join(lignes)


def construire_contenu_texte_libre(row, gabarit: str) -> str:
    """Remplace les {colonne} du gabarit par les valeurs de la ligne."""
    contenu = gabarit
    for col in row.index:
        contenu = contenu.replace("{" + str(col) + "}", str(row[col]))
    return contenu


def generer_qr_image(
    contenu: str,
    couleur_avant: str,
    couleur_fond: str,
    logo_bytes: bytes | None = None,
) -> Image.Image:
    """Génère une image de QR code personnalisée, avec logo optionnel au centre."""
    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECT_H,  # correction d'erreur élevée requise si logo
        box_size=10,
        border=4,
    )
    qr.add_data(contenu)
    qr.make(fit=True)
    img = qr.make_image(fill_color=couleur_avant, back_color=couleur_fond).convert("RGB")

    if logo_bytes:
        logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
        # Le logo occupe environ 22% de la largeur du QR code (compromis lisibilité/esthétique)
        taille_logo = int(img.size[0] * 0.22)
        logo.thumbnail((taille_logo, taille_logo))

        # Fond blanc derrière le logo pour préserver la scannabilité
        fond_logo = Image.new("RGBA", logo.size, "WHITE")
        fond_logo.paste(logo, (0, 0), logo)

        pos = (
            (img.size[0] - logo.size[0]) // 2,
            (img.size[1] - logo.size[1]) // 2,
        )
        img.paste(fond_logo, pos)

    return img


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

contenu_par_ligne = None
mapping_vcard = {}
gabarit_texte = None

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
# 3. Nom des fichiers générés
# ----------------------------------------------------------------------
st.header("3. Nommage des fichiers")
col_nom_fichier = st.selectbox(
    "Colonne à utiliser pour nommer chaque fichier QR code",
    colonnes,
    index=0,
)

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
# 5. Génération
# ----------------------------------------------------------------------
st.header("5. Génération")

if st.button("🚀 Générer les QR codes", type="primary"):
    if type_qr == "Lien direct (URL ou chemin de photo)" and df[col_lien].isna().all():
        st.error("La colonne sélectionnée est vide.")
        st.stop()

    zip_buffer = io.BytesIO()
    apercus = []

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        barre = st.progress(0, text="Génération en cours...")
        total = len(df)

        for i, row in df.iterrows():
            if type_qr == "Lien direct (URL ou chemin de photo)":
                contenu = str(row[col_lien])
            elif type_qr == "Carte de contact (vCard)":
                contenu = construire_contenu_vcard(row, mapping_vcard)
            else:
                contenu = construire_contenu_texte_libre(row, gabarit_texte)

            if not contenu or contenu.lower() == "nan":
                continue

            img = generer_qr_image(contenu, couleur_avant, couleur_fond, logo_bytes)

            nom_fichier = nettoyer_nom_fichier(row[col_nom_fichier]) + f"_{i}.png"
            buffer_img = io.BytesIO()
            img.save(buffer_img, format="PNG")
            archive.writestr(nom_fichier, buffer_img.getvalue())

            if len(apercus) < 6:
                apercus.append((nom_fichier, img))

            barre.progress((i + 1) / total, text=f"Génération en cours... ({i + 1}/{total})")

        barre.empty()

    st.success(f"{len(apercus) if len(apercus) < total else total} QR codes générés avec succès.")

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
