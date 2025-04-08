import numpy as np
import random
import math
from board import ConnectFourBoard

ROW_COUNT = 6
COLUMN_COUNT = 7
WINDOW_LENGTH = 4


# Get the score for a given board state
def score_position(board_state, piece):
    score = 0
    opponent_piece = 3 - piece

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


# Evaluate a 4 tile window and return a score
def evaluate_window(window, piece):
    score = 0
    opponent_piece = 3 - piece

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opponent_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score


def minimax(board, depth, alpha, beta, maximizing_player, ai_piece):
    board_state = board.get_board()
    opponent_piece = 3 - ai_piece
    valid_locations = board.get_valid_locations()

    # Check terminal conditions
    is_terminal = board.game_over or len(valid_locations) == 0

    if depth == 0 or is_terminal:
        if is_terminal:
            if board.winner == ai_piece:
                return (1000000 + depth, None)
            elif board.winner == opponent_piece:
                return (-1000000 - depth, None)
            else:  # Draw
                return (0, None)
        else:  # Depth is zero
            return (score_position(board_state, ai_piece), None)

    # Recursive search
    best_col = random.choice(valid_locations) if valid_locations else None

    if maximizing_player:
        max_eval = -math.inf
        for col in valid_locations:
            # Create a copy to simulate the move
            temp_board = ConnectFourBoard()
            temp_board.board = np.copy(board_state)

            # Make the move
            row = temp_board.drop_piece(col, ai_piece)
            if row == -1:  # Invalid move
                continue

            # Recursive call
            eval_score, _ = minimax(
                temp_board, depth - 1, alpha, beta, False, ai_piece)

            # Update best move
            if eval_score > max_eval:
                max_eval = eval_score
                best_col = col

            # Alpha-Beta pruning
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break

        return max_eval, best_col

    else:  # Minimizing player
        min_eval = math.inf
        for col in valid_locations:
            # Create a copy to simulate the move
            temp_board = ConnectFourBoard()
            temp_board.board = np.copy(board_state)

            # Make the move
            row = temp_board.drop_piece(col, opponent_piece)
            if row == -1:  # Invalid move
                continue

            # Recursive call
            eval_score, _ = minimax(
                temp_board, depth - 1, alpha, beta, True, ai_piece)

            # Update best move
            if eval_score < min_eval:
                min_eval = eval_score
                best_col = col

            # Alpha-Beta pruning
            beta = min(beta, eval_score)
            if beta <= alpha:
                break

        return min_eval, best_col


def get_move(board, piece, depth=4):
    state = ConnectFourBoard()
    state.board = np.copy(board)
    _, col = minimax(state, depth, -math.inf, math.inf, True, piece)
    return col


def name():
    return "Minimax AI"
