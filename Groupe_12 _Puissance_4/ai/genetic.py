import numpy as np
import random
from board import ConnectFourBoard

BEST_WEIGHTS = np.array([
    100,     
    5,       
    -80,     
    -10,     
    3       
])

AI_PIECE = 2
PLAYER_PIECE = 1
EMPTY_SLOT = 0


def evaluate_window(window, piece, weights):
    """Calculates the score for a 4-slot window."""
    score = 0
    opponent_piece = 3 - piece # Determine opponent's piece (1 vs 2)

    own_count = np.count_nonzero(window == piece)
    opp_count = np.count_nonzero(window == opponent_piece)
    empty_count = np.count_nonzero(window == EMPTY_SLOT)

    if own_count == 4:
        return float('inf') # Immediate win
    elif own_count == 3 and empty_count == 1:
        score += weights[0] # Own_3_in_row
    elif own_count == 2 and empty_count == 2:
        score += weights[1] # Own_2_in_row

    if opp_count == 4:
        return float('-inf') # Opponent would win (should be blocked)
    elif opp_count == 3 and empty_count == 1:
        score += weights[2] # Opponent_3_in_row (negative weight is bad for us)
    elif opp_count == 2 and empty_count == 2:
        score += weights[3] # Opponent_2_in_row (negative weight is bad for us)

    return score

def score_board_state(board_array, piece, weights):
    """
    Evaluates the entire board based on the weights (chromosome).
    Higher score is better for the specified 'piece'.
    """
    score = 0
    rows, cols = board_array.shape

    # Horizontal
    for r in range(rows):
        for c in range(cols - 3):
            window = board_array[r, c:c+4]
            score += evaluate_window(window, piece, weights)

    # Vertical
    for c in range(cols):
        for r in range(rows - 3):
            window = board_array[r:r+4, c]
            score += evaluate_window(window, piece, weights)

    # Positive Diagonal
    for r in range(rows - 3):
        for c in range(cols - 3):
            window = np.array([board_array[r+i][c+i] for i in range(4)])
            score += evaluate_window(window, piece, weights)

    # Negative Diagonal
    for r in range(3, rows):
        for c in range(cols - 3):
            window = np.array([board_array[r-i][c+i] for i in range(4)])
            score += evaluate_window(window, piece, weights)

    # --- Score Center Control ---
    center_col_index = cols // 2
    center_column = board_array[:, center_col_index]
    center_count = np.count_nonzero(center_column == piece)
    score += center_count * weights[4] # Center_Control weight

    return score


def _check_immediate_win_ga(board_obj, piece):
    """Checks if a piece can win immediately."""
    valid_locations = board_obj.get_valid_locations()
    for col in valid_locations:
        row = board_obj.get_next_open_row(col)
        temp_board = ConnectFourBoard()
        temp_board.board = board_obj.get_board()
        temp_board.board[row][col] = piece
        if temp_board.is_winning_move(piece):
            return col
    return None

def _is_move_dangerous(board_obj, col, piece):
    """Checks if making move 'col' allows opponent to win next turn."""
    opponent_piece = 3 - piece
    # Simulate our move
    temp_board = ConnectFourBoard()
    temp_board.board = board_obj.get_board()
    row = temp_board.get_next_open_row(col)
    if row == -1: return False 
    temp_board.drop_piece(col, piece)

    # Check if game ended
    if temp_board.game_over:
        return False

    # Check if opponent has a winning move 
    opponent_winning_move = _check_immediate_win_ga(temp_board, opponent_piece)
    return opponent_winning_move is not None


def get_move(board_state, piece):
    """
    Public interface function to get the AI's move using GA-derived evaluation.

    Parameters:
    - board_state: numpy array - The Connect Four board state.
    - piece: int - The AI's piece (usually AI_PIECE = 2).

    Returns:
    - col: int - The column where the AI wants to place its piece, or None if no move possible.
    """
    board_obj = ConnectFourBoard()
    board_obj.board = board_state.copy()
    valid_locations = board_obj.get_valid_locations()
    opponent_piece = 3 - piece

    if not valid_locations:
        return None

    # --- Rule 1: Win if possible ---
    winning_move = _check_immediate_win_ga(board_obj, piece)
    if winning_move is not None:
        return winning_move

    # --- Rule 2: Block opponent's win ---
    blocking_move = _check_immediate_win_ga(board_obj, opponent_piece)
    if blocking_move is not None:
        return blocking_move

    # --- Rule 3: Evaluate moves using the GA weights ---
    best_score = -float('inf')
    best_col = random.choice(valid_locations) # Start with a random valid move

    scored_moves = {} # Store scores for analysis

    for col in valid_locations:
        # Check if this move allows the opponent to win immediately next turn
        if _is_move_dangerous(board_obj, col, piece):
             move_score = -1e9 - col 
        else:
            # Simulate dropping the piece
            row = board_obj.get_next_open_row(col)
            temp_board = board_obj.get_board() # Get a copy
            temp_board[row][col] = piece

            # Evaluate the resulting board state
            move_score = score_board_state(temp_board, piece, BEST_WEIGHTS)

        scored_moves[col] = move_score # Store score

        # Update best move found so far
        if move_score > best_score:
            best_score = move_score
            best_col = col

    return best_col

def name():
    """
    Returns the name of this AI algorithm.
    """
    return "Genetic"