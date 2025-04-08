Etudiants : Yahya Ahachim - Léo Lopes

# Rappel du sujet

## 1. Optimisation de plannings infirmiers / Planification d’horaires de personnel soignant

### Description
Ce sujet consiste à résoudre le problème classique de planification du personnel soignant. L’objectif est d’affecter de manière optimale les infirmier·ère·s aux différents shifts (matin, après-midi, nuit) sur une période (hebdomadaire ou mensuelle), tout en respectant un ensemble de contraintes strictes et des préférences :
- **Contraintes légales et organisationnelles :** Respect des durées maximales de travail, nombre maximal de jours consécutifs, jours de repos obligatoires, etc.
- **Contraintes opérationnelles :** Chaque poste doit être pourvu à chaque créneau, avec une couverture adéquate en fonction des besoins du service.
- **Contraintes de préférences et d’équité :** Prise en compte des souhaits individuels et équilibre dans la répartition des shifts.

Ce problème est reconnu comme NP-difficile, ce qui rend l’approche par programmation par contraintes (CSP) particulièrement adaptée pour modéliser et résoudre efficacement l’ensemble des exigences (contraintes dures et souples).

### Modalités du projet
- **Modélisation :** Définir des variables représentant les infirmier·ère·s, les shifts et les jours, avec des domaines correspondant aux affectations possibles.
- **Contraintes :** Imposer les règles de couverture (chaque créneau doit être attribué), les règles de repos et les règles spécifiques (par exemple, interdiction de travailler plus de X jours consécutifs) ainsi que les préférences individuelles (souhaits, équité).
- **Méthodologie :** Utiliser un solveur CSP (ex. OR-Tools CP-SAT, IBM CP Optimizer) ou une approche hybride (CSP + MILP) pour explorer l’espace des solutions.
- **Livrables :** Code opérationnel, dépôt Git avec des commits réguliers, et un notebook explicatif détaillant la modélisation, les choix méthodologiques et l’analyse des résultats.
- **Présentation :** Une présentation orale avec support visuel illustrera la modélisation, l’implémentation et l’évaluation de la solution.

### Références
- Burke et al., *The state of the art of nurse rostering* (2004) – Revue de littérature sur les méthodes d’optimisation des plannings infirmiers.
- P. Laborie et al., *IBM CP Optimizer for staffing problems* (IBM, 2018) – Approche et cas d’utilisation de la programmation par contraintes pour le staffing.
- [Solver Max - Nurse rostering in OR-tools CP-SAT solver](https://www.solvermax.com/resources/models/staff-scheduling/nurse-rostering-in-or-tools-cp-sat-solver#:~:text=This%20is%20a%20classic%20staff,Key%20features%20of%20this%20model) – Exemple de modèle CSP pour générer un tableau de service satisfaisant.
- [Solving the Nurse Rostering Problem using Google OR-Tools](https://medium.com/@mobini/solving-the-nurse-rostering-problem-using-google-or-tools-755689b877c0) – Article détaillé sur la modélisation et la résolution du problème par OR-Tools.
- [Constraint programming for nurse scheduling - IEEE Xplore](https://ieeexplore.ieee.org/document/395324/#:~:text=Constraint%20programming%20for%20nurse%20scheduling,Programming%20for%20solving%20this%20problem) – Étude comparative démontrant l’efficacité de CP pour la planification infirmière.