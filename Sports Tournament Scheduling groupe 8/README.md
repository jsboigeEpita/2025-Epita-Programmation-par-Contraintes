## Projet Programmation par Contraintes - Calendrier sportif (Sports Tournament Scheduling)
Élaboration du calendrier de rencontres d’un championnat (par ex. tournoi toutes rondes en football), en respectant de multiples contraintes: alternance domicile/extérieur, disponibilités de stades, équité entre équipes (pas plus de X déplacements consécutifs, etc.). Ces problèmes, très complexes, ont motivé de nombreux travaux en CP. Par exemple, l’ordonnancement d’un tournoi « round-robin » peut se modéliser par contrainte avec des variables représentant qui rencontre qui à chaque journée, et des *global constraints* pour éviter les « breaks » (deux matchs Domicile ou Extérieur de suite) ([sls.dvi](http://cse.unl.edu/~choueiry/Documents/Regin/minbreak.pdf#:~:text=consider%20single%20round,to%20e%0Eciently%20prove%20this%20result)). La CP a permis de prouver des bornes théoriques, comme le nombre minimal de « breaks » (n–2 pour n équipes) en quelques secondes, exploitant la propagation sur des contraintes globales spécifiques ([sls.dvi](http://cse.unl.edu/~choueiry/Documents/Regin/minbreak.pdf#:~:text=once%20during%20all%20the%20periods,powerful%20%0Cltering%20algorithms%20are%20associated)). Plus généralement, la littérature sur le scheduling sportif montre l’intérêt de CP pour gérer les règles complexes imposées par les ligues ([sls.dvi](http://cse.unl.edu/~choueiry/Documents/Regin/minbreak.pdf#:~:text=Sport%20scheduling%20problems%20is%20an,Some%20systems%20dedicated%20to)).  
**Références :** Régin (CP 2008), *Minimizing breaks in sports schedules* – modèle CP pour tournoi rondes simples ([sls.dvi](http://cse.unl.edu/~choueiry/Documents/Regin/minbreak.pdf#:~:text=consider%20single%20round,to%20e%0Eciently%20prove%20this%20result)) ([sls.dvi](http://cse.unl.edu/~choueiry/Documents/Regin/minbreak.pdf#:~:text=once%20during%20all%20the%20periods,powerful%20%0Cltering%20algorithms%20are%20associated)); Schaerf (1999), *Sports scheduling* – revue d’approches; *ITC 2021 Sports Scheduling Track* (compétition utilisant CP et métaheuristiques).

Ce projet vise à résoudre ce problème complexes de planification en utilisant des techniques de **Programmation par Contraintes (CSP)** et des outils avancés comme **OR-Tools**, **Choco Solver**, et **Z3**.


## Structure du Projet

Voici une description des principaux dossiers et fichiers du projet :

### Racine du projet
- **`requirements.txt`** : Liste des dépendances Python nécessaires pour exécuter le projet.

### Dossiers principaux

#### `choco/`
Contient les implémentations utilisant **Choco Solver** (Java).
- **`src/main/java/org/example/`** : Code source Java, incluant le fichier principal `Main.java` et l'algorithme `RoundRobinScheduler.java`.
- **`pom.xml`** : Fichier Maven pour gérer les dépendances et compiler le projet.
- **`test/`** : Scripts de test et utilitaires pour valider les solutions générées.
- **`output.txt`** : Exemple de sortie générée par Choco Solver.

#### `or/`
Contient les implémentations utilisant **OR-Tools** (Python).
- **`entities/`** : Classes représentant les entités principales (`Team`, `Stadium`, `Schedule`).
- **`utils/`** : Fonctions utilitaires pour résoudre les problèmes et gérer les configurations.
- **`solver.py`** : Exemple d'utilisation pour générer un calendrier.
- **`benchmark.py`** : Script pour évaluer les performances de l'algorithme sur différentes tailles de tournoi.
- **`llm-solver.py`** : Script pour executer le solver avec chatGPT. 

#### `Z3/`
Contient les implémentations utilisant **Z3 Solver** (Python).
- **`or-toos.py`** : Implémentation d'un solveur de tournoi round-robin avec Z3.
- **`script.py`** : Exemple d'utilisation de Z3 pour générer un calendrier.

---

## Prérequis

### Pour les implémentations Python :
- **Python 3.8+**
- Installer les dépendances avec :
  ```bash
  pip install -r requirements.txt

## Pour les implémentations Java :
- **Java 17+**
- Maven pour gérer les dépendances.

Comment Lancer le Projet
### Utilisation avec OR-Tools (Python)
- Naviguez dans le dossier racine du projet.
- Exécutez un solveur avec :
    ```py
    python or/solver.py

- Pour exécuter un benchmark :
    ```py
    python or/benchmark.py
### Utilisation avec Choco Solver (Java)
- Naviguez dans le dossier choco/.
- Compilez et exécutez le projet avec Maven :
### Utilisation avec Z3 (Python)
- Naviguez dans le dossier Z3/.
- Exécutez le script avec :
    ```py
    python script.py
## Fonctionnalités Principales
- Génération de calendriers sportifs : Création de tournois round-robin avec des contraintes personnalisées.
- Minimisation des "breaks" : Réduction des séquences consécutives de matchs à domicile ou à l'extérieur.
- Support multi-solveurs : Implémentations disponibles en Python (OR-Tools, Z3) et Java (Choco Solver).
- Benchmarks : Évaluation des performances des algorithmes sur différentes tailles de tournoi.

## Auteurs : 
Alexis, Aniss, Pierre, Rick

