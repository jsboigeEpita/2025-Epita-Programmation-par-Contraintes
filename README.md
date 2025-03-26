# Projet Programmation par Contraintes

## Introduction

Ce projet a pour but de vous permettre d'appliquer concrètement les méthodes et outils vus en cours sur les problématiques de recherche (Search), de programmation par contraintes (CSP), et de raisonnement logique avancé (SAT/SMT). Vous serez amenés à résoudre des problèmes réels ou réalistes à l'aide de ces techniques en développant un projet complet, depuis la modélisation jusqu'à la solution opérationnelle.


## Modalités du projet

### Livrables

Chaque groupe devra forker ce dépôt  Git et déposer son travail dans un répertoire dédié du dépôt. Ce répertoire contiendra :

- Le code source complet, opérationnel, documenté et maintenable (en Python, C#, C++, ou autre).
- Le matériel complémentaire utilisé pour le projet (datasets, scripts auxiliaires, etc.).
- Les slides utilisés lors de la présentation finale.
- Un notebook explicatif détaillant les étapes du projet, les choix de modélisation, les expérimentations et les résultats obtenus.

Les livraisons se feront via des **pull requests**, qui devront être régulièrement mises à jour durant toute la durée du projet de sorte que l'enseignant puisse suivre l'avancement et éventuellement apporter des retours et de sorte que tous les élèves aient pu prendre connaissance des travaux des autres groupes avant la soutenance avec évaluation collégiale.

### Présentation

- Présentation orale finale avec support visuel (slides).
- Démonstration de la solution opérationnelle devant la classe.

### Évaluation

- Évaluation collégiale : chaque élève évaluera les autres groupes en complément de l’évaluation réalisée par l’enseignant.
- Critères : clarté, originalité, robustesse de la solution, qualité du code, pertinence des choix méthodologiques et organisation.

## Utilisation des LLMs

### Outils à disposition

Pour faciliter la réalisation du projet, vous aurez accès à plusieurs ressources avancées :

- **Plateforme Open-WebUI** : intégrant des modèles d'intelligence artificielle d'OpenAI et locaux très performants, ainsi que des plugins spécifiques et une base de connaissances complète alimentée par la bibliographie du cours (indexée via ChromaDB, taper # en conversation pour invoquer les KB).
- **Clés d'API OpenAI et locales** : mise à votre disposition pour exploiter pleinement les capacités des modèles GPT dans vos développements.
- **Notebook Agentique** : un notebook interactif permettant d'automatiser la création ou la finalisation de vos propres notebooks, facilitant ainsi la structuration et l'amélioration de vos solutions.

### Combinaison LLM et CSP

Vous avez également la possibilité d'intégrer les Large Language Models (LLMs) directement dans votre projet CSP afin d'en étendre significativement les capacités, via :

- Une utilisation directe des LLM pour assister la conception ou la résolution de CSP complexes.
- Le recours au "function calling" : fournir à un LLM un accès direct à votre CSP, permettant ainsi au modèle de piloter la résolution du problème de manière plus flexible et intuitive. Le notebook agentique fourni constitue un exemple pratique et efficace de cette méthodologie légère mais puissante. La normalisation en cours des MCPs constitue également un excellent exemple d'application de cette approche (vous développez un MCP utilisant la PrCon dans le cadre de votre projet).

# Ordonnancement de missions satellites (Satellite Scheduling)  
**Description :** Les agences spatiales font face au problème d’ordonnancer les **prises de vue et communications** de leurs satellites. Un satellite d’observation de la Terre, par exemple, a une liste de requêtes d’images à prendre de différentes zones géographiques, mais il ne peut en réaliser qu’un nombre limité par orbite (contraintes de visibilité des cibles, de mémoire embarquée, de disponibilité d’une station pour télécharger les données, etc.). Il faut donc sélectionner quelles observations effectuer et planifier à quel moment, en respectant les contraintes orbitales (fenêtres de visibilité de chaque cible) et de ressource (un satellite ne peut faire qu’une tâche à la fois, il a une capacité mémoire limitée, il doit parfois orienter ses instruments ce qui prend du temps, etc. ([DIMACS final version D.PDF](https://www2.cs.sfu.ca/CourseCentral/827/havens/papers/topic%2312(SatelliteScheduling)/dimacs98.pdf#:~:text=2%20Constraint,variables%2C%20and%20a%20set%20of)) ([DIMACS final version D.PDF](https://www2.cs.sfu.ca/CourseCentral/827/havens/papers/topic%2312(SatelliteScheduling)/dimacs98.pdf#:~:text=We%20view%20this%20scheduling%20task,scheduling))】. C’est un problème d’ordonnancement avec ressources multiples et contraintes temporelles, très complexe étant donné les interactions (certaines observations périodiques, priorités, etc.).  

**Intérêt de l’approche CSP :** La programmation par contraintes a été appliquée avec succès à ces problèmes dès les années 90, intégrée dans des systèmes comme **SPIKE** au CNES ou le framework EUROPA de NASA. Le **modèle CSP** permet d’unifier la gestion des différentes contraintes : on représente les créneaux possibles pour chaque tâche (prise de vue) comme des variables temporelles, on impose que deux tâches ne peuvent se chevaucher sur le même satellite ou la même station sol, on inclut des contraintes de précédence (par ex. *le téléchargement doit se faire après la prise d’image correspondante*), etc ([DIMACS final version D.PDF](https://www2.cs.sfu.ca/CourseCentral/827/havens/papers/topic%2312(SatelliteScheduling)/dimacs98.pdf#:~:text=We%20view%20this%20scheduling%20task,scheduling))】. Grâce à la propagation de contraintes, de nombreuses combinaisons impossibles sont éliminées d’emblée (ex. deux tâches dont les fenêtres de temps ne se croisent pas ne seront jamais planifiées sur le même passage de satellite). L’approche CSP permet aussi d’**optimiser** un critère, typiquement maximiser la somme des priorités des tâches réalisées. Des solveurs dédiés (ou des bibliothèques CP générales) ont ainsi permis d’automatiser une grande partie de la planification satellitaire, avec une flexibilité pour intégrer de nouvelles contraintes d’exploitation (ajout d’un nouveau satellite, périodes d’indisponibilité, etc. simplement en mettant à jour les données de contraintes) – alors qu’autrement chaque nouveau cas particulier nécessiterait de recoder des heuristiques. Enfin, la recherche par contraintes peut fournir non seulement une solution, mais aussi des preuves d’optimalité ou des alternatives (pour permettre aux opérateurs de comparer plusieurs plannings valides en fonction de critères secondaires).  

**Références :** *Frank et al.* (NASA Ames), **Constraint-based Scheduling for Space Missions** – détaille l’architecture d’EUROPA, qui utilise un noyau CSP pour planifier des missions complexes (rovers martiens, satellites) en gérant des contraintes d’événements, de ressources et de temps. *Jussien & Laas (Onera)*, **Scheduling Satellite modes with CP* ([[PDF] Scheduling Running Modes of Satellite Instruments Using ... - Onera](https://www.onera.fr/sites/default/files/u518/cp15.pdf#:~:text=Constraint%20Programming%20,more%20challenging%20for%20space))】 – montre que les changements d’instruments d’un satellite peuvent être planifiés efficacement via CP malgré l’accroissement de la complexité. *DIMACS’98 Paper – Constraint-Based Satellite Scheduling ([DIMACS final version D.PDF](https://www2.cs.sfu.ca/CourseCentral/827/havens/papers/topic%2312(SatelliteScheduling)/dimacs98.pdf#:~:text=2%20Constraint,variables%2C%20and%20a%20set%20of)) ([DIMACS final version D.PDF](https://www2.cs.sfu.ca/CourseCentral/827/havens/papers/topic%2312(SatelliteScheduling)/dimacs98.pdf#:~:text=We%20view%20this%20scheduling%20task,scheduling))】 – introduit formellement le problème comme un CSP (variables = tâches avec start/duration, contraintes de ressources et de visibilité, etc.) et décrit une implémentation qui a réussi à planifier des constellations de satellites en respectant l’ensemble des contraintes opérationnelles.  

## 34. Participation à une compétition CP/SAT/SMT : Algorithmes ou benchmarks

**Contexte** :  
Chaque année, plusieurs compétitions internationales dédiées à la résolution de problèmes de satisfaction de contraintes (CP), problèmes de satisfiabilité booléenne (SAT), et problèmes de satisfiabilité modulo théories (SMT) sont organisées. Ces compétitions visent à évaluer les progrès réalisés par la communauté scientifique sur des méthodes de résolution efficaces, innovantes, et robustes. Les contributions peuvent prendre deux formes principales : le développement de nouveaux algorithmes de résolution, ou bien la création de nouveaux exemples de problèmes (benchmarks) permettant d'évaluer et comparer ces algorithmes.

**Objectif du projet** :  
L'objectif de ce projet est de préparer une contribution concrète à l'une de ces compétitions internationales, à choisir entre les domaines CP, SAT ou SMT. Deux types de contribution sont possibles selon les intérêts et les compétences du groupe :

1. **Contribution algorithmique** : Développer ou adapter un algorithme original capable de résoudre efficacement une catégorie spécifique de problèmes, en s'inspirant des approches les plus récentes de la littérature scientifique.

2. **Contribution aux benchmarks** : Concevoir et produire un ensemble original et pertinent de problèmes-tests (benchmarks), permettant de mieux évaluer et différencier les performances des algorithmes actuels, en s'inspirant de problématiques concrètes ou théoriques peu couvertes par les benchmarks existants.

**Attentes et livrables** :  
- Identifier clairement la compétition cible (CP, SAT ou SMT) et les modalités de participation.
- Pour les contributions algorithmiques : Implémentation opérationnelle et évaluation comparative rigoureuse par rapport aux algorithmes existants.
- Pour les contributions aux benchmarks : Description précise de l'origine des nouveaux problèmes, justification de leur intérêt scientifique et expérimental, et génération d'un jeu de données au format standard utilisé par la compétition choisie.
- Rédaction d'un court rapport scientifique documentant la démarche, les résultats obtenus et les perspectives éventuelles.

**Ressources utiles** :  
- [International SAT Competition](https://satcompetition.github.io/)
- [SMT-COMP](https://smt-comp.github.io/)
- [MiniZinc Challenge (CP)](https://www.minizinc.org/challenge.html)
- [BenchExec (outil standardisé pour l'évaluation des solveurs)](https://github.com/sosy-lab/benchexec)

Ce sujet représente une excellente opportunité pour acquérir une visibilité scientifique en contribuant directement aux progrès internationaux dans le domaine de la résolution automatique de problèmes complexes.

