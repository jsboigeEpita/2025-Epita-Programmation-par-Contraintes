## 7. Calendriers universitaires / Planification d’emploi du temps universitaire

## Sujet
### Description
Ce sujet consiste à concevoir et résoudre le problème de la planification des emplois du temps dans un établissement universitaire (cours ou examens). L'objectif est d'assigner des cours ou examens à des créneaux horaires et des salles en tenant compte de multiples contraintes :
- **Contraintes de ressources :** Disponibilité des enseignants, capacité et disponibilité des salles, et répartition équilibrée des cours.
- **Contraintes temporelles :** Éviter tout conflit horaire pour un même enseignant ou une même salle.
- **Contraintes supplémentaires :** Intégrer des préférences (éviter les cours en fin de journée, par exemple), des contraintes sur la répartition géographique ou des contraintes liées aux groupes d’étudiants.

Ce problème, souvent NP-combinatoire, bénéficie grandement de l'approche CSP qui permet de modéliser de façon déclarative les contraintes et de bénéficier de techniques de propagation pour éliminer rapidement les affectations impossibles.

### Modalités du projet
- **Modélisation :** Définir des variables pour représenter les créneaux horaires et les salles affectées à chaque cours ou examen.
- **Contraintes :**
  - **Exclusion mutuelle :** Aucun enseignant ou salle ne peut être attribué(e) à deux activités simultanément.
  - **Alignement des ressources :** Respecter les capacités des salles et les disponibilités des enseignants.
  - **Contraintes supplémentaires :** Optimiser la répartition pour réduire les conflits et satisfaire au maximum les préférences.
- **Méthodologie :** Utiliser un solveur CSP (par exemple MiniZinc ou OR-Tools) pour générer automatiquement des emplois du temps valides et, le cas échéant, optimiser un critère (minimiser les conflits ou maximiser la satisfaction des préférences).
- **Livrables :** Code opérationnel, dépôt Git, notebook explicatif détaillant la modélisation, la gestion des contraintes et l’analyse des solutions générées.
- **Extensions possibles :** Intégrer des contraintes issues de travaux antérieurs sur la timetabling (ex. règles de répartition géographique, préférences spécifiques des départements) et utiliser des données réelles pour tester la robustesse du modèle.

### Références
- [Constraint Logic Programming over finite domains for timetabling (Citeseerx)](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=00f0110d17de0d95bbbdbea822bebeede956d64e#:~:text=Constraint%20Logic%20Programming%20over%20%0Cnite,satisfy%20speci%0Cc%20conditions%2C%20in%20particular) – Document décrivant l'application du CLP aux emplois du temps.
- [Constraint-based Timetabling](https://www.unitime.org/papers/phd05.pdf#:~:text=Timetabling%20is%20one%20of%20the,a%20set%20of%20desirable%20objectives) – Thèse ou rapport de recherche détaillant les méthodes CP appliquées à la timetabling.
- Goltz & Matzke (1999), *University Timetabling using Constraint Logic Programming* – Exemple d’encodage du problème en CLP et analyse des performances.
- Schaus et al. (2014), *CBLS for Course Timetabling* – Approche basée sur la recherche locale combinée aux contraintes pour l’optimisation des emplois du temps.
- Archives de l’International Timetabling Competition – Ressources et données sur des cas réels de planification universitaire.
