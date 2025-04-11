import os
import importlib
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from itertools import permutations
import sys
import argparse
from board import ConnectFourBoard

# Default values
AI_FOLDER = "./ai"
NUM_GAMES = 5
TIMEOUT = 5.0

def parse_arguments():
    parser = argparse.ArgumentParser(description='Connect 4 AI Benchmark')
    parser.add_argument('--games', type=int, default=NUM_GAMES, 
                        help='Games per AI pairing')
    parser.add_argument('--timeout', type=float, default=TIMEOUT,
                        help='Move timeout in seconds')
    parser.add_argument('--ai-folder', type=str, default=AI_FOLDER,
                        help='AI modules folder path')
    parser.add_argument('--save', action='store_true',
                        help='Save results to file')
    return parser.parse_args()

def load_ais(folder_path):
    ais = []
    folder_abs = os.path.abspath(folder_path)
    
    if not os.path.isdir(folder_abs):
        print(f"Error: AI folder '{folder_abs}' not found.")
        return ais

    print(f"Loading AIs from: {folder_abs}")
    sys.path.insert(0, os.path.dirname(folder_abs))
    module_parent = os.path.basename(folder_abs)

    for filename in os.listdir(folder_abs):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module_path = f"{module_parent}.{module_name}"
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_move') and callable(module.get_move) and \
                   hasattr(module, 'name') and callable(module.name):
                    ai_name = module.name()
                    if any(a['name'] == ai_name for a in ais):
                        print(f"  - Warning: Duplicate AI name '{ai_name}'. Skipping.")
                        continue
                    ais.append({
                        'name': ai_name,
                        'get_move': module.get_move,
                    })
            except Exception as e:
                print(f"\n--- Error loading {filename}: {type(e).__name__}: {e} ---")
    
    if not ais:
        print(f"Warning: No valid AI modules found in {folder_path}")
    return ais

def play_game(ai1, ai2, timeout):
    board = ConnectFourBoard()
    ais = {1: ai1, 2: ai2}
    player = 1
    error_type = None

    while not board.game_over:
        current_ai = ais[player]
        board_state = board.get_board()

        try:
            start_time = time.time()
            col = current_ai['get_move'](board_state, player)
            duration = time.time() - start_time

            if duration > timeout:
                board.game_over = True
                board.winner = 3 - player
                error_type = 'timeout'
                break

            if col is None or not board.is_valid_location(col):
                board.game_over = True
                board.winner = 3 - player
                error_type = 'invalid_move'
                break

            board.drop_piece(col, player)
            if not board.game_over:
                player = 3 - player

        except Exception:
            board.game_over = True
            board.winner = 3 - player
            error_type = 'runtime_error'
            break

    final_winner = board.winner if board.winner is not None else 3  # 3 = draw

    return {
        'winner': final_winner,
        'ai1_name': ai1['name'],
        'ai2_name': ai2['name'],
        'error': error_type is not None,
        'error_type': error_type
    }

def run_benchmark(ais, games_per_pair, timeout):
    if len(ais) < 2:
        print("Need at least two AIs.")
        return None

    results = []
    ai_names = [ai['name'] for ai in ais]
    total_pairings = len(ai_names) * (len(ai_names) - 1)
    total_games = total_pairings * games_per_pair
    game_count = 0

    print(f"\nStarting benchmark: {len(ais)} AIs, {games_per_pair} games per pair ({total_games} total)")
    print(f"Move Timeout: {timeout} seconds")
    print("-" * 40)

    for i, j in permutations(range(len(ais)), 2):
        ai1, ai2 = ais[i], ais[j]
        print(f"Playing: {ai1['name']} (P1) vs {ai2['name']} (P2)...")

        for _ in range(games_per_pair):
            game_count += 1
            print(f"  Progress: {game_count}/{total_games} games...", end="\r")
            results.append(play_game(ai1, ai2, timeout))
            
        print(f"  Finished: {ai1['name']} (P1) vs {ai2['name']} (P2)     ")

    print(f"\nBenchmark complete. Played {game_count} games.")
    print("-" * 40)
    return results

def calculate_pairwise_win_rates(results, ai_names):
    if not results:
        return None

    pairwise = defaultdict(lambda: {'p1_wins': 0, 'games': 0})

    for res in results:
        ai1 = res['ai1_name']
        ai2 = res['ai2_name']
        winner = res['winner']
        pair_key = (ai1, ai2)

        pairwise[pair_key]['games'] += 1
        if winner == 1:  # P1 won
            pairwise[pair_key]['p1_wins'] += 1

    win_rate_df = pd.DataFrame(index=ai_names, columns=ai_names, dtype=float).fillna(np.nan)

    for (p1, p2), data in pairwise.items():
        games = data['games']
        if games > 0:
            win_rate = (data['p1_wins'] / games) * 100
            win_rate_df.loc[p1, p2] = win_rate

    return win_rate_df

