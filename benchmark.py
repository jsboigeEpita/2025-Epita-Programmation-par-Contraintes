import os
import importlib
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from itertools import permutations
import traceback
import sys
import argparse

from board import ConnectFourBoard

# Default values - can be overridden by command line arguments
AI_FOLDER = "./ai"
NUM_GAMES_PER_PAIRING = 5
MOVE_TIMEOUT_SECONDS = 5.0

def parse_arguments():
    """Parse command line arguments for benchmark configuration."""
    parser = argparse.ArgumentParser(description='Connect 4 AI Benchmark Tool')
    parser.add_argument('--games', type=int, default=NUM_GAMES_PER_PAIRING, 
                        help='Number of games per AI pairing')
    parser.add_argument('--timeout', type=float, default=MOVE_TIMEOUT_SECONDS,
                        help='Move timeout in seconds')
    parser.add_argument('--ai-folder', type=str, default=AI_FOLDER,
                        help='Path to folder containing AI modules')
    parser.add_argument('--save', action='store_true',
                        help='Save results to file')
    return parser.parse_args()

def load_ais(folder_path):
    """Load all valid AI modules from the specified folder."""
    ais = []
    ai_folder_abs = os.path.abspath(folder_path)
    if not os.path.isdir(ai_folder_abs):
        print(f"Error: AI folder '{ai_folder_abs}' not found.")
        return ais

    print(f"Loading AIs from: {ai_folder_abs}")
    sys.path.insert(0, os.path.dirname(ai_folder_abs))
    ai_module_parent = os.path.basename(ai_folder_abs)

    for filename in os.listdir(ai_folder_abs):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module_path = f"{ai_module_parent}.{module_name}"
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_move') and callable(module.get_move) and \
                   hasattr(module, 'name') and callable(module.name):
                    ai_name = module.name()
                    if any(a['name'] == ai_name for a in ais):
                        print(
                            f"  - Warning: Duplicate AI name '{ai_name}' found in {filename}. Skipping.")
                        continue
                    ais.append({
                        'name': ai_name,
                        'get_move': module.get_move,
                    })
            except Exception as e:
                print(
                    f"\n--- Error loading {filename}: {type(e).__name__}: {e} ---")
    if not ais:
        print(f"Warning: No valid AI modules found in {folder_path}")
    return ais


def play_game(ai1_info, ai2_info, move_timeout):
    """Play a single game between two AIs and return the result."""
    game_board = ConnectFourBoard()
    ais = {1: ai1_info, 2: ai2_info}
    current_player = 1
    error_info = None
    error_type = None

    while not game_board.game_over:
        current_ai_info = ais[current_player]
        board_state = game_board.get_board()

        try:
            start_time = time.time()
            col = current_ai_info['get_move'](board_state, current_player)
            duration = time.time() - start_time

            if duration > move_timeout:
                game_board.game_over = True
                game_board.winner = 3 - current_player
                error_info = {'type': 'Timeout'}
                error_type = 'timeout'
                break

            if col is None or not game_board.is_valid_location(col):
                game_board.game_over = True
                game_board.winner = 3 - current_player
                error_info = {'type': 'Invalid Move'}
                error_type = 'invalid_move'
                break

            game_board.drop_piece(col, current_player)

            if not game_board.game_over:
                current_player = 3 - current_player

        except Exception as e:
            # print(f"\nRuntime Error: {current_ai_info['name']} (P{
            # current_player}) - {type(e).__name__}")  # Optional debug
            # traceback.print_exc()  # Optional debug
            game_board.game_over = True
            game_board.winner = 3 - current_player
            error_info = {'type': 'Runtime Error'}
            error_type = 'runtime_error'
            break

    winner_player = game_board.winner
    # 1, 2, or 3 (Draw)
    final_winner = winner_player if winner_player is not None else 3

    return {
        'winner': final_winner,
        'ai1_name': ai1_info['name'],
        'ai2_name': ai2_info['name'],
        'error': bool(error_info),
        'error_type': error_type
    }


def run_benchmark(ais, num_games_per_pairing, timeout):
    """Run a full benchmark with all AI combinations."""
    if len(ais) < 2:
        print("Need at least two AIs.")
        return None

    results = []
    ai_names = [ai['name'] for ai in ais]
    total_pairings = len(ai_names) * (len(ai_names) - 1)
    games_to_play_total = total_pairings * num_games_per_pairing
    game_counter = 0

    print(f"\nStarting benchmark: {len(ais)} AIs, {
          num_games_per_pairing} games per ordered pair ({games_to_play_total} total games)")
    print(f"Move Timeout: {timeout} seconds")
    print("-" * 40)

    for ai1_idx, ai2_idx in permutations(range(len(ais)), 2):
        ai1 = ais[ai1_idx]
        ai2 = ais[ai2_idx]
        # Optional more verbose letsgoo
        print(f"Playing: {ai1['name']} (P1) vs {ai2['name']} (P2)...")

        for game_num in range(num_games_per_pairing):
            game_counter += 1
            print(f"  Progress: {
                  game_counter}/{games_to_play_total} games played...", end="\r")
            game_result = play_game(ai1, ai2, timeout)
            results.append(game_result)
        # Optional again...
        print(f"  Finished games for {
              ai1['name']} (P1) vs {ai2['name']} (P2).")

    print(f"\nBenchmark finished. Played {game_counter} games.")
    print("-" * 40)
    return results


