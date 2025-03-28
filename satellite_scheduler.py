# Notebook pour l'Ordonnancement de Prises de Vue Satellite par Contraintes (CSP)

import numpy as np
import plotly.graph_objects as go
from ortools.sat.python import cp_model

# Données des prises de vue (exemple simplifié)
requests = {
    "Tokyo": {"priority": 3, "coordinates": [35.6895, 139.6917]},
    "Montréal": {"priority": 2, "coordinates": [45.5017, -73.5673]}
}

# Définition du modèle CSP
model = cp_model.CpModel()

# Variables de décision : Temps de début des prises de vue
start_times = {city: model.NewIntVar(0, 1000, f"start_{city}") for city in requests.keys()}

# Contrainte : Respect des priorités (Tokyo doit être traité avant Montréal si possible)
model.Add(start_times["Tokyo"] <= start_times["Montréal"])

# Fonction objectif : Maximiser la somme des priorités
model.Maximize(sum(requests[city]["priority"] * start_times[city] for city in requests.keys()))

# Résolution
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Affichage des résultats
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Plan de prises de vue optimisé:")
    for city in requests.keys():
        print(f"{city} -> Début: {solver.Value(start_times[city])}")
else:
    print("Aucune solution trouvée.")

# Visualisation de la trajectoire du satellite
fig = go.Figure()
fig.add_trace(go.Scattergeo(
    lon=[requests[city]['coordinates'][1] for city in requests.keys()],
    lat=[requests[city]['coordinates'][0] for city in requests.keys()],
    text=list(requests.keys()),
    mode='markers',
))
fig.update_layout(title="Positions des Cibles d'Observation")
fig.show()
