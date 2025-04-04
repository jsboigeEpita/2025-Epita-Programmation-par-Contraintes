import random


class MinesweeperSolver:
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

        return self.make_probability_guess()

    def update_mine_count(self):
        flag_count = sum(sum(1 for cell in row if cell) for row in self.game.flagged)
        self.remaining_mines = self.game.num_mines - flag_count

    def get_unrevealed_neighbors(self, x, y):
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
        self.safe_moves = []
        self.flagged_cells = []

        for y in range(self.height):
            for x in range(self.width):
                if not self.game.revealed[y][x] or self.game.grid[y][x] <= 0:
                    continue

                unrevealed = self.get_unrevealed_neighbors(x, y)
                flagged_count = self.get_flagged_neighbors_count(x, y)

                if len(unrevealed) + flagged_count == self.game.grid[y][x]:
                    for nx, ny in unrevealed:
                        if not self.game.flagged[ny][nx]:
                            self.flagged_cells.append((nx, ny))

                if flagged_count == self.game.grid[y][x]:
                    for nx, ny in unrevealed:
                        if (
                            not self.game.flagged[ny][nx]
                            and (nx, ny) not in self.safe_moves
                        ):
                            self.safe_moves.append((nx, ny))

    def make_probability_guess(self):
        has_unrevealed = False
        for y in range(self.height):
            for x in range(self.width):
                if not self.game.revealed[y][x] and not self.game.flagged[y][x]:
                    has_unrevealed = True
                    break

        if not has_unrevealed:
            return False

        candidates = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.game.revealed[y][x] and not self.game.flagged[y][x]:
                    candidates.append((x, y))

        if candidates:
            best_candidate = None
            most_revealed_neighbors = -1

            for x, y in candidates:
                revealed_neighbors = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if (dx == 0 and dy == 0) or not (
                            0 <= nx < self.width and 0 <= ny < self.height
                        ):
                            continue
                        if self.game.revealed[ny][nx]:
                            revealed_neighbors += 1

                if revealed_neighbors > most_revealed_neighbors:
                    most_revealed_neighbors = revealed_neighbors
                    best_candidate = (x, y)

            if best_candidate and most_revealed_neighbors > 0:
                self.safe_moves.append(best_candidate)
            else:
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
