import random

class GreedySolver:
    def __init__(self, game):
        self.game = game
        self.width = game.width
        self.height = game.height
        self.remaining_mines = game.num_mines
        self.safe_moves = []  # List of (x, y) coordinates that are safe to reveal
        self.flagged_cells = []  # List of (x, y) coordinates that should be flagged

    def solve_step(self):
        """Perform one step of the solving process."""
        self.safe_moves = []
        self.update_mine_count()
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

    def make_random_guess(self):
        """Make an educated guess when no trivial moves are available."""
        # Check if there are any unrevealed cells
        has_unrevealed = any(
            not self.game.revealed[y][x] and not self.game.flagged[y][x]
            for y in range(self.height)
            for x in range(self.width)
        )

        if not has_unrevealed:
            return False

        # Find candidate cells
        candidates = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if not self.game.revealed[y][x] and not self.game.flagged[y][x]
        ]

        if candidates:
            random_candidate = random.choice(candidates)
            self.safe_moves.append(random_candidate)
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
