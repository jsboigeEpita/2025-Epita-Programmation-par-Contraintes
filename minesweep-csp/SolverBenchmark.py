import time, random, statistics, argparse, os
from datetime import datetime
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np

from backend import MinesweeperBackend


class SolverBenchmark:
    """Benchmark for the Minesweeper solver."""

    def __init__(
        self,
        difficulty_presets: Optional[Dict] = None,
        output_dir: str = "benchmark_results",
    ):
        """Initialize the benchmark.

        Args:
            difficulty_presets: Dictionary of difficulty presets to test
            output_dir: Directory to save results
        """
        self.difficulty_presets = difficulty_presets or {
            "beginner": {"width": 9, "height": 9, "num_mines": 10},
            "intermediate": {"width": 16, "height": 16, "num_mines": 40},
            "expert": {"width": 30, "height": 16, "num_mines": 99},
        }

        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # All available solvers
        self.solvers = ["basic", "csp", "astar", "astar_boost"]

        # Results data structure
        self.results = {}

    def run_benchmark(
        self,
        num_games: int = 100,
        difficulties: Optional[List[str]] = None,
        solvers: Optional[List[str]] = None,
        fixed_seed: Optional[int] = None,
    ):
        """Run the benchmark.

        Args:
            num_games: Number of games to run per difficulty
            difficulties: List of difficulty levels to test
            solvers: List of solvers to test
            fixed_seed: Fixed random seed for reproducibility
        """
        if fixed_seed is not None:
            random.seed(fixed_seed)

        difficulties = difficulties or list(self.difficulty_presets.keys())
        solvers = solvers or self.solvers

        for solver_type in solvers:
            print(f"\n===== Benchmarking solver: {solver_type} =====\n")
            self.results[solver_type] = {}

            for difficulty in difficulties:
                if difficulty not in self.difficulty_presets:
                    print(f"Warning: Unknown difficulty '{difficulty}'. Skipping.")
                    continue

                preset = self.difficulty_presets[difficulty]
                width, height, num_mines = (
                    preset["width"],
                    preset["height"],
                    preset["num_mines"],
                )

                print(
                    f"Benchmarking {difficulty} difficulty with {solver_type} solver: {width}x{height} with {num_mines} mines"
                )
                print(f"Running {num_games} games...")

                difficulty_results = []

                for game_num in range(num_games):
                    # Progress update every 10% of games
                    if game_num % max(1, num_games // 10) == 0:
                        print(
                            f"  Progress: {game_num}/{num_games} games ({game_num/num_games*100:.1f}%)"
                        )

                    game_result = self._run_single_game(
                        width, height, num_mines, solver_type
                    )
                    difficulty_results.append(game_result)

                # Process and store results for this difficulty
                self.results[solver_type][difficulty] = (
                    self._process_difficulty_results(difficulty_results)
                )

                # Print summary for this difficulty
                self._print_difficulty_summary(solver_type, difficulty)

        # Generate plots
        self._generate_plots()

    def _run_single_game(
        self, width: int, height: int, num_mines: int, solver_type: str
    ) -> Dict:
        """Run a single game with the solver.

        Args:
            width: Width of the board
            height: Height of the board
            num_mines: Number of mines
            solver_type: Type of solver to use

        Returns:
            Dictionary with game results
        """
        game = MinesweeperBackend(width, height, num_mines, solver_type)

        # First move - let's pick a random cell to start
        start_x, start_y = random.randint(0, width - 1), random.randint(0, height - 1)
        game_continues = game.reveal(start_x, start_y)

        # Track metrics
        moves = 1
        safe_moves = 0
        flag_moves = 0
        guess_moves = 0

        start_time = time.time()

        # Continue making moves until the game is over
        while game_continues and not game.game_over:
            # Run solver step
            game.solver.solve_step()

            # Check what the solver found
            prev_safe_moves_count = len(game.solver.safe_moves)
            prev_flagged_cells_count = len(game.solver.flagged_cells)

            # Apply the moves
            move_applied = game.solver.apply_moves()

            if not move_applied:
                # One last check if we've won
                if game._check_win():
                    game.won = True
                    game.game_over = True
                    break
                else:
                    # No moves were applied, game is stuck
                    break

            # Count the types of moves
            if prev_safe_moves_count > 0:
                if prev_safe_moves_count > 1:
                    # Trivial safe move (from number constraint)
                    safe_moves += 1
                else:
                    # Guess (from probability)
                    guess_moves += 1

            if prev_flagged_cells_count > 0:
                flag_moves += prev_flagged_cells_count

            moves += 1

            # Check if the game is still ongoing
            if game.game_over:
                game_continues = False

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Double-check win condition
        if not game.game_over and game._check_win():
            game.won = True
            game.game_over = True

        # Calculate other metrics
        total_cells = width * height
        revealed_cells = sum(sum(1 for cell in row if cell) for row in game.revealed)
        flagged_cells = sum(sum(1 for cell in row if cell) for row in game.flagged)
        revealed_percentage = (revealed_cells / (total_cells - num_mines)) * 100

        # Prepare results
        result = {
            "width": width,
            "height": height,
            "num_mines": num_mines,
            "solver_type": solver_type,
            "won": game.won,
            "moves": moves,
            "safe_moves": safe_moves,
            "flag_moves": flag_moves,
            "guess_moves": guess_moves,
            "elapsed_time": elapsed_time,
            "revealed_cells": revealed_cells,
            "flagged_cells": flagged_cells,
            "total_cells": total_cells,
            "revealed_percentage": revealed_percentage,
        }

        return result

    def _process_difficulty_results(self, results: List[Dict]) -> Dict:
        """Process results for a difficulty level.

        Args:
            results: List of game results

        Returns:
            Dictionary with processed results
        """
        # Calculate win rate
        win_rate = sum(1 for r in results if r["won"]) / len(results) * 100

        # Calculate averages
        avg_moves = statistics.mean(r["moves"] for r in results)
        avg_safe_moves = statistics.mean(r["safe_moves"] for r in results)
        avg_flag_moves = statistics.mean(r["flag_moves"] for r in results)
        avg_guess_moves = statistics.mean(r["guess_moves"] for r in results)
        avg_time = statistics.mean(r["elapsed_time"] for r in results)
        avg_revealed_percentage = statistics.mean(
            r["revealed_percentage"] for r in results
        )

        # Calculate standard deviations
        std_moves = (
            statistics.stdev(r["moves"] for r in results) if len(results) > 1 else 0
        )
        std_safe_moves = (
            statistics.stdev(r["safe_moves"] for r in results)
            if len(results) > 1
            else 0
        )
        std_flag_moves = (
            statistics.stdev(r["flag_moves"] for r in results)
            if len(results) > 1
            else 0
        )
        std_guess_moves = (
            statistics.stdev(r["guess_moves"] for r in results)
            if len(results) > 1
            else 0
        )
        std_time = (
            statistics.stdev(r["elapsed_time"] for r in results)
            if len(results) > 1
            else 0
        )
        std_revealed_percentage = (
            statistics.stdev(r["revealed_percentage"] for r in results)
            if len(results) > 1
            else 0
        )

        return {
            "game_count": len(results),
            "win_rate": win_rate,
            "avg_moves": avg_moves,
            "avg_safe_moves": avg_safe_moves,
            "avg_flag_moves": avg_flag_moves,
            "avg_guess_moves": avg_guess_moves,
            "avg_time": avg_time,
            "avg_revealed_percentage": avg_revealed_percentage,
            "std_moves": std_moves,
            "std_safe_moves": std_safe_moves,
            "std_flag_moves": std_flag_moves,
            "std_guess_moves": std_guess_moves,
            "std_time": std_time,
            "std_revealed_percentage": std_revealed_percentage,
            "raw_results": results,
        }

    def _print_difficulty_summary(self, solver_type: str, difficulty: str):
        """Print summary of results for a difficulty level.

        Args:
            solver_type: Type of solver
            difficulty: Difficulty level
        """
        results = self.results[solver_type][difficulty]

        print(f"\nResults for {solver_type} solver on {difficulty} difficulty:")
        print(f"  Win rate: {results['win_rate']:.2f}%")
        print(
            f"  Average moves: {results['avg_moves']:.2f} ± {results['std_moves']:.2f}"
        )
        print(
            f"  Average time: {results['avg_time']:.3f}s ± {results['std_time']:.3f}s"
        )
        print(
            f"  Average revealed percentage: {results['avg_revealed_percentage']:.2f}% ± {results['std_revealed_percentage']:.2f}%"
        )
        print(f"  Move breakdown:")
        print(
            f"    Safe moves: {results['avg_safe_moves']:.2f} ± {results['std_safe_moves']:.2f}"
        )
        print(
            f"    Flag moves: {results['avg_flag_moves']:.2f} ± {results['std_flag_moves']:.2f}"
        )
        print(
            f"    Guess moves: {results['avg_guess_moves']:.2f} ± {results['std_guess_moves']:.2f}"
        )

    def _generate_plots(self):
        """Generate plots from the benchmark results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Bar chart for win rates comparing solvers
        self._plot_win_rates_comparison(timestamp)

        # Bar chart for move types per solver
        self._plot_move_types_per_solver(timestamp)

        # Bar chart for revealed percentages per solver
        self._plot_revealed_percentages_comparison(timestamp)

    def _plot_win_rates_comparison(self, timestamp: str):
        """Plot win rates across difficulties and solvers.

        Args:
            timestamp: Timestamp string for the filename
        """
        difficulties = list(next(iter(self.results.values())).keys())
        solvers = list(self.results.keys())

        fig, ax = plt.subplots(figsize=(12, 8))

        # Set width of bars
        bar_width = 0.2
        index = np.arange(len(difficulties))

        # Colors for different solvers
        colors = ["skyblue", "lightgreen", "salmon", "purple"]

        # Plot bars for each solver
        for i, solver in enumerate(solvers):
            win_rates = [self.results[solver][d]["win_rate"] for d in difficulties]
            bars = ax.bar(
                index + i * bar_width,
                win_rates,
                bar_width,
                label=solver,
                color=colors[i % len(colors)],
            )

            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 1,
                    f"{height:.1f}%",
                    ha="center",
                    va="bottom",
                )

        ax.set_xlabel("Difficulty")
        ax.set_ylabel("Win Rate (%)")
        ax.set_title("Solver Win Rate by Difficulty and Solver Type")
        ax.set_xticks(index + bar_width * (len(solvers) - 1) / 2)
        ax.set_xticklabels(difficulties)
        ax.set_ylim(0, 110)  # Give some space for the labels
        ax.legend()

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()

        # Save the plot
        plot_file = os.path.join(
            self.output_dir, f"win_rates_comparison_{timestamp}.png"
        )
        plt.savefig(plot_file)
        plt.close()

        print(f"Win rate comparison plot saved to {plot_file}")

    def _plot_move_types_per_solver(self, timestamp: str):
        """Plot move type breakdown across solvers for each difficulty.

        Args:
            timestamp: Timestamp string for the filename
        """
        difficulties = list(next(iter(self.results.values())).keys())
        solvers = list(self.results.keys())

        for difficulty in difficulties:
            fig, ax = plt.subplots(figsize=(12, 8))

            # Set width of bars
            bar_width = 0.25
            index = np.arange(len(solvers))

            # Extract data for each move type
            safe_moves = [
                self.results[solver][difficulty]["avg_safe_moves"] for solver in solvers
            ]
            flag_moves = [
                self.results[solver][difficulty]["avg_flag_moves"] for solver in solvers
            ]
            guess_moves = [
                self.results[solver][difficulty]["avg_guess_moves"]
                for solver in solvers
            ]

            # Plot bars
            ax.bar(
                index - bar_width,
                safe_moves,
                bar_width,
                label="Safe Moves",
                color="green",
            )
            ax.bar(index, flag_moves, bar_width, label="Flag Moves", color="red")
            ax.bar(
                index + bar_width,
                guess_moves,
                bar_width,
                label="Guess Moves",
                color="blue",
            )

            ax.set_xlabel("Solver Type")
            ax.set_ylabel("Average Number of Moves")
            ax.set_title(
                f"Move Type Breakdown by Solver Type ({difficulty} difficulty)"
            )
            ax.set_xticks(index)
            ax.set_xticklabels(solvers)
            ax.legend()

            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()

            # Save the plot
            plot_file = os.path.join(
                self.output_dir, f"move_types_{difficulty}_{timestamp}.png"
            )
            plt.savefig(plot_file)
            plt.close()

            print(f"Move types plot for {difficulty} saved to {plot_file}")

    def _plot_revealed_percentages_comparison(self, timestamp: str):
        """Plot revealed percentages across difficulties and solvers.

        Args:
            timestamp: Timestamp string for the filename
        """
        difficulties = list(next(iter(self.results.values())).keys())
        solvers = list(self.results.keys())

        fig, ax = plt.subplots(figsize=(12, 8))

        # Set width of bars
        bar_width = 0.2
        index = np.arange(len(difficulties))

        # Colors for different solvers
        colors = ["green", "blue", "orange", "purple"]

        # Plot bars for each solver
        for i, solver in enumerate(solvers):
            revealed_percentages = [
                self.results[solver][d]["avg_revealed_percentage"] for d in difficulties
            ]
            stds = [
                self.results[solver][d]["std_revealed_percentage"] for d in difficulties
            ]

            bars = ax.bar(
                index + i * bar_width,
                revealed_percentages,
                bar_width,
                label=solver,
                color=colors[i % len(colors)],
                yerr=stds,
                capsize=5,
            )

            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 1,
                    f"{height:.1f}%",
                    ha="center",
                    va="bottom",
                )

        ax.set_xlabel("Difficulty")
        ax.set_ylabel("Revealed Cells (%)")
        ax.set_title(
            "Average Percentage of Revealed Cells by Difficulty and Solver Type"
        )
        ax.set_xticks(index + bar_width * (len(solvers) - 1) / 2)
        ax.set_xticklabels(difficulties)
        ax.set_ylim(0, 110)  # Give some space for the labels
        ax.legend()

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()

        # Save the plot
        plot_file = os.path.join(
            self.output_dir, f"revealed_percentages_comparison_{timestamp}.png"
        )
        plt.savefig(plot_file)
        plt.close()

        print(f"Revealed percentages comparison plot saved to {plot_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Run benchmark tests on the Minesweeper solvers"
    )
    parser.add_argument(
        "--games", type=int, default=10, help="Number of games per difficulty"
    )
    parser.add_argument(
        "--difficulties",
        nargs="+",
        choices=["beginner", "intermediate", "expert"],
        default=["beginner", "intermediate"],
        help="Difficulties to benchmark",
    )
    parser.add_argument(
        "--solvers",
        nargs="+",
        choices=["basic", "csp", "astar", "astar_boost"],
        default=["basic", "csp", "astar", "astar_boost"],
        help="Solvers to benchmark",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="benchmark_results",
        help="Directory to save results",
    )

    args = parser.parse_args()

    benchmark = SolverBenchmark(output_dir=args.output_dir)
    benchmark.run_benchmark(
        num_games=args.games,
        difficulties=args.difficulties,
        solvers=args.solvers,
        fixed_seed=args.seed,
    )


if __name__ == "__main__":
    main()
