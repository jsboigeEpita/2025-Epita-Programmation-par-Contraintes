# 7. Planification d'Emplois du Temps Universitaires

- Maxime Cambou
- Dimitri Calmand
- Jules Raitiere-Delsupexhe

## Introduction

Ce projet vise à appliquer les méthodes de programmation par contraintes (CSP) pour résoudre le problème de la planification des emplois du temps universitaires. Nous utilisons un solveur CSP pour générer des emplois du temps valides en tenant compte de diverses contraintes.

## Modélisation du Problème

### Variables
- Créneaux horaires
- Salles
- Cours/Examens
- Enseignants

### Contraintes
1. Respecter le nombre d'heures par matière par semaine
2. Une classe ne peut pas avoir deux cours en même temps
3. Une salle ne peut pas être utilisées par deux cours en même temps
4. Une matière ne peut pas être enseigné dans deux classes en même temps par un même enseignant
5. Pas plus de deux heures de cours d'affilé
6. Un cours de deux heures doit prendre place dans la même salle pendant les deux heures
7. Une classe doit avoir un seul professeur par matière

### Minimisation
8. Minimiser les trous dans l'emploi du temps pour les élèves
9. Minimiser les cours de fin de journée (de 17h à 18h)
10. Minimiser les cours d'une seule heure, favoriser les cours de deux heures

### Choix du Solveur
- OR-Tools

### Définition des données du problème
- Matières et nombre d'heures hebdomadaires
- Enseignants et matières attribuées
- Créneaux horaires disponibles
- Nombre de classes et salles

### Création du modèle CSP
- Création des variables : matières, créneaux horaires, classes, salles
- Définition des contraintes
- Minimisation des trous, des cours tardifs, et favorisation des cours de deux heures

### Résolution du Problème
- Exécution du solveur avec une limite de temps
- Affichage des résultats pour chaque classe

## Interface Graphique :

Une interface graphique est disponible, pour permettre à l'utilisateur de personnaliser et visualiser plus facilement.
Pour lancer l'interface, exécutez le script `gui/main.py`.
## Conclusion :
Ce projet démontre l'application des méthodes de programmation par contraintes pour résoudre un problème complexe de planification d'emplois du temps universitaires. Le modèle peut être adapté et étendu pour inclure d'autres contraintes ou préférences spécifiques.
