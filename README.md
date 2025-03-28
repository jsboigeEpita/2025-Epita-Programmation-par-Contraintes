# Projet d'Ordonnancement de Prises de Vue Satellite par Contraintes

## 1. Objectif du Projet

Concevoir et implémenter une solution d'ordonnancement (scheduling) par contraintes (CSP) pour planifier efficacement les prises de vue et les opérations de communication d'un satellite d'observation de la Terre. L'objectif est de maximiser la somme des priorités des tâches réalisées tout en respectant les contraintes opérationnelles, orbitales et de ressources.

## 2. Contexte et Enjeux

Les agences spatiales reçoivent de nombreuses requêtes d'images couvrant des zones géographiques variées. En raison de limitations techniques et opérationnelles, le satellite ne peut réaliser qu'un nombre limité d'observations par orbite. Il est donc crucial de :

- Sélectionner les observations les plus prioritaires.
- Planifier précisément le début de chaque observation.
- Optimiser l'utilisation des ressources à bord (mémoire, énergie) et au sol (stations de téléchargement).
- Respecter les contraintes liées à la visibilité des cibles et aux délais de communication.

## 3. Contraintes du Système

1. **Position du Satellite** : Le satellite doit être au-dessus de la zone à photographier.
2. **Calibration de la Lentille** : La lentille doit être calibrée avant chaque prise de vue.
3. **Taille de la Zone** : La taille de la zone photographiée influence la taille de la photo et donc le temps d'envoi sur Terre.
4. **Énergie du Satellite** : Le satellite doit avoir suffisamment de batterie pour fonctionner toute la nuit.
5. **Priorité des Prises de Vue** : Chaque prise de vue a une priorité (échelle de 3 à 1).
6. **Tâche Unique** : Le satellite ne peut pas prendre de photos et les envoyer simultanément.
7. **Allocation de Ressources** : La mémoire du satellite est limitée (ex : 5 Go) et la taille d'une photo dépend de la taille de la zone photographiée.
8. **Durée de la Prise de Vue** : La taille de la zone influence la durée de la prise de vue.
9. **Débit d'Upload** : Le débit d'upload influence le temps d'envoi des clichés.
10. **Temps de Recalibration** : Le temps nécessaire pour recalibrer la lentille doit être pris en compte.

### Objectif

Maximiser la somme des priorités des clichés pris en respectant les contraintes mentionnées.

## 4. Approche Méthodologique – Programmation par Contraintes (CSP)

L'utilisation de la programmation par contraintes est recommandée pour les raisons suivantes :

- Unifier et modéliser l'ensemble des contraintes opérationnelles (visibilité, ressources, temporelles, précédence).
- Exploiter la propagation des contraintes pour éliminer rapidement des combinaisons impossibles et réduire l'espace de recherche.
- Optimiser un critère objectif (ex. la somme des priorités) tout en fournissant, si nécessaire, des preuves de l'optimalité ou des alternatives exploitables par les opérateurs.
- Faciliter l'extension du modèle en cas d'ajout de nouvelles contraintes (nouveau satellite, indisponibilités ponctuelles, etc.) sans nécessiter de réécriture complète des heuristiques.

Des systèmes et frameworks existants (comme SPIKE du CNES ou EUROPA de la NASA) démontrent que cette approche est efficace pour la gestion d'ordonnancements complexes, y compris pour des configurations comprenant plusieurs satellites et stations sol.

## 5. Intégration LLM pour l'Ordonnancement de Prises de Vue Satellite

### Contexte

L'intégration d'un Large Language Model (LLM) facilite l'interaction avec le système d'ordonnancement de prises de vue satellite en utilisant le langage naturel. L'objectif est de permettre aux utilisateurs de spécifier leurs besoins de manière intuitive, tout en maximisant la somme des priorités des clichés pris.

### Fonctionnement

1. **Demande de l'Utilisateur** :
    - Exemple : "Je veux au plus vite les clichés de Tokyo avec une priorité de 3 et de Montréal avec une priorité de 2."
2. **Traitement de la Demande** :
    - Le LLM extrait les informations pertinentes : `{"Tokyo": 3, "Montréal": 2}`
3. **Récupération des Coordonnées GPS** :
    - Fonction : `get_gps_coordinates(["Tokyo", "Montréal"])`
    - Sortie : `{"Tokyo": [35.6895, 139.6917], "Montréal": [45.5017, -73.5673]}`
4. **Planification des Prises de Vue** :
    - Fonction : `plan_satellite_shots({"Tokyo": [35.6895, 139.6917], "Montréal": [45.5017, -73.5673]}, {"Tokyo": 3, "Montréal": 2})`
    - Sortie : Plan de prises de vue optimisé avec les heures et les priorités.

### Exemple d'Utilisation

1. **Demande de l'Utilisateur** :
    - "Je veux au plus vite les clichés de Tokyo avec une priorité de 3 et de Montréal avec une priorité de 2."
2. **Traitement de la Demande** :
    - Le LLM extrait les informations : `{"Tokyo": 3, "Montréal": 2}`
3. **Récupération des Coordonnées GPS** :
    - Réponse : `{"Tokyo": [35.6895, 139.6917], "Montréal": [45.5017, -73.5673]}`
4. **Planification des Prises de Vue** :
    - Réponse : Plan de prises de vue optimisé.

## 6. Références et Inspirations Techniques

- Frank et al. (NASA Ames) – "Constraint-based Scheduling for Space Missions" décrivant l’architecture d’EUROPA.
- Jussien & Laas (ONERA) – Études sur la planification efficace des changements d’instruments d’un satellite via CP.
- DIMACS’98 – Publication formelle introduisant le problème d’ordonnancement satellite en tant que CSP, avec application aux constellations orbitantes.