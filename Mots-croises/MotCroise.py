import sys
import time
from ortools.sat.python import cp_model
import re
import random


def generate_table(rows = 6, columns = 6):
    noir_colonne_precedente = True
    res = []
    for i in range(rows):
        row = ["."] * columns

        if not noir_colonne_precedente:
            for i in range(random.randint(0, 3)):
                noir = random.randint(0, columns - 1)
                row[noir] = "#"
            noir_colonne_precedente = True

        elif random.random() < 0.8: #20% de chance pas de case noirs dans la ligne
            noir = random.randint(0, columns - 1)
            row[noir] = "#"
            noir_colonne_precedente = True
        else:
            noir_colonne_precedente = False

        res.append(row)
    return res
    
        

LA_GRILLE = generate_table()
for r in LA_GRILLE:
    print(r)

dictionnaire_mots = 'dictionnaire.txt'
longueur_min_mot = 3

#Emplacement structure tuple : (num, sens, ligne_debug, col_debut, longueur)


def charger_dico(nom_fichier, longueurs_requises):
    mots_par_longueur = {}
    with open(nom_fichier, 'r', encoding='utf-8') as fichier:
        for ligne in fichier:
            mot = ligne.strip()
            mot = mot.lower()
            lg = len(mot)

            if lg in longueurs_requises:
                if lg not in mots_par_longueur:
                    mots_par_longueur[lg] = []
                mots_par_longueur[lg].append(mot.upper())

        return mots_par_longueur

def trouver_emplacements_et_croisements(grille):
    hauteur = len(grille)
    largeur = len(grille[0])
    liste_emplacements = []
    compteur_emplacements = 0
    longueurs_requises = set()

    num_ligne = 0
    while num_ligne < hauteur:
        num_col = 0
        while num_col < largeur:
            if grille[num_ligne][num_col] == '.':
                col_debut_mot = num_col
                longueur_mot = 0
                while num_col < largeur and grille[num_ligne][num_col] == '.':
                    longueur_mot = longueur_mot + 1
                    num_col = num_col + 1

                if longueur_mot >= longueur_min_mot:
                    nouvel_emp = (compteur_emplacements, "H", num_ligne, col_debut_mot, longueur_mot)
                    liste_emplacements.append(nouvel_emp)
                    longueurs_requises.add(longueur_mot)
                    compteur_emplacements = compteur_emplacements + 1
            else:
                num_col = num_col + 1
        num_ligne = num_ligne + 1

    num_col = 0
    while num_col < largeur:
        num_ligne = 0
        while num_ligne < hauteur:
            if grille[num_ligne][num_col] == '.':
                ligne_debut_mot = num_ligne
                longueur_mot = 0
                while num_ligne < hauteur and grille[num_ligne][num_col] == '.':
                    longueur_mot = longueur_mot + 1
                    num_ligne = num_ligne + 1
                if longueur_mot >= longueur_min_mot:
                    nouvel_emp = (compteur_emplacements, 'V', ligne_debut_mot, num_col, longueur_mot)
                    liste_emplacements.append(nouvel_emp)
                    longueurs_requises.add(longueur_mot)
                    compteur_emplacements = compteur_emplacements + 1
            else:
                num_ligne = num_ligne + 1
        num_col = num_col + 1

    liste_croisements = []
    map_emplacements = {}
    for emp in liste_emplacements:
        map_emplacements[emp[0]] = emp

    map_cellules = {}
    for emplacement in liste_emplacements:
        for i in range(emplacement[4]):
            if emplacement[1] == 'H':
                cell = (emplacement[2], emplacement[3] + i)
            else:
                cell = (emplacement[2] + i, emplacement[3])
            if cell not in map_cellules:
                map_cellules[cell] = []

            val = map_cellules.get(cell, [])
            val.append(emplacement[0])
            map_cellules[cell] = val

    paires_traitees = []
    for cellule, ids_occupants in map_cellules.items():
        if len(ids_occupants) > 1:
             id_h = -1
             id_v = -1
             for un_id in ids_occupants:
                 emplacement_correspondant = map_emplacements[un_id]
                 if emplacement_correspondant[1] == 'H':
                     id_h = un_id
                 else:
                     id_v = un_id

             if id_h != -1 and id_v != -1:
                 if id_h < id_v:
                     paire = (id_h, id_v)
                 else:
                     paire = (id_v, id_h)

                 if paire not in paires_traitees:
                    emp_h = map_emplacements[id_h]
                    emp_v = map_emplacements[id_v]
                    index_dans_mot_h = cellule[1] - emp_h[3]
                    index_dans_mot_v = cellule[0] - emp_v[2]
                    details_croisement = {
                        'h_slot_id': id_h,
                        'v_slot_id': id_v,
                        'h_char_index': index_dans_mot_h,
                        'v_char_index': index_dans_mot_v
                    }
                    liste_croisements.append(details_croisement)
                    paires_traitees.append(paire)

    return liste_emplacements, liste_croisements, longueurs_requises

