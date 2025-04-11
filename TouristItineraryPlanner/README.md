# 🧭 Planificateur d'Itinéraires Touristiques Personnalisés avec Interface Web

---

## 🧩 Description

Ce projet implémente une solution au **Tourist Trip Design Problem (TTDP)**, qui vise à planifier automatiquement un itinéraire touristique optimal pour une journée dans une ville donnée. Étant donné une liste de points d'intérêt (POI) potentiels (musées, monuments, restaurants...) avec leurs caractéristiques (durée de visite, score d'intérêt, horaires d'ouverture, coût) et un temps total disponible, le système sélectionne un sous-ensemble de POI et détermine l'ordre de visite optimal.

L'objectif principal est de **maximiser la satisfaction du touriste** (mesurée par la somme des scores d'intérêt des lieux visités) tout en respectant diverses contraintes :
*   Fenêtre temporelle globale (heure de début et de fin).
*   Horaires d'ouverture spécifiques à chaque POI.
*   Durée de visite estimée pour chaque POI.
*   Temps de trajet entre les POI consécutifs.
*   Inclusion de visites obligatoires spécifiées par l'utilisateur.
*   Intégration d'un nombre défini de pauses repas (restaurants) dans les créneaux horaires appropriés.
*   Nombre maximum de POI à visiter dans la journée.

Le projet fournit une **interface web conviviale** pour permettre aux utilisateurs de définir facilement leurs préférences et d'obtenir leur itinéraire personnalisé.

---

## ✨ Fonctionnalités Clés

*   **Interface Web Intuitive:** Permet de spécifier la destination, les horaires, le nombre de POI/restaurants, les visites obligatoires et la méthode de calcul de distance.
*   **Génération Automatique de Données:** Utilise l'API OpenAI (GPT-4o/GPT-4o-mini) pour générer des listes de POI (attractions, restaurants) et leurs détails pour une ville donnée si les données ne sont pas déjà disponibles.
*   **Faits Intéressants:** Génère et affiche des "Fun Facts" sur la destination pendant le calcul de l'itinéraire.
*   **Optimisation par Contraintes:** Emploie Google OR-Tools (CP-SAT) pour trouver une solution optimale ou quasi-optimale respectant toutes les contraintes.
*   **Modélisation Flexible:** Gère les horaires d'ouverture variables, les durées de visite, l'inclusion de repas, et les visites imposées.
*   **Objectif d'Optimisation:** Maximise le score d'intérêt total tout en pénalisant le temps de trajet excessif.
*   **Calcul de Distance Flexible:** Offre le choix entre des estimations de temps de trajet via l'API OpenAI (plus précises) ou via la formule Haversine (plus rapide).
*   **Représentation par Graphe:** Modélise la ville et les relations entre POI à l'aide de NetworkX.
*   **Persistance des Données:** Sauvegarde et charge les graphes de villes (`.pkl`) pour éviter les appels API redondants et accélérer les utilisations futures.

---

## 🔍 Intérêt de l’approche par Contraintes (CSP)

Le TTDP est un problème complexe combinant sélection combinatoire (quels lieux visiter ?) et ordonnancement (dans quel ordre ?). La Programmation par Contraintes (CSP), et plus spécifiquement le solveur CP-SAT de Google OR-Tools, est particulièrement bien adaptée pour plusieurs raisons :

1.  **Intégration Naturelle des Contraintes Hétérogènes:** Le formalisme CSP permet de déclarer facilement une grande variété de contraintes : temporelles (horaires, durées, séquencement), logiques (visites obligatoires), cardinalité (nombre max de POI, nombre de restaurants), etc., au sein d'un modèle unique.
2.  **Propagation Efficace:** Les solveurs CP propagent les effets des décisions prises (par exemple, choisir de visiter un lieu à une certaine heure) à travers le réseau de contraintes, permettant d'élaguer très tôt des branches de l'espace de recherche qui mèneraient inévitablement à une impasse (par exemple, si ajouter un lieu dépasse le temps total disponible).
3.  **Optimisation:** Bien que nativement conçus pour la satisfaction, les solveurs CP modernes intègrent des techniques d'optimisation (comme le Branch and Bound) pour trouver la meilleure solution selon un critère donné (ici, maximiser l'intérêt pondéré moins le temps de trajet).
4.  **Modélisation Déclarative:** On décrit *ce que* doit respecter une solution valide, plutôt que *comment* la construire pas à pas, ce qui rend le modèle plus facile à comprendre et à faire évoluer.