def calculate_overall_performance(results, ai_names):
    performance = {name: {'wins': 0, 'losses': 0, 'draws': 0, 'games_p1': 0, 'games_p2': 0} 
                  for name in ai_names}
    
    for res in results:
        ai1 = res['ai1_name']
        ai2 = res['ai2_name']
        winner = res['winner']
        
        performance[ai1]['games_p1'] += 1
        performance[ai2]['games_p2'] += 1
        
        if winner == 1:
            performance[ai1]['wins'] += 1
            performance[ai2]['losses'] += 1
        elif winner == 2:
            performance[ai2]['wins'] += 1
            performance[ai1]['losses'] += 1
        else:  # Draw
            performance[ai1]['draws'] += 1
            performance[ai2]['draws'] += 1
    
    df = pd.DataFrame(index=ai_names, 
                      columns=['Win %', 'Total Games', 'Wins', 'Losses', 'Draws', 
                              'Games as P1', 'Games as P2'])
    
    for name in ai_names:
        data = performance[name]
        total = data['games_p1'] + data['games_p2']
        win_rate = (data['wins'] / total * 100) if total > 0 else 0
        
        df.loc[name] = [
            round(win_rate, 1),
            total,
            data['wins'],
            data['losses'],
            data['draws'],
            data['games_p1'],
            data['games_p2']
        ]
    
    return df.sort_values('Win %', ascending=False)

def analyze_errors(results):
    errors = defaultdict(lambda: {'timeout': 0, 'invalid_move': 0, 'runtime_error': 0, 'total': 0})
    
    for res in results:
        if not res['error']:
            continue
            
        # Identify which AI caused the error
        if res['winner'] == 2:  # P1 made an error
            ai_name = res['ai1_name']
        elif res['winner'] == 1:  # P2 made an error
            ai_name = res['ai2_name']
        else:
            continue
            
        error_type = res.get('error_type', 'runtime_error')
        errors[ai_name][error_type] += 1
        errors[ai_name]['total'] += 1
    
    if errors:
        error_df = pd.DataFrame([(name, data['timeout'], data['invalid_move'], 
                                 data['runtime_error'], data['total']) 
                                for name, data in errors.items()],
                               columns=['AI Name', 'Timeouts', 'Invalid Moves', 
                                       'Runtime Errors', 'Total Errors'])
        return error_df.sort_values('Total Errors', ascending=False)
    return None

def plot_heatmap(df, games_per_pair):
    if df is None or df.empty:
        return None

    num_ais = len(df.columns)
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(max(8, num_ais * 0.9), max(6, num_ais * 0.7)))

    sns.heatmap(df,
                annot=True,
                fmt=".1f",
                cmap="coolwarm",
                linewidths=.5,
                linecolor='lightgray',
                cbar_kws={'label': 'Win Rate (%) of Row Player (P1)'},
                ax=ax,
                center=50.0,
                annot_kws={"size": 8})

    ax.set_title(f'Pairwise Win Rate (%) - Row AI (P1) vs Col AI (P2)\n({games_per_pair} games per matchup)')
    ax.set_xlabel('Opponent (P2)')
    ax.set_ylabel('AI (P1)')
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    plt.tight_layout()
    return fig

def plot_overall_performance(df):
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=df.index, y='Win %', data=df)
    ax.set_title('Overall AI Win Percentage')
    ax.set_xlabel('AI Algorithm')
    ax.set_ylabel('Win %')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return plt.gcf()

def save_results(pairwise_df, overall_df, error_df=None):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    results_dir = "benchmark_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Save data files
    pairwise_file = os.path.join(results_dir, f"benchmark_pairwise_{timestamp}.csv")
    pairwise_df.to_csv(pairwise_file)
    
    overall_file = os.path.join(results_dir, f"benchmark_overall_{timestamp}.csv")
    overall_df.to_csv(overall_file)
    
    files = [pairwise_file, overall_file]
    
    if error_df is not None and not error_df.empty:
        error_file = os.path.join(results_dir, f"benchmark_errors_{timestamp}.csv")
        error_df.to_csv(error_file)
        files.append(error_file)
    
    # Save plots
    heatmap_file = os.path.join(results_dir, f"benchmark_heatmap_{timestamp}.png")
    plt.figure(1)
    plt.savefig(heatmap_file, dpi=300, bbox_inches='tight')
    
    performance_file = os.path.join(results_dir, f"benchmark_performance_{timestamp}.png")
    plt.figure(2)
    plt.savefig(performance_file, dpi=300, bbox_inches='tight')
    
    print(f"Results saved to: {results_dir}/")

if __name__ == "__main__":
    print("=" * 50)
    print(" Connect-4 AI Benchmark Tool")
    print("=" * 50)
    
    args = parse_arguments()
    
    loaded_ais = load_ais(args.ai_folder)

    if not loaded_ais or len(loaded_ais) < 2:
        print("\nBenchmark requires at least two valid AIs.")
        sys.exit(1)

    ai_names = [ai['name'] for ai in loaded_ais]
    print(f"\nFound {len(loaded_ais)} AIs: {', '.join(ai_names)}")

    results = run_benchmark(loaded_ais, args.games, args.timeout)

    if results:
        print("\nCalculating statistics...")
        pairwise_df = calculate_pairwise_win_rates(results, ai_names)
        overall_df = calculate_overall_performance(results, ai_names)
        error_df = analyze_errors(results)

        if pairwise_df is not None:
            print("\n--- Pairwise Win Rate (%) [Row AI (P1) vs Col AI (P2)] ---")
            print(pairwise_df.round(1))
            
            print("\n--- Overall AI Performance ---")
            print(overall_df)
            
            if error_df is not None and not error_df.empty:
                print("\n--- Error Analysis ---")
                print(error_df)
            
            print("\nGenerating visualizations...")
            fig1 = plot_heatmap(pairwise_df, args.games)
            fig2 = plot_overall_performance(overall_df)
            
            if args.save:
                save_results(pairwise_df, overall_df, error_df)
            
            print("Plots generated (close windows to exit).")
            plt.show()
        else:
            print("Analysis failed, no data generated.")
    else:
        print("Benchmark produced no results.")

    print("\nBenchmark complete.")