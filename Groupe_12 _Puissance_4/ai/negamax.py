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

def negamax_alpha_beta(board, depth, alpha, beta, color, ai_piece):
    valid_locations = board.get_valid_locations()
    is_terminal = board.game_over or len(valid_locations) == 0
    current_piece = ai_piece if color == 1 else 3 - ai_piece
    
    # Terminal node check
    if depth == 0 or is_terminal:
        if is_terminal:
            if board.winner == ai_piece:
                return (1000000 * color, None)  # AI wins
            elif board.winner == (3 - ai_piece):
                return (-1000000 * color, None)  # Opponent wins
            else:  # Draw
                return (0, None)
        else:  # Depth is zero - evaluate from current position
            return (color * score_position(board.get_board(), ai_piece), None)
    
    value = -math.inf
    best_col = random.choice(valid_locations) if valid_locations else None
    
    for col in valid_locations:
        temp_board = ConnectFourBoard()
        temp_board.board = np.copy(board.get_board())
        row = temp_board.drop_piece(col, current_piece)
        
        if row == -1:  # Invalid move
            continue
            
        # Recursively evaluate with color negation
        new_score, _ = negamax_alpha_beta(temp_board, depth - 1, -beta, -alpha, -color, ai_piece)
        new_score = -new_score
        
        # Update best value and move
        if new_score > value:
            value = new_score
            best_col = col
            
        # Update alpha
        alpha = max(alpha, value)
        if alpha >= beta:
            break  # Beta cutoff
            
    return value, best_col

def get_move(board, piece, depth=6):
    state = ConnectFourBoard()
    state.board = np.copy(board)
    
    # Start negamax search, with color=1 since AI is making move
    _, col = negamax_alpha_beta(state, depth, -math.inf, math.inf, 1, piece)
    
    # Fallback if negamax returns None unexpectedly
    if col is None:
        valid_locations = state.get_valid_locations()
        return random.choice(valid_locations) if valid_locations else None
    
    return col

def name():
    """Returns the name of this AI algorithm."""
    return "Negamax"
