# Générateur de QR Codes depuis Excel

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

Une page s'ouvre automatiquement dans le navigateur (par défaut sur `http://localhost:8501`).

## Utilisation

1. Importer un fichier Excel (`.xlsx`)
2. Choisir le type de QR code :
   - **Lien direct** : encode telle quelle la valeur d'une colonne (URL ou chemin de photo)
   - **vCard** : construit une carte de contact scannable à partir de plusieurs colonnes (nom, téléphone, email, organisation, photo)
   - **Texte personnalisé** : gabarit libre combinant plusieurs colonnes, ex. `{nom} - {lien_photo}`
3. Choisir la colonne servant à nommer chaque fichier généré
4. Personnaliser les couleurs et, si besoin, ajouter un logo (PNG/JPG) qui sera incrusté au centre
5. Cliquer sur "Générer les QR codes" puis télécharger l'archive `.zip` contenant tous les fichiers PNG

## Notes techniques

- La correction d'erreur est réglée sur le niveau élevé (H) pour que les QR codes restent scannables même avec un logo au centre.
- Le logo occupe environ 22% de la largeur du QR code — au-delà, la fiabilité de scan diminue.
- Les noms de fichiers sont nettoyés automatiquement (caractères spéciaux remplacés) et suffixés par le numéro de ligne pour éviter les doublons.

## Prochaines étapes possibles (version SaaS)

- Authentification utilisateur / gestion de quotas
- Déploiement sur Streamlit Community Cloud ou un VPS avec nom de domaine dédié
- Historique des générations et facturation à l'usage
