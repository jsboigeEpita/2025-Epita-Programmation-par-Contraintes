from PyQt5.QtCore import QObject, pyqtSignal
from ortools.sat.python import cp_model


class SolverWorker(QObject):
    # Signal to indicate the solver is finished. It sends a result dictionary.
    finished = pyqtSignal(dict)

    def __init__(self, params, parent=None):
        super().__init__(parent)
        self.params = params
        self._cancelled = False
        self.solver = None  # Will hold the solver instance once created.

    def cancel(self):
        # This method is called from another thread to cancel the search.
        self._cancelled = True
        if self.solver is not None:
            self.solver.StopSearch()

    def run(self):
        print("Solver worker started")
        # Unpack parameters from the UI.
        matieres = self.params.get("matieres", {})
        enseignants = self.params.get("enseignants", {})
        nb_classes = self.params.get("nb_classes", 8)
        nb_salles = self.params.get("nb_salles", 8)
        jours_str = self.params.get("jours", ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"])
        heures_str = self.params.get("heures",
                                     ["8h30-9h30", "9h30-10h30", "10h30-11h30", "11h30-12h30", "14h-15h", "15h-16h",
                                      "16h-17h", "17h-18h"])

        nb_jours = len(jours_str)
        nb_heures = len(heures_str)

        model_time = self.params.get("model_time", 60.0)

        model = cp_model.CpModel()

        # Create Boolean variables for each possible course slot.
        x = {}
        for nom_matiere in matieres:
            for jour in range(nb_jours):
                for heure in range(nb_heures):
                    for classe in range(nb_classes):
                        for salle in range(nb_salles):
                            for prof, matiere in enseignants.items():
                                if matiere == nom_matiere:
                                    x[(nom_matiere, jour, heure, classe, salle, prof)] = model.NewBoolVar(
                                        f'{nom_matiere}_{jour}_{heure}_classe{classe}_salle{salle}_prof{prof}')

        # (--- Add all the constraints exactly as in your original code ---)
        # Constraint 1: Each class must have the required number of hours per subject.
        for nom_matiere, heures_matiere in matieres.items():
            for classe in range(nb_classes):
                model.Add(sum(x[(nom_matiere, jour, heure, classe, salle, prof)]
                              for jour in range(nb_jours)
                              for heure in range(nb_heures)
                              for salle in range(nb_salles)
                              for prof, matiere in enseignants.items()
                              if matiere == nom_matiere) == heures_matiere)

        # Constraint 2: A class cannot have two courses at the same time.
        for jour in range(nb_jours):
            for heure in range(nb_heures):
                for classe in range(nb_classes):
                    model.Add(sum(x[(nom_matiere, jour, heure, classe, salle, prof)]
                                  for nom_matiere in matieres
                                  for salle in range(nb_salles)
                                  for prof, matiere in enseignants.items()
                                  if matiere == nom_matiere) <= 1)

        # Constraint 3: A room cannot host two courses simultaneously.
        for jour in range(nb_jours):
            for heure in range(nb_heures):
                for salle in range(nb_salles):
                    model.Add(
                        sum(x[(nom_matiere, jour, heure, classe, salle, prof)]
                            for nom_matiere in matieres
                            for classe in range(nb_classes)
                            for prof, matiere in enseignants.items()
                            if matiere == nom_matiere) <= 1
                    )

        # Constraint 4: The same course cannot be taught in different classes at the same time.
        for nom_matiere in matieres:
            for jour in range(nb_jours):
                for heure in range(nb_heures):
                    for prof, matiere in enseignants.items():
                        if matiere == nom_matiere:
                            model.Add(sum(x[(nom_matiere, jour, heure, classe, salle, prof)]
                                          for classe in range(nb_classes)
                                          for salle in range(nb_salles)) <= 1)

        # Constraint 5: No more than two consecutive hours for the same course.
        for nom_matiere in matieres:
            for jour in range(nb_jours):
                for heure in range(nb_heures - 2):
                    for classe in range(nb_classes):
                        model.Add(
                            sum(x[(nom_matiere, jour, heure, classe, salle, prof)]
                                for salle in range(nb_salles)
                                for prof, matiere in enseignants.items()
                                if matiere == nom_matiere) +
                            sum(x[(nom_matiere, jour, heure + 1, classe, salle, prof)]
                                for salle in range(nb_salles)
                                for prof, matiere in enseignants.items()
                                if matiere == nom_matiere) +
                            sum(x[(nom_matiere, jour, heure + 2, classe, salle, prof)]
                                for salle in range(nb_salles)
                                for prof, matiere in enseignants.items()
                                if matiere == nom_matiere) < 3
                        )

        # Constraint 6: No course in two different rooms consecutively.
        for nom_matiere in matieres:
            for jour in range(nb_jours):
                for heure in range(nb_heures - 1):
                    for classe in range(nb_classes):
                        for salle1 in range(nb_salles):
                            for salle2 in range(nb_salles):
                                if salle1 != salle2:
                                    for prof, matiere in enseignants.items():
                                        if matiere == nom_matiere:
                                            model.Add(
                                                x[(nom_matiere, jour, heure, classe, salle1, prof)] +
                                                x[(nom_matiere, jour, heure + 1, classe, salle2, prof)] <= 1
                                            )

        # Constraint 7: A class must have only one teacher per subject.
        for nom_matiere in matieres:
            for classe in range(nb_classes):
                professeurs_matiere = [prof for prof, matiere in enseignants.items() if matiere == nom_matiere]
                prof_assigned = {}
                for prof in professeurs_matiere:
                    prof_assigned[prof] = model.NewBoolVar(f'prof_assigned_{nom_matiere}_{classe}_{prof}')
                    for jour in range(nb_jours):
                        for heure in range(nb_heures):
                            for salle in range(nb_salles):
                                model.AddImplication(x[(nom_matiere, jour, heure, classe, salle, prof)],
                                                     prof_assigned[prof])
                model.Add(sum(prof_assigned[prof] for prof in professeurs_matiere) == 1)

        # Minimization: reduce gaps (trous), courses after 17h, and balance single vs. two-hour courses.
        Y = {}
        for classe in range(nb_classes):
            for jour in range(nb_jours):
                for heure in range(nb_heures):
                    Y[(classe, jour, heure)] = model.NewBoolVar(f"Y_classe{classe}_{jour}_{heure}")
                    model.Add(Y[(classe, jour, heure)] ==
                              sum(x[(nom_matiere, jour, heure, classe, salle, prof)]
                                  for nom_matiere in matieres
                                  for salle in range(nb_salles)
                                  for prof, matiere in enseignants.items()
                                  if matiere == nom_matiere)
                              )

        trous = []
        for classe in range(nb_classes):
            for jour in range(nb_jours):
                for heure in range(nb_heures - 2):
                    trou1 = model.NewBoolVar(f"trou1_classe{classe}_{jour}_{heure}")
                    model.Add(trou1 <= Y[(classe, jour, heure)])
                    model.Add(trou1 <= 1 - Y[(classe, jour, heure + 1)])
                    model.Add(trou1 <= Y[(classe, jour, heure + 2)])
                    model.Add(trou1 >= Y[(classe, jour, heure)]
                              + (1 - Y[(classe, jour, heure + 1)])
                              + Y[(classe, jour, heure + 2)] - 2)
                    trous.append(trou1)
                for heure in range(nb_heures - 3):
                    trou2 = model.NewBoolVar(f"trou2_classe{classe}_{jour}_{heure}")
                    model.Add(trou2 <= Y[(classe, jour, heure)])
                    model.Add(trou2 <= 1 - Y[(classe, jour, heure + 1)])
                    model.Add(trou2 <= 1 - Y[(classe, jour, heure + 2)])
                    model.Add(trou2 <= Y[(classe, jour, heure + 3)])
                    model.Add(trou2 >= Y[(classe, jour, heure)]
                              + (1 - Y[(classe, jour, heure + 1)])
                              + (1 - Y[(classe, jour, heure + 2)])
                              + Y[(classe, jour, heure + 3)] - 3)
                    trous.append(trou2)
                    for heure in range(nb_heures - 4):
                        trou3 = model.NewBoolVar(f"trou3_classe{classe}_{jour}_{heure}")
                        model.Add(trou3 <= Y[(classe, jour, heure)])
                        model.Add(trou3 <= 1 - Y[(classe, jour, heure + 1)])
                        model.Add(trou3 <= 1 - Y[(classe, jour, heure + 2)])
                        model.Add(trou3 <= 1 - Y[(classe, jour, heure + 3)])
                        model.Add(trou3 <= Y[(classe, jour, heure + 4)])
                        model.Add(trou3 >= Y[(classe, jour, heure)]
                                  + (1 - Y[(classe, jour, heure + 1)])
                                  + (1 - Y[(classe, jour, heure + 2)])
                                  + (1 - Y[(classe, jour, heure + 3)])
                                  + Y[(classe, jour, heure + 4)] - 4)
                        trous.append(trou3)
                    for heure in range(nb_heures - 5):
                        trou4 = model.NewBoolVar(f"trou4_classe{classe}_{jour}_{heure}")
                        model.Add(trou4 <= Y[(classe, jour, heure)])
                        model.Add(trou4 <= 1 - Y[(classe, jour, heure + 1)])
                        model.Add(trou4 <= 1 - Y[(classe, jour, heure + 2)])
                        model.Add(trou4 <= 1 - Y[(classe, jour, heure + 3)])
                        model.Add(trou4 <= 1 - Y[(classe, jour, heure + 4)])
                        model.Add(trou4 <= Y[(classe, jour, heure + 5)])
                        model.Add(trou4 >= Y[(classe, jour, heure)]
                                  + (1 - Y[(classe, jour, heure + 1)])
                                  + (1 - Y[(classe, jour, heure + 2)])
                                  + (1 - Y[(classe, jour, heure + 3)])
                                  + (1 - Y[(classe, jour, heure + 4)])
                                  + Y[(classe, jour, heure + 5)] - 5)
                        trous.append(trou4)

        cours_tardifs = []
        dernier_cours = nb_heures - 1
        for classe in range(nb_classes):
            for nom_matiere in matieres:
                for jour in range(nb_jours):
                    for salle in range(nb_salles):
                        for prof, matiere in enseignants.items():
                            if matiere == nom_matiere:
                                ct = model.NewBoolVar(f"cours_tardif_classe{classe}_{nom_matiere}_{jour}")
                                model.Add(ct == x[(nom_matiere, jour, dernier_cours, classe, salle, prof)])
                                cours_tardifs.append(ct)

        two_hour_courses = []
        single_hour_courses = []
        for classe in range(nb_classes):
            for nom_matiere in matieres:
                for jour in range(nb_jours):
                    for heure in range(nb_heures - 1):
                        two_hour_course = model.NewBoolVar(f"two_hour_course_{classe}_{nom_matiere}_{jour}_{heure}")
                        model.Add(two_hour_course <= sum(x[(nom_matiere, jour, heure, classe, salle, prof)]
                                                         for salle in range(nb_salles)
                                                         for prof, matiere in enseignants.items()
                                                         if matiere == nom_matiere))
                        model.Add(two_hour_course <= sum(x[(nom_matiere, jour, heure + 1, classe, salle, prof)]
                                                         for salle in range(nb_salles)
                                                         for prof, matiere in enseignants.items()
                                                         if matiere == nom_matiere))
                        model.Add(two_hour_course >= sum(x[(nom_matiere, jour, heure, classe, salle, prof)]
                                                         for salle in range(nb_salles)
                                                         for prof, matiere in enseignants.items()
                                                         if matiere == nom_matiere)
                                  + sum(x[(nom_matiere, jour, heure + 1, classe, salle, prof)]
                                        for salle in range(nb_salles)
                                        for prof, matiere in enseignants.items()
                                        if matiere == nom_matiere) - 1)
                        two_hour_courses.append(two_hour_course)
                    for heure in range(nb_heures):
                        single_hour_course = model.NewBoolVar(
                            f"single_hour_course_{classe}_{nom_matiere}_{jour}_{heure}")
                        cours_heure_courante = sum(x[(nom_matiere, jour, heure, classe, salle, prof)]
                                                   for salle in range(nb_salles)
                                                   for prof, matiere in enseignants.items()
                                                   if matiere == nom_matiere)
                        if heure == 0:
                            model.Add(single_hour_course <= cours_heure_courante)
                            model.Add(
                                single_hour_course <= 1 - sum(x[(nom_matiere, jour, heure + 1, classe, salle, prof)]
                                                              for salle in range(nb_salles)
                                                              for prof, matiere in enseignants.items()
                                                              if matiere == nom_matiere))
                        elif heure == nb_heures - 1:
                            model.Add(single_hour_course <= cours_heure_courante)
                            model.Add(
                                single_hour_course <= 1 - sum(x[(nom_matiere, jour, heure - 1, classe, salle, prof)]
                                                              for salle in range(nb_salles)
                                                              for prof, matiere in enseignants.items()
                                                              if matiere == nom_matiere))
                        else:
                            model.Add(single_hour_course <= cours_heure_courante)
                            model.Add(
                                single_hour_course <= 1 - sum(x[(nom_matiere, jour, heure - 1, classe, salle, prof)]
                                                              for salle in range(nb_salles)
                                                              for prof, matiere in enseignants.items()
                                                              if matiere == nom_matiere))
                            model.Add(
                                single_hour_course <= 1 - sum(x[(nom_matiere, jour, heure + 1, classe, salle, prof)]
                                                              for salle in range(nb_salles)
                                                              for prof, matiere in enseignants.items()
                                                              if matiere == nom_matiere))
                        single_hour_courses.append(single_hour_course)

        model.Minimize(10 * sum(trous) + 5 * sum(cours_tardifs) + 3 * sum(single_hour_courses) - sum(two_hour_courses))

        self.solver = cp_model.CpSolver()
        self.solver.parameters.max_time_in_seconds = model_time
        status = self.solver.Solve(model)

        result = {}
        if self._cancelled:
            result["error"] = "Model was cancelled."
        elif status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            result["objective_value"] = self.solver.ObjectiveValue()
            schedules = {}
            for classe in range(nb_classes):
                edt = {}
                # Initialize schedule for each day and time slot.
                for j, jour in enumerate(jours_str):
                    edt[jour] = {}
                    for h, heure in enumerate(heures_str):
                        edt[jour][heure] = "---"
                for nom_matiere in matieres:
                    for j in range(nb_jours):
                        for h in range(nb_heures):
                            for salle in range(nb_salles):
                                for prof, matiere in enseignants.items():
                                    if matiere == nom_matiere:
                                        if self.solver.BooleanValue(x[(nom_matiere, j, h, classe, salle, prof)]):
                                            edt[jours_str[j]][
                                                heures_str[h]] = f"{nom_matiere} (Salle {salle}, Prof: {prof})"
                schedules[classe] = edt
            result["schedules"] = schedules
            result["jours"] = jours_str
            result["heures"] = heures_str
        else:
            result["error"] = "No solution found."

        print("Solver worker finished")
        self.finished.emit(result)