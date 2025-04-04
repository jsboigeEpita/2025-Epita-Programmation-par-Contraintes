# Minesweeper CSP Solver

A Constraint Satisfaction Problem (CSP) implementation of Minesweeper with multiple solving strategies. This project provides a web interface for solving Minesweeper puzzles using different algorithms.

## Contributors

- Armand BLIN `(armand.blin@epita.fr)`
- Baptiste ARNOLD `(baptiste.anorld@epita.fr)`
- Angela SAADE `(angela.saade@epita.fr)`

## Features

- Web-based Minesweeper game interface
- Multiple solving algorithms with different strategies
- Benchmarking tools to compare solver performance
- Real-time visualization of solving process

## Solvers

The project implements three different solving strategies:

1. **Greedy Solver**

   - Makes random guesses when no obvious moves are available
   - Simple and fast but less effective
   - Good for basic gameplay

2. **A\* Solver**

   - Implements A\* search algorithm for Minesweeper
   - Uses heuristic-based approach to find safe moves
   - More sophisticated than the greedy approach
   - Handles trivial cases and makes educated guesses

3. **A\* Boosted Solver**
   - Enhanced version of the A\* solver
   - Implements probabilistic frontier solving
   - More advanced strategies for complex situations
   - Better performance on difficult boards

## Usage

1. Clone the repository
2. Start the program:
   ```bash
   ./start.sh
   ```

Then open your browser to `http://localhost:5000`

## Project Structure

- `app.py` - Main web application
- `backend.py` - Core game logic and solver integration
- `frontend/` - Web interface components
- `solvers/` - Different solving algorithms
  - `greedysolver.py`
  - `astarsolver.py`
  - `astarboostedsolver.py`
- `benchmarks/` - Benchmark results and tools
- `MinesweepBenchmark.py` - Benchmarking utility
