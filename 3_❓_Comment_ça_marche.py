import streamlit as st

st.set_page_config(page_title="Comment ça marche — QR Studio", page_icon="❓", layout="centered")

st.title("❓ Comment ça marche")

st.markdown(
    """
## 1. La méthode rapide (sans réfléchir)

Si tu veux juste **un** QR code, tout de suite :

1. Va dans **Générateur** (menu à gauche)
2. Choisis le type de contenu :
   - **Lien direct** → pour un site web ou une photo
   - **Texte personnalisé** → pour un message libre
   - **Carte de contact (vCard)** → pour un email, un téléphone, une fiche contact
3. Importe ton fichier Excel avec les informations (même pour un seul QR code,
   un fichier d'une seule ligne suffit)
4. Clique sur **Générer**
5. Télécharge l'image (PNG) depuis l'archive `.zip`

## 2. Le niveau supérieur : personnalisation

Une fois la méthode rapide maîtrisée, tu peux :

- 🎨 changer les couleurs du QR code
- 🖼️ ajouter ton logo au centre
- 📄 générer automatiquement des **centaines** de QR codes en une seule fois,
  directement depuis un fichier Excel
- 📊 activer le **suivi des scans** pour savoir combien de fois — et quand —
  chaque QR code a été scanné (page **Statistiques**)

## 3. Ce que fait QR Studio différemment d'un générateur en ligne classique

| Besoin | Générateur en ligne classique | QR Studio |
|---|---|---|
| 1 QR code ponctuel | ✅ | ✅ |
| Des centaines de QR codes d'un coup | ❌ (un par un) | ✅ (depuis Excel) |
| Logo + couleurs personnalisées | Parfois, souvent payant | ✅ |
| Statistiques de scans | Rarement gratuit | ✅ |

## 4. Bon à savoir

Le suivi des scans fonctionne en faisant passer le QR code par cette
application avant de rediriger vers le contenu réel — c'est ce qui permet
d'enregistrer chaque passage. Sans le suivi activé, le QR code pointe
directement vers ton contenu, sans passer par aucun serveur intermédiaire.
"""
)
