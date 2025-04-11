# 1. Introduction Générale

Le jeu de plateau *Quoridor* est un jeu de stratégie combinatoire abstrait pour deux ou quatre joueurs. Chacun des joueurs tente d’atteindre le côté opposé du plateau en déplaçant un pion, tout en posant des murs pour bloquer la progression de l’adversaire. La particularité du jeu réside dans l’alternance entre le mouvement du pion et le placement stratégique de murs limités en nombre. L’aspect spatial, combiné à une logique de cheminement et de blocage, en fait un jeu idéal pour la mise en œuvre de techniques d’intelligence artificielle.

# 2. Objectif du Projet

Le présent projet s'inscrit dans le cadre de la conception d'une intelligence artificielle (IA) jouant à un jeu inspiré de *Quoridor*, un jeu de stratégie à deux joueurs. L'objectif principal est de développer une IA capable d'évaluer, d'explorer et de choisir les coups les plus judicieux dans un environnement où la pose de murs peut modifier dynamiquement le chemin optimal vers la victoire. La particularité de ce jeu réside dans sa composante spatiale et dans la nécessité d'anticiper les coups adverses tout en gérant les ressources limitées que sont les murs.

# 3. Architecture du Projet

## 3.1 Structure du backend Java

Le backend Java repose sur le framework Quarkus et suit une architecture REST modulaire. Il est conçu pour gérer des parties de jeu en ligne entre un ou deux joueurs (humain ou IA), en mettant à disposition un ensemble de routes HTTP accessibles via l’interface `QuoridorController`. Cette couche expose les points d’entrée pour créer des utilisateurs, démarrer une partie, rejoindre une session, ou encore envoyer des actions de jeu comme des déplacements ou des placements de murs.

Les composants principaux sont :

- `QuoridorController` : interface REST exposant les routes principales.
- `QuoridorService` : logique métier (vérifications, gestion des états, décisions IA).
- `Games` et `Players` : classes de stockage des données en mémoire (simulateur de base de données).
- `Game` et `Board` : représentation de l’état d’une partie et du plateau.
- `AIService` : moteur de décodage et d’interprétation des fichiers `.quoridor` pour produire les coups de l’IA.
- `AIPlay` : objet encapsulant une décision de l’IA (déplacement ou pose de mur).

Les utilisateurs sont identifiés via un UUID généré lors de leur création. Les parties sont également indexées par UUID. Chaque requête doit inclure l’identifiant du joueur dans l’en-tête X-Player-UUID.

## 3.2 Architecture du Frontend

Le frontend du jeu est une application web statique construite en HTML, CSS et JavaScript. Il interagit directement avec l’API REST du backend Java et fournit une interface fluide et interactive permettant de jouer à Quoridor contre un autre joueur ou une IA.

### Structure du frontend

- `index.html` : point d’entrée principal contenant les éléments DOM pour la navigation, la création ou la visualisation des parties.
- `script.js` : logique JavaScript, appels HTTP vers le backend, affichage dynamique.
- `style.css` : mise en forme de l’application.
- `config.js` : paramètres réseau.

### Fonctionnalités principales

- Page d’accueil : permet de saisir un nom d’utilisateur et de le valider. Si la saisie est invalide, un message d’erreur s’affiche dynamiquement.

- Navigation : une barre supérieure permet de revenir à la page d’accueil, de voir les parties disponibles ou d’en créer une nouvelle.

- Création de partie : l’utilisateur peut sélectionner la taille du plateau, le nombre de murs, l’équipe (joueur 1, joueur 2 ou aléatoire), et lancer la partie avec un bouton dédié.

- Affichage des parties : les parties existantes sont représentées par des miniatures interactives, avec indication des joueurs, du statut et des actions disponibles (rejoindre, observer).

- Affichage d’une partie : une grille dynamique est générée en fonction de la taille du plateau. Les murs et pions sont positionnés selon l’état reçu du backend. Les mouvements sont interprétés et transmis au serveur pour validation.

- Fin de partie : lorsqu’un joueur gagne, une animation spéciale s’affiche, indiquant le gagnant.

L’architecture est pensée pour être entièrement côté client, avec une séparation claire entre la logique métier (dans le backend) et l’interface (dans le frontend). L’approche modulaire rend le projet facilement extensible (par exemple vers une version mobile ou une application Electron).

## 3.3 Architecture du code C

La partie C du projet est responsable de la logique d’intelligence artificielle, de l’encodage des positions et de l’exploration stratégique des coups possibles. Elle produit les fichiers `.quoridor` utilisés ensuite par le backend Java.

