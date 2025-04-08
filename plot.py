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

from board import ConnectFourBoard

AI_FOLDER = "./ai"
NUM_GAMES_PER_PAIRING = 5
MOVE_TIMEOUT_SECONDS = 5.0


def load_ais(folder_path):
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
    game_board = ConnectFourBoard()
    ais = {1: ai1_info, 2: ai2_info}
    current_player = 1
    error_info = None

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
                break

            if not game_board.is_valid_location(col):
                game_board.game_over = True
                game_board.winner = 3 - current_player
                error_info = {'type': 'Invalid Move'}
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
            break

    winner_player = game_board.winner
    # 1, 2, or 3 (Draw)
    final_winner = winner_player if winner_player is not None else 3

    return {
        'winner': final_winner,
        'ai1_name': ai1_info['name'],
        'ai2_name': ai2_info['name'],
        # Indicate if game ended due to an error by P1 or P2
        'error': bool(error_info)
    }


def run_benchmark(ais, num_games_per_pairing, timeout):
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


def plot_heatmap(pairwise_df, num_games_per_pairing):
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
    plt.show()


if __name__ == "__main__":
    print("=" * 50)
    print(" Connect-4 AI Benchmark (Pairwise Heatmap only, more to be added >:) )")
    print("=" * 50)

    loaded_ais = load_ais(AI_FOLDER)

    if not loaded_ais or len(loaded_ais) < 2:
        print("\nBenchmark requires at least two valid AIs.")
        sys.exit(1)

    ai_names_list = [ai['name'] for ai in loaded_ais]
    print(f"\nFound {len(loaded_ais)} AIs: {', '.join(ai_names_list)}")

    benchmark_results = run_benchmark(
        loaded_ais, NUM_GAMES_PER_PAIRING, MOVE_TIMEOUT_SECONDS)

    if benchmark_results:
        print("\nCalculating pairwise win rates...")
        pairwise_win_df = calculate_pairwise_win_rates(
            benchmark_results, ai_names_list)

        if pairwise_win_df is not None:
            # TODO: Add a logging global variable ? :/

            # Some more logging
            print(
                "\n--- Pairwise Win Rate (%) [Row AI (P1) vs Col AI (P2)] ---")
            print(pairwise_win_df.round(1))
            print("\nGenerating heatmap plot...")
            plot_heatmap(pairwise_win_df, NUM_GAMES_PER_PAIRING)
            print("Plot generated (close plot window to exit script).")
        else:
            print("Analysis failed, no pairwise data generated.")
    else:
        print("Benchmark run failed or produced no results.")

    print("\nBenchmark script finished.")