def calculate_pairwise_win_rates(results, ai_names):
    """Calculate pairwise win rates between all AIs."""
    if not results:
        return None

    pairwise_raw = defaultdict(lambda: {'p1_wins': 0, 'games': 0})

    for res in results:
        ai1 = res['ai1_name']  # Player 1 in this game
        ai2 = res['ai2_name']  # Player 2 in this game
        winner = res['winner']
        pair_key = (ai1, ai2)

        pairwise_raw[pair_key]['games'] += 1
        if winner == 1:  # P1 won
            pairwise_raw[pair_key]['p1_wins'] += 1

    pairwise_win_rate_df = pd.DataFrame(
        index=ai_names, columns=ai_names, dtype=float).fillna(np.nan)

    for (p1_name, p2_name), data in pairwise_raw.items():
        total_games_this_pairing = data['games']
        if total_games_this_pairing > 0:
            win_rate = (data['p1_wins'] / total_games_this_pairing) * 100
            pairwise_win_rate_df.loc[p1_name, p2_name] = win_rate
        # else: leave as NaN

    return pairwise_win_rate_df


def calculate_overall_performance(results, ai_names):
    """Calculate overall performance metrics for each AI."""
    performance = {name: {'wins': 0, 'losses': 0, 'draws': 0, 'games_p1': 0, 'games_p2': 0} 
                  for name in ai_names}
    
    for res in results:
        ai1 = res['ai1_name']  # Player 1
        ai2 = res['ai2_name']  # Player 2
        winner = res['winner']
        
        # Count games played as P1/P2
        performance[ai1]['games_p1'] += 1
        performance[ai2]['games_p2'] += 1
        
        # Count wins/losses/draws
        if winner == 1:
            performance[ai1]['wins'] += 1
            performance[ai2]['losses'] += 1
        elif winner == 2:
            performance[ai2]['wins'] += 1
            performance[ai1]['losses'] += 1
        else:  # Draw
            performance[ai1]['draws'] += 1
            performance[ai2]['draws'] += 1
    
    # Create DataFrame with metrics
    df = pd.DataFrame(index=ai_names, columns=['Win %', 'Total Games', 'Wins', 'Losses', 'Draws', 'Games as P1', 'Games as P2'])
    
    for name in ai_names:
        data = performance[name]
        total_games = data['games_p1'] + data['games_p2']
        win_rate = (data['wins'] / total_games * 100) if total_games > 0 else 0
        
        df.loc[name] = [
            round(win_rate, 1),
            total_games,
            data['wins'],
            data['losses'],
            data['draws'],
            data['games_p1'],
            data['games_p2']
        ]
    
    # Sort by win percentage
    df = df.sort_values('Win %', ascending=False)
    return df


def analyze_errors(results):
    """Analyze and summarize errors by AI."""
    error_counts = defaultdict(lambda: {'timeout': 0, 'invalid_move': 0, 'runtime_error': 0, 'total': 0})
    
    for res in results:
        if not res['error']:
            continue
            
        # For simplicity, assume the loser caused the error
        if res['winner'] == 2:  # P1 made an error
            ai_name = res['ai1_name']
        elif res['winner'] == 1:  # P2 made an error
            ai_name = res['ai2_name']
        else:
            continue  # Shouldn't happen
            
        # Increment error counts
        error_type = res.get('error_type', 'runtime_error')  # Default to runtime if not specified
        error_counts[ai_name][error_type] += 1
        error_counts[ai_name]['total'] += 1
    
    # Create a DataFrame
    if error_counts:
        error_df = pd.DataFrame([(name, data['timeout'], data['invalid_move'], 
                                 data['runtime_error'], data['total']) 
                                for name, data in error_counts.items()],
                               columns=['AI Name', 'Timeouts', 'Invalid Moves', 'Runtime Errors', 'Total Errors'])
        return error_df.sort_values('Total Errors', ascending=False)
    return None


