import numpy as np
import random
from board import ConnectFourBoard # Assuming board.py is in the same directory
import math # For infinity

# --- Genetic Algorithm Configuration (Represents the *Result* of Training) ---

# These weights would ideally be determined through an offline GA training process.
# They represent the "best chromosome" found.
# The features are just examples; a real GA might use more/different ones.
# Weights: [Own_3_in_row, Own_2_in_row, Opponent_3_in_row, Opponent_2_in_row, Center_Control]
# Note: A 4-in-a-row is treated as an immediate win/loss (infinite score).
# Positive weights are good for AI, negative weights are bad (opponent benefit).
# We negate opponent scores when adding to the total.
BEST_WEIGHTS = np.array([
    100,     # Score for having 3 of AI's pieces in a row (with one empty)
    5,       # Score for having 2 of AI's pieces in a row (with two empties)
    -80,     # Score for opponent having 3 pieces in a row (negative because it's bad for AI) - Block this!
    -10,     # Score for opponent having 2 pieces in a row
    3        # Small bonus for each piece in the center column
])

# Constants for pieces
AI_PIECE = 2
PLAYER_PIECE = 1
EMPTY_SLOT = 0

# --- Evaluation Function ---

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

    # --- Score Windows ---
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

# --- Helper to Check for Immediate Win/Loss ---
# (Similar to expert system, useful for pruning)
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

# --- Helper to Check if Move Sets Up Opponent Win ---
def _is_move_dangerous(board_obj, col, piece):
    """Checks if making move 'col' allows opponent to win next turn."""
    opponent_piece = 3 - piece
    # Simulate our move
    temp_board = ConnectFourBoard()
    temp_board.board = board_obj.get_board()
    row = temp_board.get_next_open_row(col)
    if row == -1: return False # Should not happen for valid col
    temp_board.drop_piece(col, piece) # Make the move

    # Check if game ended (then it's not dangerous in this sense)
    if temp_board.game_over:
        return False

    # Check if opponent has a winning move *now*
    opponent_winning_move = _check_immediate_win_ga(temp_board, opponent_piece)
    return opponent_winning_move is not None

# --- Required Public Interface Functions ---

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
        # print(f"GA AI: Found immediate win in column {winning_move}") # Debug
        return winning_move

    # --- Rule 2: Block opponent's win ---
    blocking_move = _check_immediate_win_ga(board_obj, opponent_piece)
    if blocking_move is not None:
        # print(f"GA AI: Found blocking move in column {blocking_move}") # Debug
        return blocking_move

    # --- Rule 3: Evaluate moves using the GA weights ---
    best_score = -float('inf')
    best_col = random.choice(valid_locations) # Start with a random valid move

    scored_moves = {} # Store scores for debugging/analysis

    for col in valid_locations:
        # Check if this move allows the opponent to win immediately next turn
        if _is_move_dangerous(board_obj, col, piece):
             # print(f"GA AI: Move {col} is dangerous, assigning very low score.") # Debug
             # Assign a very low score, but slightly different per column
             # to ensure a move is still picked if all are dangerous.
             move_score = -1e9 - col # Avoid this move unless absolutely necessary
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

    # print(f"GA AI: Move scores: {scored_moves}") # Debug
    # print(f"GA AI: Chose column {best_col} with score {best_score}") # Debug
    return best_col

def name():
    """
    Returns the name of this AI algorithm.
    """
    return "Genetic"