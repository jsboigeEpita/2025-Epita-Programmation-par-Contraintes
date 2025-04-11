# Connect 4 AI Project

## Setup

To install the necessary dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Running the Game

To play the Connect 4 game, execute the following command:

```bash
python game.py
```

## Running the Benchmark

To benchmark the AI implementations, use the benchmark script:

```bash
python benchmark.py [OPTIONS]
```

### Benchmark Options

You can customize the benchmark execution with the following command-line arguments:

*   `--games <number>`: Specify the number of games to play per AI pairing. (Default: `NUM_GAMES`)
*   `--timeout <seconds>`: Set the maximum time allowed for each move in seconds. (Default: `TIMEOUT`)
*   `--ai-folder <path>`: Define the path to the folder containing the AI modules. (Default: `AI_FOLDER`)
*   `--save`: If included, save the benchmark results to a file.

*Note: Replace `NUM_GAMES`, `TIMEOUT`, and `AI_FOLDER` with their actual default values if known, or remove them if they are not defined constants.*