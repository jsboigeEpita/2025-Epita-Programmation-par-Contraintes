# Projet Programmation Par Contraintes

## Utiliser l'outil d'optimisation
1. Lancer le server python contenant les algorithmes:

    - (recommandé) créer un environnement python
    - pip install -r requirements.txt
    - cd frameword && python3 server.py

2. Lancer le frontend React:

    - cd dashboard
    - npm install
    - npm run dev

## Sujet 18: Optimisation de portefeuille financier sous contraintes  
Sélection d’un ensemble d’investissements (actions, actifs) maximisant le rendement attendu pour
un niveau de risque donné, en respectant diverses contraintes (budget maximum, limites par
secteur, etc.). Le problème se ramène souvent à une optimisation combinatoire (et continue) où
l’on décide quelles fractions du capital allouer à chaque actif. On peut modéliser cela en CP/MILP
en introduisant des variables entières (nombre d’unités de chaque actif) ou booléennes (actif
sélectionné ou non) avec des contraintes de budget et de diversification, et en maximisant une
fonction d’utilité (rendement moins pénalité de risque). Par exemple, un modèle CP-SAT peut utiliser
des variables entières pour chaque produit financier (avec bornes min/max d’investissement) et ajouter
des contraintes de type knapsack et d’allocation ([algorithm - Portfolio optimization problem:
improving the O(n!) solution - Stack Overflow](https://stackoverflow.com/questions/73184010/portfolio-optimization-problem-improving-the-on-solution#:~:text=indicator%20%3D%20solver.BoolVar%28,Solve)),
l’objectif étant de maximiser le profit total ([algorithm - Portfolio optimization problem: improving the O(n!) solution - Stack Overflow](https://stackoverflow.com/questions/73184010/portfolio-optimization-problem-improving-the-on-solution#:~:text=3)).
Grâce aux solveurs modernes, ce type de problème (combinatoire non linéaire approché linéairement)
peut être résolu sur des portefeuilles de taille raisonnable, offrant une solution optimale respectant
strictement les contraintes de gestion du risque.  

**Références :** Markowitz (1952), *Portfolio Selection* – modèle moyenne/variance; StackOverflow (2022) – formulation d’un portefeuille en CP-SAT (OR-Tools) ([algorithm - Portfolio optimization problem: improving the O(n!) solution - Stack Overflow](https://stackoverflow.com/questions/73184010/portfolio-optimization-problem-improving-the-on-solution#:~:text=3)) ([algorithm - Portfolio optimization problem: improving the O(n!) solution - Stack Overflow](https://stackoverflow.com/questions/73184010/portfolio-optimization-problem-improving-the-on-solution#:~:text=indicator%20%3D%20solver.BoolVar%28,Solve)); Michalewicz & Fogel (2000), *How to Solve It: Modern Heuristics* – chapitre sur optimisation financière.

Les [publications suivantes](https://drive.google.com/file/d/1KPokq-5Z_aj_T5ysXyqnFebaoefpKU-6/view?usp=sharing) constituent un ensemble de ressources variées introduisant le problème d'optimisation de portefeuille financier sous contrainte et différentes techniques autour de la programmation par contrainte.
