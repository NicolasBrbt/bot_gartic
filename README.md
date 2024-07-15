# Bot Gartic Phone

## Description

Ce projet permet de charger une image depuis une URL, de sélectionner des couleurs à partir de cette image, de définir une grille, puis de dessiner des lignes sur l'écran en fonction des couleurs sélectionnées et des gradients calculés. Il utilise des bibliothèques Python telles que `pynput`, `Pillow`, `requests`, et `numpy`.

## Prérequis

Avant de pouvoir exécuter le programme, vous devez installer les dépendances nécessaires. Vous pouvez le faire en utilisant le fichier `requirements.txt` fourni dans ce dépôt.

### Installation des Dépendances

Créez un environnement virtuel (optionnel mais recommandé) et installez les dépendances en exécutant :

```bash
# Crée un environnement virtuel
python -m venv venv

# Active l'environnement virtuel
# Sur Windows
venv\Scripts\activate
# Sur macOS/Linux
source venv/bin/activate

# Installe les dépendances
pip install -r requirements.txt
```
## Exemple d'Utilisation

Voici un guide étape par étape pour vous aider à utiliser le script Python et accomplir les tâches de dessin automatisé.

### Étape 1 : Exécuter le Script

Pour démarrer le programme, ouvrez une ligne de commande ou un terminal et exécutez le script `main.py` avec la commande suivante :

```bash
python main.py
```

### Étape 2 : Entrer l'URL de l'Image
Le programme vous demandera de fournir l'URL de l'image à utiliser. Entrez l'URL complète de l'image que vous souhaitez traiter :
```bash
Entrez l'URL de l'image: https://example.com/image.png
```

### Étape 3 : Spécifier le Nombre de Couleurs Souhaitées
Vous serez invité à entrer le nombre de couleurs que vous souhaitez sélectionner à partir de l'image. Tapez le nombre et appuyez sur Entrée :

```bash
Veuillez entrer le nombre de couleurs souhaitées : 3
```

### Étape 4 : Sélectionner les Couleurs de la Palette
Après avoir spécifié le nombre de couleurs, le programme vous demandera de cliquer sur les couleurs de la palette du jeu.

### Étape 5 : Sélectionner les Coins de la Grille
Le programme vous demandera ensuite de cliquer sur deux coins opposés de la grille sur l'écran. Ces coins définiront la zone dans laquelle le dessin sera effectué :


### Étape 6 : Attendre le Dessin Automatisé
Après avoir sélectionné les couleurs et défini la grille, le programme effectuera automatiquement les actions de dessin en utilisant les couleurs sélectionnées. Vous verrez les lignes dessinées à l'écran selon les instructions basées sur l'image et les couleurs choisies.

Note : Assurez-vous que votre écran est visible pour que le programme puisse dessiner correctement.

