import random
import numpy as np
import copy

def solve_sudoku_genetic(grid, population_size=100, max_generations=1000, 
                          mutation_rate=0.1, elite_size=10):
    """
    Résout un Sudoku en utilisant un algorithme génétique.
    
    Args:
        grid: Une grille de Sudoku 9x9 représentée comme une liste de listes.
              Les cases vides sont représentées par 0.
        population_size: Taille de la population.
        max_generations: Nombre maximum de générations.
        mutation_rate: Taux de mutation.
        elite_size: Nombre d'individus élites à conserver.
        
    Returns:
        La grille résolue si une solution a été trouvée, None sinon.
    """
    # Convertir la grille en numpy array pour faciliter les manipulations
    grid = np.array(grid)
    
    # Positions fixes (les chiffres donnés dans la grille originale)
    fixed_positions = np.zeros((9, 9), dtype=bool)
    for i in range(9):
        for j in range(9):
            if grid[i, j] != 0:
                fixed_positions[i, j] = True
    
    # Création de la population initiale
    population = [create_individual(grid.copy(), fixed_positions) for _ in range(population_size)]
    
    # Début de l'évolution
    best_fitness = 0
    best_solution = None
    
    for generation in range(max_generations):
        # Évaluation de la population
        fitness_scores = [fitness(individual) for individual in population]
        
        # Vérifier si une solution parfaite a été trouvée
        best_idx = np.argmax(fitness_scores)
        if fitness_scores[best_idx] > best_fitness:
            best_fitness = fitness_scores[best_idx]
            best_solution = population[best_idx].copy()
            
            # Si une solution parfaite est trouvée, on s'arrête
            if best_fitness == 162:  # 9 lignes + 9 colonnes + 9 blocs, tous parfaits
                return best_solution.tolist()
        
        # Sélection des parents
        parents = selection(population, fitness_scores, elite_size)
        
        # Création de la nouvelle population
        next_generation = parents.copy()  # Élites conservés
        
        # Compléter la population avec des enfants
        while len(next_generation) < population_size:
            parent1, parent2 = random.sample(parents, 2)
            child = crossover(parent1, parent2, fixed_positions)
            child = mutation(child, fixed_positions, mutation_rate)
            next_generation.append(child)
        
        population = next_generation
    
    # Retourner la meilleure solution trouvée
    if best_solution is not None:
        return best_solution.tolist()
    return None

def create_individual(grid, fixed_positions):
    """
    Crée un individu valide pour la population initiale.
    Les chiffres fixes sont conservés, les autres sont remplis de manière aléatoire
    tout en respectant les contraintes par ligne.
    """
    # Pour chaque ligne, remplir les cases vides avec les chiffres manquants
    for i in range(9):
        # Trouver les chiffres déjà présents dans la ligne
        present_digits = set(grid[i][grid[i] != 0])
        
        # Chiffres manquants à placer
        missing_digits = list(set(range(1, 10)) - present_digits)
        random.shuffle(missing_digits)
        
        # Remplir les cases vides avec les chiffres manquants
        for j in range(9):
            if grid[i, j] == 0:
                grid[i, j] = missing_digits.pop()
    
    return grid

def fitness(grid):
    """
    Évalue la qualité d'une solution.
    Une solution parfaite a un score de 162 (9 lignes + 9 colonnes + 9 blocs, tous parfaits).
    """
    score = 0
    
    # Vérifier les lignes
    for i in range(9):
        score += len(set(grid[i])) - (9 - len(set(grid[i])))
    
    # Vérifier les colonnes
    for j in range(9):
        score += len(set(grid[:, j])) - (9 - len(set(grid[:, j])))
    
    # Vérifier les blocs 3x3
    for block_i in range(3):
        for block_j in range(3):
            block = grid[block_i*3:(block_i+1)*3, block_j*3:(block_j+1)*3].flatten()
            score += len(set(block)) - (9 - len(set(block)))
    
    return score

def selection(population, fitness_scores, elite_size):
    """
    Sélectionne les meilleurs individus pour la reproduction.
    """
    # Trier la population par fitness
    elite_indices = np.argsort(fitness_scores)[-elite_size:]
    elites = [population[i] for i in elite_indices]
    
    return elites

def crossover(parent1, parent2, fixed_positions):
    """
    Crée un nouvel individu en combinant deux parents.
    Le croisement se fait par ligne: certaines lignes viennent du parent1, d'autres du parent2.
    """
    child = np.zeros((9, 9), dtype=int)
    
    # Sélectionner aléatoirement les lignes à hériter de chaque parent
    for i in range(9):
        if random.random() < 0.5:
            child[i] = parent1[i].copy()
        else:
            child[i] = parent2[i].copy()
    
    # S'assurer que les positions fixes sont respectées
    for i in range(9):
        for j in range(9):
            if fixed_positions[i, j]:
                # Récupérer la valeur fixe du parent1 (les deux parents ont les mêmes valeurs fixes)
                child[i, j] = parent1[i, j]
    
    return child

def mutation(individual, fixed_positions, mutation_rate):
    """
    Applique une mutation à un individu.
    La mutation consiste à échanger deux chiffres non fixes dans une même ligne.
    """
    mutated = individual.copy()
    
    for i in range(9):
        if random.random() < mutation_rate:
            # Trouver les positions non fixes dans cette ligne
            non_fixed_positions = [j for j in range(9) if not fixed_positions[i, j]]
            
            if len(non_fixed_positions) >= 2:
                # Choisir deux positions à échanger
                j1, j2 = random.sample(non_fixed_positions, 2)
                
                # Échanger les valeurs
                mutated[i, j1], mutated[i, j2] = mutated[i, j2], mutated[i, j1]
    
    return mutated