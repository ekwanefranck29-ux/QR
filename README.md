# QR Studio

Application Streamlit multi-pages pour générer des QR codes en masse depuis
Excel, avec personnalisation visuelle et suivi optionnel des scans.

## Structure du projet

```
qr-studio/
├── app.py                          # Accueil + gestionnaire de redirection
├── utils.py                        # Fonctions partagées (génération QR, tracking)
├── requirements.txt
├── data/                           # Stockage CSV (liens trackés + scans)
└── pages/
    ├── 1_🔳_Générateur.py          # Génération en masse depuis Excel
    ├── 2_📊_Statistiques.py        # Tableau de bord des scans
    └── 3_❓_Comment_ça_marche.py   # Tutoriel utilisateur
```

⚠️ **Important** : `app.py` doit rester le fichier d'entrée à la racine du
dépôt GitHub pour que Streamlit Community Cloud détecte automatiquement les
pages du dossier `pages/`.

## Installation locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déploiement sur Streamlit Community Cloud

1. Pousse tout le contenu de ce dossier (en gardant la structure) sur un
   dépôt GitHub public
2. Sur share.streamlit.io → "New app" → sélectionne le dépôt et indique
   `app.py` comme fichier principal
3. Une fois déployée, note l'URL obtenue (ex. `https://ton-app.streamlit.app`)
   — c'est celle à renseigner dans le champ "URL publique" du Générateur pour
   activer le suivi des scans

## Fonctionnement du suivi des scans

Quand le suivi est activé, chaque QR code encode non pas le lien final, mais
une URL de la forme `https://ton-app.streamlit.app/?rid=abc123`. En scannant
ce QR code :

1. L'utilisateur arrive sur `app.py` (page d'accueil)
2. L'app détecte le paramètre `rid`, enregistre le scan (date/heure) dans
   `data/scans.csv`
3. L'app redirige automatiquement vers le contenu réel (lien, contact, texte)

Les statistiques (nombre de scans, dernier scan) sont consultables dans la
page **Statistiques**.

### ⚠️ Limitation importante du stockage

Les données sont stockées dans de simples fichiers CSV sur le disque de
l'application. Sur Streamlit Community Cloud, ce stockage est **éphémère** :
il peut être réinitialisé lors d'une mise en veille prolongée ou d'un
redéploiement. C'est largement suffisant pour tester et valider le concept,
mais **avant un usage commercial avec des utilisateurs payants**, il faudra
migrer vers un stockage persistant externe (Google Sheets API, Supabase,
Firebase, ou une vraie base de données). Cette migration ne touche que
`utils.py` — le reste de l'application n'a pas besoin de changer.

## Notes techniques

- Correction d'erreur QR réglée sur le niveau élevé (H) pour rester
  scannable même avec un logo au centre
- Le logo occupe environ 22% de la largeur du QR code
- Les noms de fichiers générés sont nettoyés automatiquement et suffixés
  par le numéro de ligne pour éviter les doublons

## Prochaines étapes possibles (version SaaS)

- Stockage persistant externe (voir ci-dessus)
- Authentification utilisateur / gestion de quotas
- Facturation à l'usage
- Nom de domaine personnalisé