### Structure des fichiers en C

- main.c : point d’entrée du programme, utile pour exécuter les tests et générer les fichiers de solutions.

- game.c : contient la logique de validation des coups, des sauts, des placements de murs et les mouvements des joueurs.

- code.c : transforme les positions de jeu en un code numérique unique en utilisant des méthodes mathématiques telles que les coefficients binomiaux.

- layer.c : cœur de l’algorithme de backtracking, construit des arbres de décisions à partir des positions gagnantes et remonte couche par couche les meilleurs coups.

- memory.c : enregistre les résultats calculés pour éviter de recalculer les états identiques.

- queue.c : fournit une file d’attente pour gérer les états à explorer dans les algorithmes.

- utilities.c : fonctions mathématiques ou auxiliaires comme la génération du triangle de Pascal.

### Fonctionnement de l’IA en C

L’approche choisie est un backtracking orienté victoire : on commence par les positions terminales (c’est-à-dire gagnantes), puis on remonte les coups qui y mènent. À chaque état, les coups légaux sont simulés, et le meilleur coup est choisi selon une stratégie minimax très simplifiée (recherche du plus court chemin en nombre de coups).

Les coups sont simulés via la fonction move() (ou place()), puis annulés via backMove() pour explorer tous les scénarios. L'état de chaque position est encodé, comparé à la mémoire, puis inscrit dans une base structurée par couches.

Le résultat de ce calcul massif est exporté dans des fichiers .quoridor structurés par taille de plateau, nombre de murs, et nombre de murs posés (ou profondeur). Ces fichiers sont ensuite utilisés par le backend Java pour fournir instantanément une réponse IA.

---

# 4. Stratégie de Conception de l'IA

La conception de l’intelligence artificielle de ce projet repose sur une approche déterministe fondée sur l’analyse exhaustive des états du jeu. L’objectif n’est pas seulement de simuler un comportement plausible, mais de fournir des coups optimaux à chaque situation rencontrée, à partir d’un calcul effectué en amont.

## 4.1 Philosophie

L’IA n’est pas construite de manière dynamique par apprentissage ou heuristique. Elle repose sur une analyse statique complète de l’arbre des possibilités, effectuée en langage C, et stockée dans des fichiers .quoridor utilisés ensuite à chaud par le backend Java. Cette séparation permet d’obtenir un comportement IA immédiat et fiable, car les choix sont pré-calculés.

## 4.2 Origine de la stratégie

Le principe est de partir des positions finales gagnantes (par exemple un joueur ayant atteint sa ligne d’arrivée) et de remonter tous les coups possibles qui y mènent. Ce backtracking permet de construire un arbre inversé des coups menant à la victoire.

Chaque coup est évalué en fonction du nombre de coups restants pour gagner. À chaque étape, le coup choisi est celui qui permet de minimiser ce nombre si c’est le tour de l’IA, ou de le maximiser si c’est le tour de l’adversaire (logique inspirée du minimax).

## 4.3 Construction des solutions

Les fichiers .quoridor sont générés pour chaque configuration possible de taille de plateau, nombre de murs, et nombre de murs déjà posés. Chaque fichier contient une table d’actions à effectuer à partir de chaque code d’état. Ces actions peuvent être un déplacement dans une direction donnée (avec ou sans saut), ou un placement de mur à une coordonnée donnée, dans une orientation précise.

Le calcul de ces fichiers prend du temps, mais il n’est effectué qu’une fois, ce qui rend le comportement en ligne de l’IA extrêmement rapide.

## 4.4 Interprétation et exécution des coups

Lorsque le backend Java reçoit une demande de coup IA, il encode l’état courant du plateau dans un identifiant unique (grâce à AIService), puis lit l’action correspondante dans le fichier .quoridor. Cette action est transformée en objet AIPlay, qui est exécuté comme un coup classique dans la partie.

Cette séparation permet à la partie C d’agir comme un moteur de calcul intensif, tandis que le backend Java fournit une interface réseau souple et réactive.

---

# 5. Conclusion

Ce projet démontre une modélisation solide d’un jeu de type Quoridor, avec un frontend et un backend pleinement fonctionnels.

Concernant l’IA, bien que l’infrastructure soit en place, un bug non identifié empêche son fonctionnement final. Elle reste donc à la touche finale du développement.

De nombreux axes d’amélioration sont possibles. Cette séparation permet à la partie C d’agir comme un moteur de calcul intensif, tandis que le backend Java fournit une interface réseau souple et réactive.

FOULIARD Matthieu

(Rapport ecrit a l'aide d'une IA)