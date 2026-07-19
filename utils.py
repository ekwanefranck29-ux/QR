"""
Fonctions utilitaires partagées par toutes les pages de l'application.
"""

import io
import re
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import qrcode
from PIL import Image
from qrcode.constants import ERROR_CORRECT_H

# ----------------------------------------------------------------------
# Chemins de stockage (CSV légers — voir limitation dans le README)
# ----------------------------------------------------------------------
DOSSIER_DATA = Path(__file__).parent / "data"
DOSSIER_DATA.mkdir(exist_ok=True)
FICHIER_LIENS = DOSSIER_DATA / "liens.csv"
FICHIER_SCANS = DOSSIER_DATA / "scans.csv"

COLONNES_LIENS = ["id", "nom", "type", "contenu", "date_creation"]
COLONNES_SCANS = ["id", "date_scan"]


def _lire_csv(chemin: Path, colonnes: list) -> pd.DataFrame:
    if chemin.exists():
        return pd.read_csv(chemin)
    return pd.DataFrame(columns=colonnes)


def _ecrire_ligne_csv(chemin: Path, colonnes: list, ligne: dict) -> None:
    df = _lire_csv(chemin, colonnes)
    df = pd.concat([df, pd.DataFrame([ligne])], ignore_index=True)
    df.to_csv(chemin, index=False)


# ----------------------------------------------------------------------
# Gestion des liens trackés
# ----------------------------------------------------------------------
def creer_lien_tracke(nom: str, type_qr: str, contenu: str) -> str:
    """Enregistre un contenu à suivre et retourne son identifiant unique."""
    identifiant = uuid.uuid4().hex[:10]
    _ecrire_ligne_csv(
        FICHIER_LIENS,
        COLONNES_LIENS,
        {
            "id": identifiant,
            "nom": nom,
            "type": type_qr,
            "contenu": contenu,
            "date_creation": datetime.now().isoformat(timespec="seconds"),
        },
    )
    return identifiant


def lire_lien(identifiant: str) -> dict | None:
    df = _lire_csv(FICHIER_LIENS, COLONNES_LIENS)
    resultat = df[df["id"] == identifiant]
    if resultat.empty:
        return None
    return resultat.iloc[0].to_dict()


def enregistrer_scan(identifiant: str) -> None:
    _ecrire_ligne_csv(
        FICHIER_SCANS,
        COLONNES_SCANS,
        {"id": identifiant, "date_scan": datetime.now().isoformat(timespec="seconds")},
    )


def statistiques_scans() -> pd.DataFrame:
    """Fusionne liens et scans pour obtenir un tableau de statistiques par QR code."""
    liens = _lire_csv(FICHIER_LIENS, COLONNES_LIENS)
    scans = _lire_csv(FICHIER_SCANS, COLONNES_SCANS)
    if liens.empty:
        return pd.DataFrame(columns=["nom", "type", "nb_scans", "dernier_scan", "date_creation"])

    compte = scans.groupby("id").agg(nb_scans=("id", "count"), dernier_scan=("date_scan", "max"))
    fusion = liens.set_index("id").join(compte, how="left")
    fusion["nb_scans"] = fusion["nb_scans"].fillna(0).astype(int)
    return fusion.reset_index()[["nom", "type", "nb_scans", "dernier_scan", "date_creation", "id"]]


# ----------------------------------------------------------------------
# Génération des QR codes (image)
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
        taille_logo = int(img.size[0] * 0.22)
        logo.thumbnail((taille_logo, taille_logo))

        fond_logo = Image.new("RGBA", logo.size, "WHITE")
        fond_logo.paste(logo, (0, 0), logo)

        pos = (
            (img.size[0] - logo.size[0]) // 2,
            (img.size[1] - logo.size[1]) // 2,
        )
        img.paste(fond_logo, pos)

    return img
