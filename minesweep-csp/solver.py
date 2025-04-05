import random
from collections import defaultdict

class MinesweeperSolver:
    def __init__(self, game):
        """Initialize the solver with only observable game information."""
        # We'll only use the game object to get dimensions and observe revealed cells
        self.width = game.width
        self.height = game.height
        self.total_mines = game.num_mines
        self.safe_moves = []  # List of (x, y) coordinates that are safe to reveal
        self.flagged_cells = []  # List of (x, y) coordinates that should be flagged
        
        # Internal solver state based only on observable information
        self.revealed_cells = set()  # Set of (x,y) tuples that are revealed
        self.flagged_mines = set()   # Set of (x,y) tuples that are flagged
        self.visible_numbers = {}    # Dict of (x,y) -> number for revealed cells with numbers
        
        # Update solver state from current game state
        self.update_solver_state(game)
        
    def update_solver_state(self, game):
        """Update the solver state based on the visible game state."""
        # Clear existing state
        self.revealed_cells = set()
        self.flagged_mines = set()
        self.visible_numbers = {}
        
        # Scan the game board for visible information
        for y in range(self.height):
            for x in range(self.width):
                if game.revealed[y][x]:
                    self.revealed_cells.add((x, y))
                    # If the revealed cell has a number, record it
                    # We can see this information as a player
                    cell_value = self._get_visible_number(game, x, y)
                    if cell_value > 0:
                        self.visible_numbers[(x, y)] = cell_value
                
                if game.flagged[y][x]:
                    self.flagged_mines.add((x, y))
    
    def _get_visible_number(self, game, x, y):
        """Get the visible number at position (x,y) if revealed."""
        # This simulates a player seeing the number on a revealed cell
        if game.revealed[y][x] and game.grid[y][x] >= 0:
            return game.grid[y][x]
        return 0
    
    def get_unrevealed_neighbors(self, x, y):
        """Get all unrevealed neighboring cells of (x, y)."""
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (dx == 0 and dy == 0) or not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                if (nx, ny) not in self.revealed_cells:
                    neighbors.append((nx, ny))
        return neighbors
    
    def get_flagged_neighbors(self, x, y):
        """Get flagged neighbors of (x, y)."""
        flagged = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (dx == 0 and dy == 0) or not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                if (nx, ny) in self.flagged_mines:
                    flagged.append((nx, ny))
        return flagged
    
    def solve_step(self):
        """Perform one step of the solving process using constraint satisfaction."""
        self.safe_moves = []
        self.flagged_cells = []
        
        # Solve using single cell constraints
        self._apply_single_cell_constraints()
        
        # If no progress with single cells, try more advanced methods
        if not self.safe_moves and not self.flagged_cells:
            # Look for subset constraints (e.g., if cell A has 2 mines out of 3 neighbors,
            # and cell B has 1 mine out of the same 3 neighbors, then the third neighbor must be safe)
            self._apply_subset_constraints()
        
        # If still no progress, make a probability-based guess
        if not self.safe_moves and not self.flagged_cells:
            self._make_probability_guess()
        
        return bool(self.safe_moves or self.flagged_cells)

    def _apply_single_cell_constraints(self):
        """Apply constraints based on single cells."""
        for (x, y), number in self.visible_numbers.items():
            # Get unrevealed neighbors and flagged neighbors
            unrevealed = self.get_unrevealed_neighbors(x, y)
            flagged = self.get_flagged_neighbors(x, y)
            
            # If number of flags equals the cell's number, all other neighbors are safe
            if len(flagged) == number and unrevealed:
                for nx, ny in unrevealed:
                    if (nx, ny) not in self.flagged_mines and (nx, ny) not in self.safe_moves:
                        self.safe_moves.append((nx, ny))
            
            # If number of unrevealed cells equals remaining mines, all are mines
            if len(unrevealed) + len(flagged) == number and unrevealed:
                for nx, ny in unrevealed:
                    if (nx, ny) not in self.flagged_mines and (nx, ny) not in self.flagged_cells:
                        self.flagged_cells.append((nx, ny))
    
    def _apply_subset_constraints(self):
        """Apply constraints based on comparing overlapping cell neighborhoods."""
        # Group cells by their unrevealed neighbors
        cell_groups = defaultdict(list)
        for (x, y), number in self.visible_numbers.items():
            unrevealed = tuple(sorted(self.get_unrevealed_neighbors(x, y)))
            if unrevealed:  # Only consider cells with unrevealed neighbors
                flagged = self.get_flagged_neighbors(x, y)
                # The effective number is the cell's number minus already flagged neighbors
                effective_number = number - len(flagged)
                cell_groups[unrevealed].append(((x, y), effective_number))
        
        # Look for subsets where we can derive new information
        for neighbors, cells in cell_groups.items():
            if len(cells) < 2:  # Need at least two cells to compare
                continue
            
            # Find subsets of cells where constraints can be derived
            for i in range(len(cells)):
                for j in range(i+1, len(cells)):
                    cell1, num1 = cells[i]
                    cell2, num2 = cells[j]
                    
                    # Find unique neighbors of each cell
                    set1 = set(self.get_unrevealed_neighbors(*cell1)) - self.flagged_mines
                    set2 = set(self.get_unrevealed_neighbors(*cell2)) - self.flagged_mines
                    
                    # Set operations to find differences
                    unique_to_1 = set1 - set2
                    unique_to_2 = set2 - set1
                    common = set1 & set2
                    
                    # If cell1 has X mines in N cells, and cell2 has X mines in a subset of those N cells,
                    # then all cells in unique_to_1 must be safe
                    if num1 == num2 and unique_to_1 and not unique_to_2:
                        for nx, ny in unique_to_1:
                            if (nx, ny) not in self.safe_moves:
                                self.safe_moves.append((nx, ny))
                    
                    # If cell1 has X mines in N cells, and cell2 has X+Y mines in N+Z cells,
                    # then all Z cells in unique_to_2 must contain Y mines
                    if num2 > num1 and len(unique_to_2) == num2 - num1:
                        for nx, ny in unique_to_2:
                            if (nx, ny) not in self.flagged_cells:
                                self.flagged_cells.append((nx, ny))
                    
                    # The reverse case
                    if num1 > num2 and len(unique_to_1) == num1 - num2:
                        for nx, ny in unique_to_1:
                            if (nx, ny) not in self.flagged_cells:
                                self.flagged_cells.append((nx, ny))
    
    def _make_probability_guess(self):
        """Make a probability-based guess when deterministic methods fail."""
        if not self.visible_numbers:
            # No information yet, make a random guess
            all_cells = [(x, y) for y in range(self.height) for x in range(self.width)]
            unrevealed = [(x, y) for x, y in all_cells 
                         if (x, y) not in self.revealed_cells and (x, y) not in self.flagged_mines]
            
            if unrevealed:
                # Start with a corner or center for first move
                preferred_starts = [(0, 0), (0, self.height-1), (self.width-1, 0), 
                                   (self.width-1, self.height-1), (self.width//2, self.height//2)]
                for start in preferred_starts:
                    if start in unrevealed:
                        self.safe_moves.append(start)
                        return
                
                # Otherwise random
                self.safe_moves.append(random.choice(unrevealed))
            return
        
        # Calculate probabilities for each unrevealed cell
        cell_probabilities = {}
        all_unrevealed = set()
        
        # For each numbered cell, calculate probabilities for its neighbors
        for (x, y), number in self.visible_numbers.items():
            unrevealed = set(self.get_unrevealed_neighbors(x, y)) - self.flagged_mines
            flagged = set(self.get_flagged_neighbors(x, y))
            remaining_mines = number - len(flagged)
            
            # Update the global set of all unrevealed cells
            all_unrevealed.update(unrevealed)
            
            # Skip if no unrevealed cells or no more mines
            if not unrevealed or remaining_mines <= 0:
                continue
            
            # Calculate probability for each unrevealed neighbor
            prob = remaining_mines / len(unrevealed)
            for nx, ny in unrevealed:
                if (nx, ny) in cell_probabilities:
                    # Use the maximum probability if a cell belongs to multiple constraints
                    cell_probabilities[(nx, ny)] = max(cell_probabilities[(nx, ny)], prob)
                else:
                    cell_probabilities[(nx, ny)] = prob
        
        # Cells not adjacent to any numbers have a default probability based on remaining mines
        remaining_total_mines = self.total_mines - len(self.flagged_mines)
        non_frontier_cells = all_unrevealed - set(cell_probabilities.keys())
        remaining_non_frontier_cells = len(non_frontier_cells)
        
        if non_frontier_cells and remaining_total_mines > 0 and remaining_non_frontier_cells > 0:
            default_prob = min(0.2, remaining_total_mines / remaining_non_frontier_cells)
            for cell in non_frontier_cells:
                cell_probabilities[cell] = default_prob
        
        # Choose the cell with the lowest probability of being a mine
        if cell_probabilities:
            safest_cell = min(cell_probabilities.items(), key=lambda x: x[1])[0]
            self.safe_moves.append(safest_cell)
        elif all_unrevealed:
            # If we have unrevealed cells but no probabilities (unlikely), make a random choice
            self.safe_moves.append(random.choice(list(all_unrevealed)))
    
    def apply_moves(self, game):
        """Apply the moves found by the solver to the game."""
        # First apply all flags
        for x, y in self.flagged_cells:
            if not game.flagged[y][x]:
                game.toggle_flag(x, y)
                # Update our internal state
                self.flagged_mines.add((x, y))
        
        # Then reveal safe cells
        if self.safe_moves:
            x, y = self.safe_moves[0]  # Only apply one safe move at a time
            game.reveal(x, y)
            # Update our internal state
            self.revealed_cells.add((x, y))
            return True
        
        return False