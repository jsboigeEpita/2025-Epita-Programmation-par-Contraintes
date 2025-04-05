import random
from collections import defaultdict

class AstarSolver:
    def __init__(self, game):
        self.width = game.width
        self.height = game.height
        self.total_mines = game.num_mines
        self.safe_moves = []
        self.flagged_cells = []
        
        self.revealed_cells = set()
        self.flagged_mines = set()
        self.visible_numbers = {}
        self.nb_explosions = 0

        self.update_solver_state(game)
    
    def update_solver_state(self, game):
        self.revealed_cells = set()
        self.flagged_mines = set()
        self.visible_numbers = {}

        for y in range(self.height):
            for x in range(self.width):
                if game.revealed[y][x]:
                    self.revealed_cells.add((x, y))
                    cell_value = self._get_visible_number(game, x, y)
                    if cell_value > 0:
                        self.visible_numbers[(x, y)] = cell_value

                if game.flagged[y][x]:
                    self.flagged_mines.add((x, y))
    
    def _get_visible_number(self, game, x, y):
        if game.revealed[y][x] and game.grid[y][x] >= 0:
            return game.grid[y][x]
        return 0
    
    def get_unrevealed_neighbors(self, x, y):
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + i >= 0 and x + i < self.width and y + j >= 0 and y + j < self.height and (x + i, y + j) not in self.revealed_cells and (x + i, y + j) not in self.flagged_mines:
                    neighbors.append((x + i, y + j))
        return neighbors

    def get_flagged_neighbors(self, x, y):
        flagged = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + i >= 0 and x + i < self.width and y + j >= 0 and y + j < self.height and (x + i, y + j) in self.flagged_mines and (x + i, y + j):
                    flagged.append((x + i, y + j))
        return flagged

    def solve_step(self):
        self.safe_moves = []
        self.flagged_cells = []

        self._apply_single_cell_constraints()

        if not self.safe_moves and not self.flagged_cells:
            self.random_pick()
        
        return bool(self.safe_moves or self.flagged_cells)
    
    def _apply_single_cell_constraints(self):
        for cell, number in self.visible_numbers.items():
            x, y = cell
            unrevealed_neighbors = self.get_unrevealed_neighbors(x, y)
            flagged_neighbors = self.get_flagged_neighbors(x, y)

            if len(flagged_neighbors) == number and unrevealed_neighbors:
                for nx, ny in unrevealed_neighbors:
                    if (nx, ny) not in self.flagged_mines and (nx, ny) not in self.safe_moves and (nx, ny) not in self.revealed_cells:
                        self.safe_moves.append((nx, ny))
            
            if len(unrevealed_neighbors) + len(flagged_neighbors) == number and unrevealed_neighbors:
                for nx, ny in unrevealed_neighbors:
                    if (nx, ny) not in self.flagged_mines and (nx, ny) not in self.flagged_cells:
                        self.flagged_cells.append((nx, ny))
    
    def apply_moves(self, game):
        for x, y in self.flagged_cells:
            if not game.flagged[y][x]:
                game.toggle_flag(x, y)
                self.flagged_mines.add((x, y))
        
        if self.safe_moves:
            x,y = self.safe_moves[0]
            game.reveal(x, y)
            self.revealed_cells.add((x, y))
            return True
        return False
    # One step of the A* algorithm
    # def solve(self):
    #     while self.apply_logic():
    #         self.apply_moves()
    #         while self.moves != []:
    #             self.apply_moves()
    #     
    #     if self.is_solved():
    #         return True 
    #     
    #     else:
    #         self.random_solve()
    #         while self.moves != []:
    #             self.apply_moves()
    #         return False
    
    # def is_solved(self):
    #     return self.get_count_revealed() + self.get_count_flagged() == self.width * self.height
    
    # def get_count_revealed(self):
    #     count = 0
    #     for x in range(self.width):
    #         for y in range(self.height):
    #             if self.revealed_cells[x][y]:
    #                 count += 1
    #     return count
    
    # def get_count_flagged(self):
    #     count = 0
    #     for x in range(self.width):
    #         for y in range(self.height):
    #             if self.flagged_cells[x][y]:
    #                 count += 1
    #     return count
    
    # def apply_logic(self):
    #     self.moves = []
    #     revealed = self.get_revealed()
    #     for cell in revealed:
    #         x, y = cell[0]
    #         number = cell[1]
    #         unrevealed_neighbors = self.get_unrevealed_neighbors(x, y)
    #         flagged_neighbors = self.get_flagged_neighbors(x, y)

    #         # If number of flags equals the cell's number, all other neighbors are safe
    #         if len(flagged_neighbors) == number and unrevealed_neighbors:
    #             for nx, ny in unrevealed_neighbors:
    #                 if not self.flagged_cells[nx][ny] and (nx, ny) not in self.moves:
    #                     self.moves.append((nx, ny))
    #         
    #         # If number of flags plus number of unrevealed neighbors equals the cell's number, all unrevealed neighbors are mines
    #         if len(flagged_neighbors) + len(unrevealed_neighbors) == number and unrevealed_neighbors:
    #             for nx, ny in unrevealed_neighbors:
    #                 if not self.flagged_cells[nx][ny] and (nx, ny):
    #                     self.flagged_cells[nx][ny] = True
    #     
    #     return self.moves != []

    # def get_flagged_neighbors(self, x, y):
    #     flagged_neighbors = []
    #     for i in range(-1, 2):
    #         for j in range(-1, 2):
    #             if x + i >= 0 and x + i < self.width and y + j >= 0 and y + j < self.height and self.flagged_cells[x + i][y + j]:
    #                 flagged_neighbors.append((x + i, y + j))
    #     return flagged_neighbors

    # def get_unrevealed_neighbors(self, x, y):
    #     unrevealed_neighbors = []
    #     for i in range(-1, 2):
    #         for j in range(-1, 2):
    #             if x + i >= 0 and x + i < self.width and y + j >= 0 and y + j < self.height and not self.revealed_cells[x + i][y + j] and not self.flagged_cells[x + i][y + j]:
    #                 unrevealed_neighbors.append((x + i, y + j))
    #     return unrevealed_neighbors

    # def get_revealed(self):
    #     revealed = []
    #     for x in range(self.width):
    #         for y in range(self.height):
    #             if self.revealed_cells[x][y]:
    #                 revealed.append(((x, y), self.grid[x][y]))
    #     return revealed


    # def apply_moves(self):
    #     new_moves = []
    #     for x, y in self.moves:
    #         if not (0 <= x < self.width and 0 <= y < self.height):
    #             continue

    #         if self.revealed_cells[x][y] or self.flagged_cells[x][y]:
    #             continue

    #         self.revealed_cells[x][y] = True

    #         if self.grid[x][y] == -1:
    #             self.nb_explosions += 1
    #             self.revealed_cells[x][y] = False
    #             self.flagged_cells[x][y] = True
    #             continue

    #         if self.grid[x][y] == 0:
    #             for dy in [-1, 0, 1]:
    #                 for dx in [-1, 0, 1]:
    #                     nx, ny = x + dx, y + dy
    #                     if 0 <= nx < self.width and 0 <= ny < self.height:
    #                         new_moves.append((nx, ny))
    #     self.moves = []
    #     self.moves = new_moves


    # def random_solve(self):
    #     x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
    #     while self.revealed_cells[x][y] or self.flagged_cells[x][y]:
    #         x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1) 
    #     self.moves.append((x, y))
    #     self.apply_moves()

    