def afficher_grille(structure_grille, la_solution=None, les_emplacements=None):
    hauteur = len(structure_grille)
    largeur = len(structure_grille[0])

    grille_affichee = []
    for ligne_originale in structure_grille:
        nouvelle_ligne = []
        for caractere in ligne_originale:
            nouvelle_ligne.append(caractere)
        grille_affichee.append(nouvelle_ligne)

    if la_solution is not None and les_emplacements is not None:
         map_emplacements = {}
         for emp in les_emplacements:
             map_emplacements[emp[0]] = emp

         for id_emp, mot_choisi in la_solution.items():
             emplacement = map_emplacements[id_emp]
             index_lettre = 0
             while index_lettre < len(mot_choisi):
                 lettre = mot_choisi[index_lettre]
                 ligne_case = emplacement[2]
                 colonne_case = emplacement[3]
                 if emplacement[1] == "H":
                     colonne_case += index_lettre
                 else:
                     ligne_case += index_lettre
                 grille_affichee[ligne_case][colonne_case] = lettre
                 index_lettre = index_lettre + 1

    num_ligne = 0
    while num_ligne < hauteur:
        ligne_texte = ""
        num_col = 0
        while num_col < largeur:
           ligne_texte = ligne_texte + grille_affichee[num_ligne][num_col] + " "
           num_col = num_col + 1
        print(ligne_texte.strip())
        num_ligne = num_ligne + 1

if __name__ == "__main__":
    les_emplacements, les_croisements, les_longueurs_requises = trouver_emplacements_et_croisements(LA_GRILLE)

    if len(les_emplacements) == 0:
        sys.exit(0)

    dico_mots_par_longueur = charger_dico(dictionnaire_mots, les_longueurs_requises)

    mots_possibles_par_emplacement = {}
    map_emplacements = {}
    for emp in les_emplacements:
        map_emplacements[emp[0]] = emp

    probleme_valide = True
    for emplacement in les_emplacements:
        longueur_voulue = emplacement[4]
        candidats = dico_mots_par_longueur.get(longueur_voulue, [])

        if len(candidats) == 0:
            probleme_valide = False
            break
        mots_possibles_par_emplacement[emplacement[0]] = candidats

    if not probleme_valide:
        sys.exit(1)

    modele = cp_model.CpModel()

    vars_emplacement = {}
    for emplacement in les_emplacements:
        num_emp = emplacement[0]
        nb_candidats = len(mots_possibles_par_emplacement[num_emp])

        nom_variable = f'emp_{num_emp}'
        vars_emplacement[num_emp] = modele.NewIntVar(0, nb_candidats - 1, nom_variable)

    for croisement in les_croisements:
        id_h = croisement['h_slot_id']
        id_v = croisement['v_slot_id']
        index_lettre_h = croisement['h_char_index']
        index_lettre_v = croisement['v_char_index']

        var_h = vars_emplacement[id_h]
        var_v = vars_emplacement[id_v]

        mots_h = mots_possibles_par_emplacement[id_h]
        mots_v = mots_possibles_par_emplacement[id_v]

        affectations_permises = []
        index_candidat_h = 0
        while index_candidat_h < len(mots_h):
            mot_h = mots_h[index_candidat_h]
            index_candidat_v = 0
            while index_candidat_v < len(mots_v):
                mot_v = mots_v[index_candidat_v]

                if mot_h[index_lettre_h] == mot_v[index_lettre_v]:
                    affectations_permises.append( (index_candidat_h, index_candidat_v) )

                index_candidat_v = index_candidat_v + 1
            index_candidat_h = index_candidat_h + 1

        if len(affectations_permises) > 0:
            modele.AddAllowedAssignments([var_h, var_v], affectations_permises)
        else:
            modele.AddBoolOr([])


    solveur = cp_model.CpSolver()
    solveur.parameters.num_search_workers = 1
    statut = solveur.Solve(modele)

    if statut == cp_model.OPTIMAL or statut == cp_model.FEASIBLE:
        la_solution_finale = {}
        for id_emp, variable in vars_emplacement.items():
            index_mot_retenu = solveur.Value(variable)
            mot_retenu = mots_possibles_par_emplacement[id_emp][index_mot_retenu]
            la_solution_finale[id_emp] = mot_retenu

        afficher_grille(LA_GRILLE, la_solution_finale, les_emplacements)

    else:
        print("pas faisable apparement")
