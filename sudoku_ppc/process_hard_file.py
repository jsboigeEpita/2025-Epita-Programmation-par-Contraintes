# Ouvrir le fichier source en mode lecture et le fichier destination en mode écriture
with open('HardestDatabase110626.txt', 'r', encoding='utf-8') as fichier_source, \
     open('hard_test.txt', 'w', encoding='utf-8') as fichier_dest:
    
    # Lire le fichier source ligne par ligne
    for ligne in fichier_source:

        #eviter les lignes qui ne commence pas par 0-9 ou .
        if not ligne.startswith(tuple("0123456789.")):
            continue

        sudoku = ligne.split()[0]

        sudoku = sudoku.replace(".", "0")

        for i in range(9):
            line = sudoku[i*9:(i+1)*9]
            fichier_dest.write(line + "\n")

        # Ajouter une ligne vide entre les grilles
        fichier_dest.write("\n")
        
        # Optionnel: vider le buffer d'écriture à chaque itération
        fichier_dest.flush()