def plot_heatmap(pairwise_df, num_games_per_pairing):
    """Plot a heatmap of pairwise win rates."""
    if pairwise_df is None or pairwise_df.empty:
        print("No pairwise data to plot.")
        return

    num_ais = len(pairwise_df.columns)
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(
        figsize=(max(8, num_ais * 0.9), max(6, num_ais * 0.7)))

    sns.heatmap(pairwise_df,
                annot=True,
                fmt=".1f",
                cmap="coolwarm",
                linewidths=.5,
                linecolor='lightgray',
                cbar_kws={'label': 'Win Rate (%) of Row Player (P1)'},
                ax=ax,
                center=50.0,
                annot_kws={"size": 8})

    ax.set_title(f'Pairwise Win Rate (%) - Row AI (P1) vs Col AI (P2)\n({
                 num_games_per_pairing} games per matchup)')
    ax.set_xlabel('Opponent (Played as P2)')
    ax.set_ylabel('AI (Played as P1)')
    plt.setp(ax.get_xticklabels(), rotation=45,
             ha="right", rotation_mode="anchor")
    plt.setp(ax.get_yticklabels(), rotation=0)
    fig.tight_layout()
    return fig


def plot_overall_performance(overall_df):
    """Plot a bar chart of overall AI performance."""
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=overall_df.index, y='Win %', data=overall_df)
    ax.set_title('Overall AI Win Percentage')
    ax.set_xlabel('AI Algorithm')
    ax.set_ylabel('Win %')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return plt.gcf()


def save_results(pairwise_df, overall_df, error_df=None, filename="benchmark_results"):
    """Save benchmark results to CSV files."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    # Create results directory if it doesn't exist
    results_dir = "benchmark_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Save pairwise results
    pairwise_file = os.path.join(results_dir, f"{filename}_pairwise_{timestamp}.csv")
    pairwise_df.to_csv(pairwise_file)
    
    # Save overall results
    overall_file = os.path.join(results_dir, f"{filename}_overall_{timestamp}.csv")
    overall_df.to_csv(overall_file)
    
    # Save error analysis if available
    if error_df is not None and not error_df.empty:
        error_file = os.path.join(results_dir, f"{filename}_errors_{timestamp}.csv")
        error_df.to_csv(error_file)
        print(f"Results saved to:\n- {pairwise_file}\n- {overall_file}\n- {error_file}")
    else:
        print(f"Results saved to:\n- {pairwise_file}\n- {overall_file}")
    
    # Save plots as images
    pairwise_plot_file = os.path.join(results_dir, f"{filename}_heatmap_{timestamp}.png")
    plt.figure(1)
    plt.savefig(pairwise_plot_file, dpi=300, bbox_inches='tight')
    
    overall_plot_file = os.path.join(results_dir, f"{filename}_performance_{timestamp}.png")
    plt.figure(2)
    plt.savefig(overall_plot_file, dpi=300, bbox_inches='tight')
    
    print(f"Plots saved to:\n- {pairwise_plot_file}\n- {overall_plot_file}")


if __name__ == "__main__":
    print("=" * 50)
    print(" Connect-4 AI Benchmark Tool")
    print("=" * 50)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Update settings from arguments
    AI_FOLDER = args.ai_folder
    NUM_GAMES_PER_PAIRING = args.games
    MOVE_TIMEOUT_SECONDS = args.timeout
    SAVE_RESULTS = args.save

    loaded_ais = load_ais(AI_FOLDER)

    if not loaded_ais or len(loaded_ais) < 2:
        print("\nBenchmark requires at least two valid AIs.")
        sys.exit(1)

    ai_names_list = [ai['name'] for ai in loaded_ais]
    print(f"\nFound {len(loaded_ais)} AIs: {', '.join(ai_names_list)}")

    benchmark_results = run_benchmark(
        loaded_ais, NUM_GAMES_PER_PAIRING, MOVE_TIMEOUT_SECONDS)

    if benchmark_results:
        # Calculate pairwise statistics
        print("\nCalculating pairwise win rates...")
        pairwise_win_df = calculate_pairwise_win_rates(
            benchmark_results, ai_names_list)
        
        # Calculate overall performance
        print("Calculating overall performance metrics...")
        overall_df = calculate_overall_performance(
            benchmark_results, ai_names_list)
        
        # Analyze errors
        print("Analyzing errors...")
        error_df = analyze_errors(benchmark_results)

        if pairwise_win_df is not None:
            # Display results
            print("\n--- Pairwise Win Rate (%) [Row AI (P1) vs Col AI (P2)] ---")
            print(pairwise_win_df.round(1))
            
            print("\n--- Overall AI Performance ---")
            print(overall_df)
            
            if error_df is not None and not error_df.empty:
                print("\n--- Error Analysis ---")
                print(error_df)
            
            # Generate plots
            print("\nGenerating visualizations...")
            fig1 = plot_heatmap(pairwise_win_df, NUM_GAMES_PER_PAIRING)
            fig2 = plot_overall_performance(overall_df)
            
            # Save results if requested
            if SAVE_RESULTS:
                save_results(pairwise_win_df, overall_df, error_df)
            
            # Show plots
            plt.figure(1)
            plt.figure(2)
            print("Plots generated (close plot windows to exit script).")
            plt.show()
        else:
            print("Analysis failed, no data generated.")
    else:
        print("Benchmark run failed or produced no results.")

    print("\nBenchmark script finished.")