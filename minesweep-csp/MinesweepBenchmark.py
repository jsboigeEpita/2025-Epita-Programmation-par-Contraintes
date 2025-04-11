import time
import random
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
from backend import MinesweeperBackend
from tqdm import tqdm


class MinesweeperBenchmark:
    """Benchmark class for evaluating Minesweeper solvers."""

    def __init__(self, board_sizes=None, mine_densities=None, num_trials=50):
        self.board_sizes = board_sizes or [
            (9, 9),
            (16, 16),
            (30, 16),
        ]
        self.mine_densities = mine_densities or [
            10,
            15,
            20,
            25,
        ]
        self.num_trials = num_trials
        self.solver_types = ["greedy", "astar", "astar_boost"]  # All three solvers
        self.results = defaultdict(list)

    def run_benchmark(self):
        """Run the benchmarking process across all configurations."""
        self.results = defaultdict(list)

        total_tests = (
            len(self.board_sizes)
            * len(self.mine_densities)
            * len(self.solver_types)
            * self.num_trials
        )
        with tqdm(total=total_tests, desc="Running benchmarks") as pbar:
            for width, height in self.board_sizes:
                for density in self.mine_densities:
                    total_cells = width * height
                    num_mines = int(total_cells * density / 100)

                    for solver_type in self.solver_types:
                        for trial in range(self.num_trials):
                            random.seed(width * height * density * trial)

                            # Create a new game
                            start_time = time.time()
                            game = MinesweeperBackend(
                                width, height, num_mines, solver_type
                            )

                            # Solve the game
                            solve_result = game.solve_game(max_iterations=10000)
                            end_time = time.time()

                            # Record results
                            self.results["board_size"].append(f"{width}x{height}")
                            self.results["density"].append(density)
                            self.results["solver"].append(solver_type)
                            self.results["num_mines"].append(num_mines)
                            self.results["success"].append(solve_result["success"])
                            self.results["iterations"].append(
                                solve_result["iterations"]
                            )
                            self.results["explosions"].append(
                                solve_result["explosions"]
                            )
                            self.results["time"].append(end_time - start_time)

                            pbar.update(1)

        self.df_results = pd.DataFrame(self.results)
        return self.df_results

    def generate_reports(self, output_dir="benchmarks"):
        if not hasattr(self, "df_results"):
            raise ValueError("No benchmark results available. Run benchmark first.")

        self._plot_performance_by_density(
            save_path=os.path.join(output_dir, "performance_by_density.png")
        )
        self._plot_time_comparison(
            save_path=os.path.join(output_dir, "time_comparison.png")
        )

    def _plot_performance_by_density(self, save_path=None):
        """Plot performance metrics by mine density."""
        # Create line plots for explosions and success rate by density
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        colors = ["#ff9999", "#66b3ff", "#99ff99"]  # Different colors for each solver
        markers = ["o", "s", "^"]  # Different markers for each solver

        for i, solver in enumerate(self.solver_types):
            solver_data = self.df_results[self.df_results["solver"] == solver]

            # Group by density
            density_grouped = solver_data.groupby("density")

            # Plot explosions by density
            explosions = density_grouped["explosions"].mean()
            ax1.plot(
                explosions.index,
                explosions.values,
                marker=markers[i],
                color=colors[i],
                linewidth=2,
                label=f"{solver} Solver",
            )

            # Plot success rate by density
            success_rate = density_grouped["success"].mean() * 100
            ax2.plot(
                success_rate.index,
                success_rate.values,
                marker=markers[i],
                color=colors[i],
                linewidth=2,
                label=f"{solver} Solver",
            )

        ax1.set_xlabel("Mine Density (%)")
        ax1.set_ylabel("Average Explosions")
        ax1.set_title("Average Explosions by Mine Density")
        ax1.grid(True)
        ax1.legend()

        ax2.set_xlabel("Mine Density (%)")
        ax2.set_ylabel("Success Rate (%)")
        ax2.set_title("Success Rate by Mine Density")
        ax2.grid(True)
        ax2.legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)

        return plt.gcf()

    def _plot_time_comparison(self, save_path=None):
        """Plot the average solution time for each solver type."""
        grouped = self.df_results.groupby(["board_size", "density", "solver"])
        time_data = grouped["time"].mean().reset_index()

        # Create grouped bar chart
        board_sizes = time_data["board_size"].unique()
        densities = time_data["density"].unique()
        solver_types = time_data["solver"].unique()

        x = np.arange(len(board_sizes) * len(densities))
        width = 0.25  # Adjusted for three solvers

        fig, ax = plt.subplots(figsize=(16, 8))  # Made wider for more bars

        colors = ["#ff9999", "#66b3ff", "#99ff99"]  # Different colors for each solver

        for i, solver in enumerate(solver_types):
            solver_data = time_data[time_data["solver"] == solver]
            positions = []
            values = []

            for board in board_sizes:
                for density in densities:
                    idx = len(densities) * list(board_sizes).index(board) + list(
                        densities
                    ).index(density)
                    row = solver_data[
                        (solver_data["board_size"] == board)
                        & (solver_data["density"] == density)
                    ]
                    if not row.empty:
                        positions.append(idx)
                        values.append(row["time"].values[0])

            ax.bar(
                [p + (i * width) for p in positions],
                values,
                width,
                label=f"{solver} Solver",
                color=colors[i % len(colors)],
            )

        # Add labels, title, and custom x-axis tick labels
        ax.set_xlabel("Board Size and Mine Density")
        ax.set_ylabel("Average Solution Time (seconds)")
        ax.set_title("Average Solution Time by Solver Type")

        labels = [
            f"{board}\n{density}%" for board in board_sizes for density in densities
        ]
        ax.set_xticks(x + width)  # Adjusted for three bars
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)

        return plt.gcf()


if __name__ == "__main__":
    import os

    benchmark = MinesweeperBenchmark(
        num_trials=30,
    )

    os.makedirs("benchmarks", exist_ok=True)

    results = benchmark.run_benchmark()

    print("Generating reports...")
    summary = benchmark.generate_reports(output_dir="benchmarks")

    print("\nBenchmark Summary:")
    print(summary)

    print("All charts and data have been exported to the 'benchmarks' folder")
