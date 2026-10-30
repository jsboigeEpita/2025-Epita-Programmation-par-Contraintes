# Générateur de Mots Croisés avec OR-Tools et OpenAI

Ce projet génère automatiquement des grilles de mots croisés remplies, accompagnées de leurs définitions générées par une IA. Il utilise la bibliothèque OR-Tools de Google pour la modélisation et la résolution par programmation par contraintes (CSP), et l'API OpenAI pour la génération des définitions.

## Fonctionnalités

*   Génération aléatoire de la structure de la grille (cases noires/blanches).
*   Identification automatique des emplacements pour les mots (horizontaux et verticaux).
*   Chargement d'un dictionnaire externe et filtrage des mots par longueur requise.
*   Modélisation du problème de remplissage comme un Problème de Satisfaction de Contraintes (CSP).
*   Utilisation du solveur CP-SAT d'OR-Tools pour trouver une solution valide (remplissage de la grille).
*   Génération automatique des définitions pour les mots de la solution via l'API OpenAI (GPT-3.5).
*   Affichage de la grille remplie et des définitions dans la console.
*   (Via le Notebook) Exportation de la grille et des définitions dans un fichier HTML interactif simple.

## Prérequis

*   Python 3.8 ou supérieur
*   pip
*   Un fichier dictionnaire `dictionnaire.txt` contenant une liste de mots, un par ligne
*   Une clé API OpenAI valide.

## Installation

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/jsboigeEpita/2025-Epita-Programmation-par-Contraintes.git
    cd Mots-croises
    ```

2.  **Installez les dépendances :**
    ```bash
    pip install ortools openai
    ```
    Optionnel, pour utiliser le notebook :
    ```bash
    pip install jupyterlab notebook jupytext
    ```

4.  **Placez le fichier dictionnaire :**
    Placez le fichier dictionnaire nommé `dictionnaire.txt`

5.  **Configurez la clé API OpenAI :**
    Placez votre clé API OpenAI dans `definitions.py`
    ```python
    OPENAI_API_KEY = "VOTRE_CLE_API_ICI"
    ```

## Configuration

Vous pouvez ajuster les paramètres suivants :

*   `rows`, `columns`: Dimensions de la grille (par défaut 6x6).
*   `dictionnaire_mots`: Chemin vers le fichier dictionnaire.
*   `longueur_min_mot`: Longueur minimale des mots à placer dans la grille.
*   `OPENAI_API_KEY`: Votre clé secrète OpenAI.

## Utilisation

### Via le Script Python

Exécutez le script principal depuis votre terminal :

```bash
python generateur_mots_croises.py
```

Le script va :

Générer et afficher la structure de la grille vide.

Tenter de trouver une solution en remplissant la grille.

Si une solution est trouvée :

Appeler l'API OpenAI pour générer les définitions.

Afficher les définitions (Horizontal / Vertical).

Demander confirmation avant d'afficher la grille remplie.
