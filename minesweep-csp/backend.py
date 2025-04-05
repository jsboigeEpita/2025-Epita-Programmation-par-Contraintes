from typing import Tuple, Optional
import random
from solver import MinesweeperSolver
from astarsolver import AstarSolver
from astarboostedsolver import AstarBoostedSolver
from greedysolver import GreedySolver

class SolverFactory:
    """Factory for creating different solver instances."""

    @staticmethod
    def create_solver(solver_type, game):
        """
        Create a solver instance based on the specified type.

        Args:
            solver_type (str): The type of solver to create ('basic', 'csp', 'astar', 'astar_boost')
            game: The game instance to create a solver for

        Returns:
            A solver instance
        """
        if solver_type == "basic":
            return GreedySolver(game)
        elif solver_type == "csp":
            return MinesweeperSolver(game)
        elif solver_type == "astar":
            # This will be implemented later
            return AstarSolver(game)
        elif solver_type == "astar_boost":
            # This will be implemented later
            return AstarBoostedSolver(game)
        else:
            # Default to basic solver
            return MinesweeperSolver(game)


class MinesweeperBackend:
    def __init__(
        self, width: int, height: int, num_mines: int, solver_type: str = "basic"
    ):
        """
        Initialize a new Minesweeper game backend.

        Args:
            width (int): Width of the game board
            height (int): Height of the game board
            num_mines (int): Number of mines to place
            solver_type (str): Type of solver to use ('basic', 'csp', 'astar', 'astar_boost')
        """
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flagged = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.won = False
        self.solver_type = solver_type
        self._place_mines()
        self._calculate_numbers()
        self.solver = SolverFactory.create_solver(solver_type, self)
        self.nb_explosions = 0

    def _place_mines(self):
        """Place mines randomly on the board."""
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        mine_positions = random.sample(positions, self.num_mines)
        for x, y in mine_positions:
            self.grid[y][x] = -1  # -1 represents a mine

    def _calculate_numbers(self):
        """Calculate the numbers for each cell based on adjacent mines."""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == -1:
                    continue
                count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if (dx == 0 and dy == 0) or not (
                            0 <= nx < self.width and 0 <= ny < self.height
                        ):
                            continue
                        if self.grid[ny][nx] == -1:
                            count += 1
                self.grid[y][x] = count

    def reveal(self, x: int, y: int) -> bool:
        """
        Reveal a cell at the given coordinates.

        Args:
            x (int): X coordinate
            y (int): Y coordinate

        Returns:
            bool: True if the game is still ongoing, False if game over
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        if self.flagged[y][x] or self.revealed[y][x]:
            return True

        self.revealed[y][x] = True

        if self.grid[y][x] == -1:
            self.nb_explosions += 1
            self.revealed[y][x] = False
            self.toggle_flag(x, y)
            return True

        if self.grid[y][x] == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if (dx == 0 and dy == 0) or not (
                        0 <= nx < self.width and 0 <= ny < self.height
                    ):
                        continue
                    self.reveal(nx, ny)

        if self._check_win():
            self.won = True
            self.game_over = True

        return not self.game_over

    def toggle_flag(self, x: int, y: int):
        """
        Toggle the flag state of a cell.

        Args:
            x (int): X coordinate
            y (int): Y coordinate
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if not self.revealed[y][x]:
            self.flagged[y][x] = not self.flagged[y][x]
        if self._check_win():
            self.won = True
            self.game_over = True

    def _check_win(self) -> bool:
        """Check if the game has been won."""
        print("Checking if won")
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == -1 and not self.flagged[y][x]:
                    return False
                if self.grid[y][x] != -1 and not self.revealed[y][x]:
                    return False
        print("Game won")
        return True

    def get_game_state(self) -> dict:
        """
        Get the current state of the game.

        Returns:
            dict: Dictionary containing the game state
        """
        return {
            "grid": self.grid,
            "revealed": self.revealed,
            "flagged": self.flagged,
            "game_over": self.game_over,
            "won": self.won,
            "width": self.width,
            "height": self.height,
            "num_mines": self.num_mines,
            "solver_type": self.solver_type,
        }

    def change_solver(self, solver_type: str):
        """
        Change the solver type.

        Args:
            solver_type (str): The new solver type
        """
        self.solver_type = solver_type
        self.solver = SolverFactory.create_solver(solver_type, self)

    def solve_next_move(self) -> Optional[Tuple[int, int]]:
        """
        Get the next move from the solver.

        Returns:
            Optional[Tuple[int, int]]: The next move coordinates or None if no move is available
        """
        if self.game_over:
            return None

        if self.solver.solve_step():
            if self.solver.safe_moves:
                return self.solver.safe_moves[0]
            if self.solver.flagged_cells:
                return self.solver.flagged_cells[0]
        return None

    def apply_solver_move(self) -> bool:
        """
        Apply the next move from the solver.

        Returns:
            bool: True if a move was applied, False otherwise
        """
        print("Applying solver move")
        print("Actual count of explosions: ", self.nb_explosions)
        return self.solver.apply_moves()

    def reset_game(self):
        """Reset the game to its initial state."""
        print("Resetting game")
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.revealed = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.flagged = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.game_over = False
        self.won = False
        self._place_mines()
        self._calculate_numbers()
        self.solver = SolverFactory.create_solver(self.solver_type, self)
        self.nb_explosions = 0

    def solve_game(self, max_iterations: int = 1000) -> dict:
        """
        Attempt to solve the entire Minesweeper game in one go.

        Args:
            max_iterations (int): Maximum number of solver steps to prevent infinite loops

        Returns:
            dict: A dictionary containing game solve results
                - 'success': Boolean indicating if the game was solved
                - 'iterations': Number of iterations taken
                - 'explosions': Number of mine explosions
                - 'won': Boolean indicating if the game was won
        """
        # Reset tracking variables
        iterations = 0
        initial_explosions = self.nb_explosions

        # Attempt to solve the game
        while not self.game_over and iterations < max_iterations:
            # Try to get and apply the next solver move
            move = self.solve_next_move()
            
            # If no move is available, break the loop
            if move is None:
                break
            
            # Apply the solver move
            move_result = self.apply_solver_move()
            
            # Increment iterations
            iterations += 1

            # Break if the game is over (won or lost)
            if self.game_over:
                break

        # Prepare and return results
        return {
            'success': self.won,
            'iterations': iterations,
            'explosions': self.nb_explosions - initial_explosions,
            'won': self.won
        }