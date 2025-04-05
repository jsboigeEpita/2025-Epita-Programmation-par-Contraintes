import time
import random
import statistics
import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import numpy as np

from backend import MinesweeperBackend
from solver import MinesweeperSolver


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

        # Results data structure
        self.results = {}

    def run_benchmark(
        self,
        num_games: int = 100,
        difficulties: Optional[List[str]] = None,
        fixed_seed: Optional[int] = None,
    ):
        """Run the benchmark.

        Args:
            num_games: Number of games to run per difficulty
            difficulties: List of difficulty levels to test
            fixed_seed: Fixed random seed for reproducibility
        """
        if fixed_seed is not None:
            random.seed(fixed_seed)

        difficulties = difficulties or list(self.difficulty_presets.keys())

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
                f"Benchmarking {difficulty} difficulty: {width}x{height} with {num_mines} mines"
            )
            print(f"Running {num_games} games...")

            difficulty_results = []

            for game_num in range(num_games):
                # Progress update every 10% of games
                if game_num % max(1, num_games // 10) == 0:
                    print(
                        f"  Progress: {game_num}/{num_games} games ({game_num/num_games*100:.1f}%)"
                    )

                game_result = self._run_single_game(width, height, num_mines)
                difficulty_results.append(game_result)

            # Process and store results for this difficulty
            self.results[difficulty] = self._process_difficulty_results(
                difficulty_results
            )

            # Print summary for this difficulty
            self._print_difficulty_summary(difficulty)

        # Save all results
        self._save_results()

        # Generate plots
        self._generate_plots()

    def _run_single_game(self, width: int, height: int, num_mines: int) -> Dict:
        """Run a single game with the solver.

        Args:
            width: Width of the board
            height: Height of the board
            num_mines: Number of mines

        Returns:
            Dictionary with game results
        """
        game = MinesweeperBackend(width, height, num_mines)
        solver = MinesweeperSolver(game)

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
        while game_continues:
            # Run solver step
            solver.solve_step()

            # Check what the solver found
            prev_safe_moves_count = len(solver.safe_moves)
            prev_flagged_cells_count = len(solver.flagged_cells)

            # Apply the moves
            move_applied = solver.apply_moves()

            if not move_applied:
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

        # Calculate other metrics
        total_cells = width * height
        revealed_cells = sum(sum(1 for cell in row if cell) for row in game.revealed)
        revealed_percentage = (revealed_cells / (total_cells - num_mines)) * 100

        # Prepare results
        result = {
            "width": width,
            "height": height,
            "num_mines": num_mines,
            "won": game.won,
            "moves": moves,
            "safe_moves": safe_moves,
            "flag_moves": flag_moves,
            "guess_moves": guess_moves,
            "elapsed_time": elapsed_time,
            "revealed_cells": revealed_cells,
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

    def _print_difficulty_summary(self, difficulty: str):
        """Print summary of results for a difficulty level.

        Args:
            difficulty: Difficulty level
        """
        results = self.results[difficulty]

        print(f"\nResults for {difficulty} difficulty:")
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

    def _save_results(self):
        """Save benchmark results to files."""
        # Create timestamp for the results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save raw results as JSON
        results_with_metadata = {
            "timestamp": timestamp,
            "difficulties": self.difficulty_presets,
            "results": {k: v for k, v in self.results.items() if k != "raw_results"},
        }

        results_file = os.path.join(self.output_dir, f"benchmark_{timestamp}.json")
        with open(results_file, "w") as f:
            json.dump(results_with_metadata, f, indent=2)

        print(f"\nResults saved to {results_file}")

    def _generate_plots(self):
        """Generate plots from the benchmark results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Bar chart for win rates
        self._plot_win_rates(timestamp)

        # Bar chart for move types
        self._plot_move_types(timestamp)

        # Bar chart for revealed percentages
        self._plot_revealed_percentages(timestamp)

    def _plot_win_rates(self, timestamp: str):
        """Plot win rates across difficulties.

        Args:
            timestamp: Timestamp string for the filename
        """
        difficulties = list(self.results.keys())
        win_rates = [self.results[d]["win_rate"] for d in difficulties]

        plt.figure(figsize=(10, 6))
        bars = plt.bar(difficulties, win_rates, color="skyblue")

        plt.xlabel("Difficulty")
        plt.ylabel("Win Rate (%)")
        plt.title("Solver Win Rate by Difficulty")
        plt.ylim(0, 100)

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                f"{height:.1f}%",
                ha="center",
                va="bottom",
            )

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()

        # Save the plot
        plot_file = os.path.join(self.output_dir, f"win_rates_{timestamp}.png")
        plt.savefig(plot_file)
        plt.close()

        print(f"Win rate plot saved to {plot_file}")

    def _plot_move_types(self, timestamp: str):
        """Plot move type breakdown across difficulties.

        Args:
            timestamp: Timestamp string for the filename
        """
        difficulties = list(self.results.keys())
        safe_moves = [self.results[d]["avg_safe_moves"] for d in difficulties]
        flag_moves = [self.results[d]["avg_flag_moves"] for d in difficulties]
        guess_moves = [self.results[d]["avg_guess_moves"] for d in difficulties]

        plt.figure(figsize=(10, 6))

        x = np.arange(len(difficulties))
        width = 0.25

        plt.bar(x - width, safe_moves, width, label="Safe Moves", color="green")
        plt.bar(x, flag_moves, width, label="Flag Moves", color="red")
        plt.bar(x + width, guess_moves, width, label="Guess Moves", color="blue")

        plt.xlabel("Difficulty")
        plt.ylabel("Average Number of Moves")
        plt.title("Solver Move Type Breakdown by Difficulty")
        plt.xticks(x, difficulties)
        plt.legend()

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()

        # Save the plot
        plot_file = os.path.join(self.output_dir, f"move_types_{timestamp}.png")
        plt.savefig(plot_file)
        plt.close()

        print(f"Move types plot saved to {plot_file}")

    def _plot_revealed_percentages(self, timestamp: str):
        """Plot revealed percentages across difficulties.

        Args:
            timestamp: Timestamp string for the filename
        """
        difficulties = list(self.results.keys())
        revealed_percentages = [
            self.results[d]["avg_revealed_percentage"] for d in difficulties
        ]
        stds = [self.results[d]["std_revealed_percentage"] for d in difficulties]

        plt.figure(figsize=(10, 6))
        bars = plt.bar(
            difficulties, revealed_percentages, yerr=stds, capsize=5, color="purple"
        )

        plt.xlabel("Difficulty")
        plt.ylabel("Revealed Cells (%)")
        plt.title("Average Percentage of Revealed Cells by Difficulty")
        plt.ylim(0, 100)

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                f"{height:.1f}%",
                ha="center",
                va="bottom",
            )

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()

        # Save the plot
        plot_file = os.path.join(
            self.output_dir, f"revealed_percentages_{timestamp}.png"
        )
        plt.savefig(plot_file)
        plt.close()

        print(f"Revealed percentages plot saved to {plot_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Run benchmark tests on the Minesweeper solver"
    )
    parser.add_argument(
        "--games", type=int, default=100, help="Number of games per difficulty"
    )
    parser.add_argument(
        "--difficulties",
        nargs="+",
        choices=["beginner", "intermediate", "expert"],
        default=["beginner", "intermediate", "expert"],
        help="Difficulties to benchmark",
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
        num_games=args.games, difficulties=args.difficulties, fixed_seed=args.seed
    )


if __name__ == "__main__":
    main()
