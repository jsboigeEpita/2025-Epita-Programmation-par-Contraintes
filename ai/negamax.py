import numpy as np
import random
import math
from board import ConnectFourBoard

ROW_COUNT = 6
COLUMN_COUNT = 7
WINDOW_LENGTH = 4
EMPTY = 0

def evaluate_window(window, piece):
    score = 0
    opponent_piece = 3 - piece
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opponent_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score

def score_position(board_state, piece):
    score = 0
    # Score center column
    center_array = [int(i) for i in list(board_state[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    # Score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board_state[r, :])]
        for c in range(COLUMN_COUNT - WINDOW_LENGTH + 1):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    # Score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board_state[:, c])]
        for r in range(ROW_COUNT - WINDOW_LENGTH + 1):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    # Score positive diagonal
    for r in range(ROW_COUNT - WINDOW_LENGTH + 1):
        for c in range(COLUMN_COUNT - WINDOW_LENGTH + 1):
            window = [board_state[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    # Score negative diagonal
    for r in range(WINDOW_LENGTH - 1, ROW_COUNT):
        for c in range(COLUMN_COUNT - WINDOW_LENGTH + 1):
            window = [board_state[r - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    return score

def negamax(board, depth, alpha, beta, player_piece, ai_original_piece):
    opponent_piece = 3 - player_piece
    valid_locations = board.get_valid_locations()
    is_terminal = board.game_over or len(valid_locations) == 0

    if depth == 0 or is_terminal:
        if is_terminal:
            winner = board.winner
            if winner == ai_original_piece:
                return (1000000 + depth * 100, None)
            elif winner == (3 - ai_original_piece):
                return (-1000000 - depth * 100, None)
            else: # Draw
                return (0, None)
        else: # Depth is zero
            return (score_position(board.get_board(), ai_original_piece), None)

    max_eval = -math.inf
    best_col = random.choice(valid_locations) if valid_locations else None

    for col in valid_locations:
        temp_board = ConnectFourBoard()
        temp_board.board = np.copy(board.get_board())
        if not temp_board.drop_piece(col, player_piece):
            continue

        # Recursive call, negating score and swapping/negating alpha beta
        eval_score, _ = negamax(temp_board, depth - 1, -beta, -alpha, opponent_piece, ai_original_piece)
        eval_score = -eval_score

        if eval_score > max_eval:
            max_eval = eval_score
            best_col = col

        alpha = max(alpha, eval_score)
        if alpha >= beta:
            break # Prune

    return max_eval, best_col

def get_move(board, piece, depth=4):
    state = ConnectFourBoard()
    state.board = np.copy(board)
    _, col = negamax(state, depth, -math.inf, math.inf, piece, piece)

    # Fallback if negamax returns None unexpectedly
    if col is None:
         valid_locations = state.get_valid_locations()
         return random.choice(valid_locations) if valid_locations else None

    return col

def name():
    """Returns the name of this AI algorithm."""
    return "Negamax AI"
