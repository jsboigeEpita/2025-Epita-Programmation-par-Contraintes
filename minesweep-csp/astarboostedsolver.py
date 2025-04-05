import random

class AstarBoostedSolver:
    def __init__(self, game):
        self.game = game
        self.width = game.width
        self.height = game.height
        self.remaining_mines = game.num_mines
        self.safe_moves = []  # List of (x, y) coordinates that are safe to reveal
        self.flagged_cells = []  # List of (x, y) coordinates that should be flagged

    def solve_step(self):
        """Perform one step of the solving process."""
        self.update_mine_count()
        self.find_trivial_moves()

        if self.safe_moves or self.flagged_cells:
            return True

        # Use advanced solving strategies
        try:
            x, y = self.probabilistic_frontier_solver()
            self.safe_moves.append((x, y))
            return True
        except Exception:
            return self.make_random_guess()

    def update_mine_count(self):
        """Update the remaining mine count based on flagged cells."""
        flag_count = sum(sum(1 for cell in row if cell) for row in self.game.flagged)
        self.remaining_mines = self.game.num_mines - flag_count

    def get_unrevealed_neighbors(self, x, y):
        """Get a list of unrevealed neighboring cells."""
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (dx == 0 and dy == 0) or not (
                    0 <= nx < self.width and 0 <= ny < self.height
                ):
                    continue
                if not self.game.revealed[ny][nx]:
                    neighbors.append((nx, ny))
        return neighbors

    def get_flagged_neighbors_count(self, x, y):
        """Count the number of flagged neighboring cells."""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (dx == 0 and dy == 0) or not (
                    0 <= nx < self.width and 0 <= ny < self.height
                ):
                    continue
                if self.game.flagged[ny][nx]:
                    count += 1
        return count

    def find_trivial_moves(self):
        """Find obvious moves based on revealed cell numbers."""
        self.safe_moves = []
        self.flagged_cells = []

        for y in range(self.height):
            for x in range(self.width):
                # Skip unrevealed or zero cells
                if not self.game.revealed[y][x] or self.game.grid[y][x] <= 0:
                    continue

                unrevealed = self.get_unrevealed_neighbors(x, y)
                flagged_count = self.get_flagged_neighbors_count(x, y)

                # If unrevealed + flagged == cell number, all unrevealed are mines
                if len(unrevealed) + flagged_count == self.game.grid[y][x]:
                    for nx, ny in unrevealed:
                        if not self.game.flagged[ny][nx]:
                            self.flagged_cells.append((nx, ny))

                # If flagged count equals cell number, all other unrevealed are safe
                if flagged_count == self.game.grid[y][x]:
                    for nx, ny in unrevealed:
                        if (
                            not self.game.flagged[ny][nx]
                            and (nx, ny) not in self.safe_moves
                        ):
                            self.safe_moves.append((nx, ny))

    def probabilistic_frontier_solver(self):
        """
        Advanced probabilistic solver tracking mine frontiers
        Estimates mine probabilities across board regions
        """
        frontier_cells = []
        for y in range(self.height):
            for x in range(self.width):
                if self.game.revealed[y][x]:
                    unrevealed_neighbors = [
                        (nx, ny) 
                        for nx in range(max(0, x-1), min(self.width, x+2))
                        for ny in range(max(0, y-1), min(self.height, y+2))
                        if not self.game.revealed[ny][nx] and not self.game.flagged[ny][nx]
                    ]
                    
                    # Compute local mine probability
                    remaining_mines = self.game.grid[y][x] - self.get_flagged_neighbors_count(x, y)
                    local_prob = remaining_mines / len(unrevealed_neighbors) if unrevealed_neighbors else 0
                    
                    frontier_cells.extend(
                        (nx, ny, local_prob) 
                        for nx, ny in unrevealed_neighbors
                    )

        # If no frontier cells found, fall back to random
        if not frontier_cells:
            candidates = [
                (x, y)
                for y in range(self.height)
                for x in range(self.width)
                if not self.game.revealed[y][x] and not self.game.flagged[y][x]
            ]
            return random.choice(candidates) if candidates else (0, 0)

        # Return cell with lowest probability of being a mine
        return min(frontier_cells, key=lambda x: x[2])[:2]

    def make_random_guess(self):
        """Make a random guess when no other strategy works."""
        candidates = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if not self.game.revealed[y][x] and not self.game.flagged[y][x]
        ]

        if candidates:
            self.safe_moves.append(random.choice(candidates))
            return True
        return False

    def apply_moves(self):
        """Apply the moves found by the solver to the game."""
        # Apply flag moves first
        for x, y in self.flagged_cells:
            if not self.game.flagged[y][x]:
                self.game.toggle_flag(x, y)

        # Then reveal one safe cell (if any)
        if self.safe_moves:
            x, y = self.safe_moves[0]
            self.game.reveal(x, y)
            return True

        return False