Cette approche permet de trouver des solutions de haute qualité, souvent meilleures que des heuristiques simples (comme un algorithme glouton), en explorant intelligemment l'espace des possibilités tout en garantissant le respect de toutes les règles.

---

## 🛠️ Technologies Utilisées

*   **Backend:**
    *   Langage : Python 3.x
    *   Optimisation : Google OR-Tools (CP-SAT)
    *   IA Générative : OpenAI API (Models: `gpt-4o`, `gpt-4o-mini`)
    *   Graphes : NetworkX
    *   Configuration : python-dotenv
    *   Sérialisation : Pickle
    *   Web Framework (Nécessaire pour faire le lien avec le frontend) : Flask / FastAPI / Django (Non fourni dans ce dépôt, à ajouter par l'utilisateur)
*   **Frontend:**
    *   Structure : HTML5
    *   Style : CSS3
    *   Logique : JavaScript (ES6+)
    *   Icônes : Bootstrap Icons

---

## 📁 Structure du Projet
.
├── data/
│ ├── city_graphs/
│ │ ├── paris_graph.pkl
│ │ └── ... (autres villes)
│ └── city_graph.py
├── src/
│ ├── city_generator.py
│ ├── distance_api.py
│ └── solver.py
├── static/
│ ├── script.js
│ └── style.css
├── templates/
│ └── index.html
├── .env
├── notebook.ipynb
├── requirements.txt
├── README.md
└── app.py


---

## 🚀 Installation et Lancement

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/dslalex/TouristItineraryPlanner.git
    cd TouristItineraryPlanner
    ```

2.  **Créer un environnement virtuel (recommandé) :**
    ```bash
    python -m venv venv
    # Sous Windows:
    venv\Scripts\activate
    # Sous macOS/Linux:
    source venv/bin/activate
    ```

3.  **Installer les dépendances Python :**
    *(Assurez-vous d'avoir un fichier `requirements.txt` à jour ou installez manuellement)*
    ```bash
    pip install -r requirements.txt
    # Ou manuellement: pip install openai "google-ortools>=9.0" networkx python-dotenv matplotlib requests
    ```

4.  **Configurer la clé API OpenAI :**
    *   Renommez `.env.example` en `.env`.
    *   Ouvrez le fichier `.env` et remplacez `your_openai_api_key_here` par votre clé API OpenAI réelle.
    ```.env
    OPENAI_API_KEY=sk-VotreCleAPI...
    ```

5.  **Lancer le serveur Backend :**
    *   Vous devez implémenter un serveur web (par exemple, avec Flask dans `app.py`) qui importe et utilise les modules `solver`, `city_generator`, etc., pour répondre aux requêtes `/api/plan` et `/api/fun-facts`.
    *   Exemple de commande de lancement (si vous utilisez Flask dans `app.py`):
        ```bash
        flask run
        # Ou: python app.py
        ```

6.  **Accéder à l'Interface Web :**
    *   Ouvrez votre navigateur web et allez à l'adresse fournie par votre serveur backend (généralement `http://127.0.0.1:5000` ou `http://localhost:5000` pour Flask).

---

## 💡 Utilisation

1.  Ouvrez l'application dans votre navigateur.
2.  Remplissez le formulaire :
    *   **Destination City:** Entrez le nom de la ville (ex: `Rome`, `London`).
    *   **Start Time / End Time:** Définissez la plage horaire de votre journée.
    *   **Maximum Points of Interest:** Choisissez le nombre total de lieux (attractions + restaurants) que vous souhaitez visiter (2-12).
    *   **Number of Restaurants:** Indiquez combien de repas au restaurant vous voulez inclure (0, 1 ou 2).
    *   **Must-Visit Places:** Listez les noms des attractions que vous voulez absolument inclure (séparés par des virgules ou des sauts de ligne, ex: `Colosseum, Vatican Museums`). Le système essaiera de les faire correspondre aux noms dans sa base de données.
    *   **Distance Calculation Method:** Sélectionnez `API` (plus précis, nécessite des appels OpenAI) ou `Haversine Formula` (plus rapide, basé sur la distance à vol d'oiseau).
3.  Cliquez sur "Plan My Itinerary".
4.  Patientez pendant que le système génère les données (si nécessaire) et calcule l'itinéraire optimal. Des faits intéressants sur la ville s'afficheront.
5.  L'itinéraire généré apparaîtra dans la section des résultats.

---

## ⚙️ Configuration

La configuration principale se fait via le fichier `.env` à la racine du projet :

*   `OPENAI_API_KEY`: Votre clé API OpenAI est **requise** pour la génération de données et potentiellement pour le calcul des temps de trajet (si l'option API est choisie).

---

## 🔄 Fonctionnement Interne (Workflow)

1.  L'utilisateur soumet le formulaire via l'**interface web** (`index.html`).
2.  Le **JavaScript** (`script.js`) envoie les paramètres aux endpoints `/api/plan` et `/api/fun-facts` du serveur backend via des requêtes `fetch`.
3.  Le **serveur backend** (Flask/FastAPI - `app.py`) reçoit les requêtes.
4.  Pour `/api/fun-facts`, il appelle `city_generator.generate_city_fun_facts` et renvoie les faits.
5.  Pour `/api/plan`:
    *   Il vérifie si le graphe pour la ville demandée existe (`city_graph.load_graph`).
    *   Si non, il appelle `city_generator.generate_city_data` (qui utilise l'API OpenAI) pour créer et sauvegarder le graphe.
    *   Il instancie `solver.TouristItinerarySolver` avec les paramètres de l'utilisateur et le graphe chargé/généré.
    *   Le `Solver` pré-calcule les voisins et les temps de trajet préférés (utilisant `distance_api.DistanceCalculator` - API ou Haversine).
    *   Le `Solver` construit et résout le modèle CP-SAT avec `ortools`.
    *   Le `Solver` renvoie la solution (ou une indication d'échec) au backend.
6.  Le **backend** formate la réponse (itinéraire textuel ou erreur) en JSON.
7.  Le **JavaScript** reçoit la réponse et met à jour l'interface web pour afficher le résultat.

---

## ⚠️ Limitations Connues

*   **Précision des Données LLM:** Les données générées (coordonnées, horaires, durées) peuvent parfois être imprécises ou obsolètes.
*   **Estimation des Temps de Trajet:** Les temps de trajet (API ou Haversine) sont des estimations et ne tiennent pas compte du trafic en temps réel, des aléas des transports, etc.
*   **Performance du Solveur:** Pour un très grand nombre de POI potentiels ou des contraintes très complexes, le temps de calcul peut augmenter significativement.
*   **Interface Utilisateur:**
    *   Pas de visualisation sur carte de l'itinéraire.
    *   La correspondance des "Must-Visit Places" textuels peut être fragile.
    *   Pas de modification interactive de l'itinéraire après génération.
*   **Dépendance API:** Nécessite une clé API OpenAI valide et potentiellement payante.

---

## 📚 Références

*   Vu, D. M., Lodi, A., & Mendoza, J. E. (2021). Branch-and-Check Approaches for the Tourist Trip Design Problem with Rich Constraints. *Transportation Science*, 55(5), 1115-1137. [*(Lien possible vers l'article ou la page de requête PDF)*]
*   Souffriau, W., Vansteenwegen, P., Vanden Berghe, G., & Van Oudheusden, D. (2010). A constraint programming approach for the tourist trip design problem. *Proceedings of the 7th International Conference on the Practice and Theory of Automated Timetabling (PATAT 2008)*.
*   Vansteenwegen, P., Souffriau, W., & Van Oudheusden, D. (2011). The orienteering problem: A survey. *European Journal of Operational Research*, 209(1), 1-10.
*   Google OR-Tools Documentation: [https://developers.google.com/optimization](https://developers.google.com/optimization)
*   OpenAI API Documentation: [https://platform.openai.com/docs](https://platform.openai.com/docs)