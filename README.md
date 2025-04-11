## SUJET : 23.Planification de tâches multi-robots dans un entrepôt

**Description :** On considère une flotte de robots mobiles (par ex. des robots de manutention dans un entrepôt) devant accomplir un ensemble de tâches (transporter des objets, préparer des commandes) dans des délais impartis. Le problème consiste à assigner les tâches aux robots et à planifier l’ordonnancement de celles-ci, en gérant les contraintes de disponibilité des robots, d’évitement de collisions (deux robots ne doivent pas se trouver au même endroit en même temps), et d’énergie (retours à la base pour recharger). Ce problème de **planification et ordonnancement multi-robots** est très complexe, car il combine l’affectation (qui fait quoi) et l’ordonnancement dans le temps, souvent avec des contraintes de chemins. Par exemple, dans un centre de retrait de colis, on doit planifier pour chaque robot une suite d’actions (aller à telle étagère, déposer l’objet à telle station) en s’assurant que les chemins ne se croisent pas dangereusement et que les deadlines sont respectées ([(PDF) A Constraint Programming Approach to Multi-Robot Task Allocation and Scheduling in Retirement Homes](https://www.researchgate.net/publication/306387267_A_Constraint_Programming_Approach_to_Multi-Robot_Task_Allocation_and_Scheduling_in_Retirement_Homes#:~:text=We%20study%20the%20application%20of,our%20initial%20CP%20approach%20using)) ([](https://icaps16.icaps-conference.org/proceedings/dc/abstracts/booth.pdf#:~:text=work%20on%20a%20single,based)).

**Intérêt de l’approche CSP :** La programmation par contraintes (souvent couplée à des techniques de planification) a montré de très bons résultats pour ce type de problème, notamment en fournissant **des solutions optimisées respectant rigoureusement toutes les contraintes**. Par exemple, une approche CP a surpassé les MILP (programmation linéaire) classiques sur un cas de planification de robots d’assistance en maison de retraite, en trouvant des solutions de haute qualité beaucoup plus rapidement ([](https://icaps16.icaps-conference.org/proceedings/dc/abstracts/booth.pdf#:~:text=work%20on%20a%20single,based)). Un modèle CSP permet d’intégrer naturellement des contraintes temporelles disjointes, des dépendances entre tâches (ne pas commencer la tâche B avant que A soit terminée par un autre robot), et les niveaux de batterie de chaque robot ([(PDF) A Constraint Programming Approach to Multi-Robot Task Allocation and Scheduling in Retirement Homes](https://www.researchgate.net/publication/306387267_A_Constraint_Programming_Approach_to_Multi-Robot_Task_Allocation_and_Scheduling_in_Retirement_Homes#:~:text=We%20study%20the%20application%20of,our%20initial%20CP%20approach%20using)). Grâce à des stratégies de recherche adaptées (ordre de variable, *large neighborhood search* combiné avec CP…), on peut résoudre des instances réalistes et même obtenir toutes les solutions stables. L’approche CSP apporte également de la **flexibilité** : si une nouvelle contrainte apparaît (par exemple, un robot ne peut pas aller dans une certaine zone temporairement), on l’ajoute au modèle et le solveur recalculera un planning valide, plutôt que de devoir redévelopper un algorithme dédié.

## Architecture du Projet

Le projet est organisé en plusieurs dossiers principaux :

### 1. **Backend**

- **Chemin** : `backend/`
- Contient la logique principale pour la simulation des robots, la planification des tâches, et l'API exposée au frontend.
- **Technologies** : Python (Flask, OR-Tools)
- **Fichiers clés** :

  - `robots_ortools_3.py` : Contient les algorithmes de planification et de visualisation.
  - `collision_free.py` : Gère les déplacements sans collision des robots.

### 2. **Frontend**

- **Chemin** : `frontend/robot-simulation/`
- **Description** :
  Le frontend est une interface utilisateur développée avec React pour visualiser les simulations et interagir avec le système.
- **Technologies** : React, Vite, Tailwind CSS

### Rapport de projet

* ``rapport_implementation.pdf``

### Jeu de slides

* ``slides.pdf``
