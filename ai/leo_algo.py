import numpy as np
from board import ConnectFourBoard
import random

# --- Expert System Logic ---

# Constants
AI_PIECE = 2
PLAYER_PIECE = 1
EMPTY_SLOT = 0
ROW_COUNT = 6
COLUMN_COUNT = 7

# --- Board Analysis Functions ---

def _get_game_phase(board_obj):
    """
    Determines the current game phase based on the number of pieces.
    
    Returns: 'opening', 'midgame', or 'endgame'
    """
    piece_count = np.count_nonzero(board_obj.board)
    total_slots = ROW_COUNT * COLUMN_COUNT
    
    if piece_count < total_slots * 0.3:  # Less than 30% filled
        return 'opening'
    elif piece_count < total_slots * 0.7:  # Between 30% and 70% filled
        return 'midgame'
    else:  # More than 70% filled
        return 'endgame'

def _detect_horizontal_trap(board_obj, piece):
    """
    Detects horizontal traps like "XX_X" or "X_XX" where placing in the gap creates a win.
    Returns the column to play or None.
    """
    board_array = board_obj.board
    
    # Check for horizontal traps
    for row in range(ROW_COUNT):
        for col in range(COLUMN_COUNT - 3):
            # Check patterns like "X_XX" and "XX_X"
            window = [board_array[row][col+i] for i in range(4)]
            
            # If there's exactly one empty space and three of our pieces
            if window.count(piece) == 3 and window.count(EMPTY_SLOT) == 1:
                # Find the empty slot position
                empty_pos = col + window.index(EMPTY_SLOT)
                # Check if we can actually play there (column not full)
                if board_obj.is_valid_location(empty_pos) and board_obj.get_next_open_row(empty_pos) == row:
                    return empty_pos
    
    return None

def _detect_vertical_trap(board_obj, piece):
    """
    Detects vertical trap opportunities where placing a piece would create 3 in a column
    with an open spot above for a win next turn.
    
    Fixed to properly detect both completed and near-complete vertical alignments.
    """
    board_array = board_obj.board
    
    # Modified to check bottom-up vertical sequences
    for col in range(COLUMN_COUNT):
        # Count consecutive pieces in this column
        consecutive_count = 0
        for row in range(ROW_COUNT-1, -1, -1):  # Start from bottom
            if board_array[row][col] == piece:
                consecutive_count += 1
            else:
                break
                
        # If we found 3 consecutive pieces and there's room above
        if consecutive_count == 3:
            top_row = ROW_COUNT - consecutive_count - 1
            if top_row >= 0 and board_array[top_row][col] == EMPTY_SLOT:
                # Check if we can place here
                if board_obj.is_valid_location(col) and board_obj.get_next_open_row(col) == top_row:
                    return col
    
    # Also check for potential vertical traps (2 pieces with room for 2 more)
    for col in range(COLUMN_COUNT):
        for row in range(ROW_COUNT - 2):  # Only need to check up to 3rd row from bottom
            # Check for pattern: piece, piece, empty, empty from bottom up
            if (row + 3 < ROW_COUNT and
                board_array[row+2][col] == piece and
                board_array[row+3][col] == piece and
                board_array[row+1][col] == EMPTY_SLOT and
                board_array[row][col] == EMPTY_SLOT):
                # The trap only works if we can play in this position
                if board_obj.is_valid_location(col) and board_obj.get_next_open_row(col) == row+1:
                    return col
    
    return None

def _detect_diagonal_trap(board_obj, piece):
    """
    Detects diagonal trap setups that could lead to forced wins.
    Enhanced to detect more diagonal threat patterns.
    """
    board_array = board_obj.board
    
    # Check for diagonal patterns in both directions
    # Positive diagonal (/)
    for row in range(ROW_COUNT - 3):
        for col in range(COLUMN_COUNT - 3):
            window = [board_array[row+i][col+i] for i in range(4)]
            if window.count(piece) == 3 and window.count(EMPTY_SLOT) == 1:
                empty_idx = window.index(EMPTY_SLOT)
                empty_row, empty_col = row + empty_idx, col + empty_idx
                if (board_obj.is_valid_location(empty_col) and 
                    board_obj.get_next_open_row(empty_col) == empty_row):
                    return empty_col
    
    # Negative diagonal (\)
    for row in range(3, ROW_COUNT):
        for col in range(COLUMN_COUNT - 3):
            window = [board_array[row-i][col+i] for i in range(4)]
            if window.count(piece) == 3 and window.count(EMPTY_SLOT) == 1:
                empty_idx = window.index(EMPTY_SLOT)
                empty_row, empty_col = row - empty_idx, col + empty_idx
                if (board_obj.is_valid_location(empty_col) and 
                    board_obj.get_next_open_row(empty_col) == empty_row):
                    return empty_col
    
    # Additional check for stacked diagonals (detect 'developing' threats)
    # For positive diagonal (/)
    for row in range(1, ROW_COUNT - 2):  # Start from row 1 to ensure space below
        for col in range(1, COLUMN_COUNT - 2):  # Start from col 1 to ensure space before
            # Check if we have 2 pieces in a diagonal with playable spots at both ends
            if (board_array[row][col] == piece and
                board_array[row+1][col+1] == piece and
                board_array[row+2][col+2] == EMPTY_SLOT and
                board_array[row-1][col-1] == EMPTY_SLOT):
                # Check if we can actually play at one of the empty positions
                if (board_obj.is_valid_location(col+2) and 
                    board_obj.get_next_open_row(col+2) == row+2):
                    return col+2
                if (board_obj.is_valid_location(col-1) and
                    board_obj.get_next_open_row(col-1) == row-1):
                    return col-1
    
    # For negative diagonal (\)
    for row in range(2, ROW_COUNT - 1):  # Ensure space above and below
        for col in range(1, COLUMN_COUNT - 2):  # Start from col 1 to ensure space before
            # Check if we have 2 pieces in a diagonal with playable spots at both ends
            if (board_array[row][col] == piece and
                board_array[row-1][col+1] == piece and
                board_array[row-2][col+2] == EMPTY_SLOT and
                board_array[row+1][col-1] == EMPTY_SLOT):
                # Check if we can actually play at one of the empty positions
                if (board_obj.is_valid_location(col+2) and 
                    board_obj.get_next_open_row(col+2) == row-2):
                    return col+2
                if (board_obj.is_valid_location(col-1) and
                    board_obj.get_next_open_row(col-1) == row+1):
                    return col-1
    
    return None

def _detect_developing_trap(board_obj, piece):
    """
    Detects developing traps where a player has two consecutive pieces
    with spaces on both sides, which could develop into a dangerous
    three-in-a-row with open ends.
    
    Returns the column to play to block this developing threat, or None.
    """
    board_array = board_obj.board
    
    # Check for horizontal developing traps (XX00)
    for row in range(ROW_COUNT):
        for col in range(COLUMN_COUNT - 3):
            # Check for pattern "XX00" or "00XX"
            # First check "XX00"
            if (col + 3 < COLUMN_COUNT and
                board_array[row][col] == piece and
                board_array[row][col+1] == piece and
                board_array[row][col+2] == EMPTY_SLOT and
                board_array[row][col+3] == EMPTY_SLOT):
                
                # Check if we can play at the third position
                if (row == ROW_COUNT - 1 or 
                    (row + 1 < ROW_COUNT and board_array[row+1][col+2] != EMPTY_SLOT)):
                    if board_obj.is_valid_location(col+2):
                        return col+2
            
            # Then check "00XX"
            if (col + 3 < COLUMN_COUNT and
                board_array[row][col] == EMPTY_SLOT and
                board_array[row][col+1] == EMPTY_SLOT and 
                board_array[row][col+2] == piece and
                board_array[row][col+3] == piece):
                
                # Check if we can play at the second position
                if (row == ROW_COUNT - 1 or 
                    (row + 1 < ROW_COUNT and board_array[row+1][col+1] != EMPTY_SLOT)):
                    if board_obj.is_valid_location(col+1):
                        return col+1
    
    # Check for "X0X0" and "0X0X" patterns
    for row in range(ROW_COUNT):
        for col in range(COLUMN_COUNT - 3):
            # Check for "X0X0"
            if (board_array[row][col] == piece and
                board_array[row][col+1] == EMPTY_SLOT and
                board_array[row][col+2] == piece and
                board_array[row][col+3] == EMPTY_SLOT):
                
                # Check if we can play at the second position
                if (row == ROW_COUNT - 1 or 
                    (row + 1 < ROW_COUNT and board_array[row+1][col+1] != EMPTY_SLOT)):
                    if board_obj.is_valid_location(col+1):
                        return col+1
            
            # Check for "0X0X"
            if (board_array[row][col] == EMPTY_SLOT and
                board_array[row][col+1] == piece and
                board_array[row][col+2] == EMPTY_SLOT and
                board_array[row][col+3] == piece):
                
                # Check if we can play at the third position
                if (row == ROW_COUNT - 1 or 
                    (row + 1 < ROW_COUNT and board_array[row+1][col+2] != EMPTY_SLOT)):
                    if board_obj.is_valid_location(col+2):
                        return col+2
    
    # Most critical case: bottom row check for "0XX0" pattern
    bottom_row = ROW_COUNT - 1
    for col in range(1, COLUMN_COUNT - 2):
        if (board_array[bottom_row][col] == piece and
            board_array[bottom_row][col+1] == piece and
            board_array[bottom_row][col-1] == EMPTY_SLOT and
            board_array[bottom_row][col+2] == EMPTY_SLOT):
            
            # We should block one of the ends immediately
            if board_obj.is_valid_location(col-1):
                return col-1
            if board_obj.is_valid_location(col+2):
                return col+2
    
    return None

def _detect_open_ended_three_in_a_row(board_obj, piece):
    """
    Detects open-ended three-in-a-row patterns like "0XXX0" where both ends are open,
    creating a double threat that's impossible to block in one move.
    
    Returns the column to play to block one end (if blocking needed),
    or to create the threat (if for our piece), or None.
    """
    board_array = board_obj.board
    
    # Check for horizontal open-ended three-in-a-row
    for row in range(ROW_COUNT):
        for col in range(1, COLUMN_COUNT - 3):  # Need space on both sides
            # Check if there's a sequence of 3 pieces with empty spaces on both ends
            if (col-1 >= 0 and col+3 < COLUMN_COUNT and
                board_array[row][col] == piece and
                board_array[row][col+1] == piece and
                board_array[row][col+2] == piece and
                board_array[row][col-1] == EMPTY_SLOT and
                board_array[row][col+3] == EMPTY_SLOT):
                
                # Check if we can play at either open end
                if (row == ROW_COUNT - 1 or board_array[row + 1][col - 1] != EMPTY_SLOT):
                    if board_obj.is_valid_location(col - 1):
                        return col - 1  # Block/create on left side
                
                if (row == ROW_COUNT - 1 or board_array[row + 1][col + 3] != EMPTY_SLOT):
                    if board_obj.is_valid_location(col + 3):
                        return col + 3  # Block/create on right side
    
    return None

def _detect_trap_threat(board_obj, piece):
    """
    Detects if a player can create a winning trap in one move.
    Returns the column to play to block/create the trap, or None.
    
    Enhanced to prioritize certain threat types.
    """
    # Check horizontal, vertical, and diagonal traps
    traps = []
    
    # Check for open-ended three-in-a-row (highest priority - impossible to block both sides)
    open_trap = _detect_open_ended_three_in_a_row(board_obj, piece)
    if open_trap is not None:
        traps.append((open_trap, 4))  # Even higher priority
    
    # Check vertical trap
    v_trap = _detect_vertical_trap(board_obj, piece)
    if v_trap is not None:
        traps.append((v_trap, 3))
        
    # Check horizontal trap (single gap)
    h_trap = _detect_horizontal_trap(board_obj, piece)
    if h_trap is not None:
        traps.append((h_trap, 2))
        
    # Check diagonal trap
    d_trap = _detect_diagonal_trap(board_obj, piece)
    if d_trap is not None:
        traps.append((d_trap, 1))
    
    # Check developing trap
    developing_trap = _detect_developing_trap(board_obj, piece)
    if developing_trap is not None:
        traps.append((developing_trap, 0))
    
    # Verify which traps actually create a winning position
    verified_traps = []
    for col, priority in traps:
        temp_board = ConnectFourBoard()
        temp_board.board = board_obj.get_board()
        row = temp_board.get_next_open_row(col)
        if row != -1:
            temp_board.board[row][col] = piece
            # For open-ended three-in-a-row, it's already verified
            if priority == 4 or temp_board.is_winning_move(piece):
                # Store with priority
                verified_traps.append((col, priority))
    
    # Sort by priority and return the highest priority trap
    if verified_traps:
        verified_traps.sort(key=lambda x: x[1], reverse=True)
        return verified_traps[0][0]
    return None

def _detect_double_threat(board_obj, col, piece):
    """
    Checks if placing piece in column creates a double threat (two ways to win).
    Returns True if the move creates a double threat.
    """
    # Create temporary board with the move
    temp_board = ConnectFourBoard()
    temp_board.board = board_obj.get_board()
    row = temp_board.get_next_open_row(col)
    if row == -1:
        return False
        
    # Make the move
    temp_board.drop_piece(col, piece)
    
    # Check for potential winning moves after this move
    winning_columns = []
    for next_col in range(COLUMN_COUNT):
        if temp_board.is_valid_location(next_col):
            next_row = temp_board.get_next_open_row(next_col)
            temp_board.board[next_row][next_col] = piece  # Try the move
            if temp_board.is_winning_move(piece):
                winning_columns.append(next_col)
            temp_board.board[next_row][next_col] = EMPTY_SLOT  # Undo
    
    # Two or more winning options means a double threat
    return len(winning_columns) >= 2

def _avoids_setting_up_opponent(board_obj, col, piece):
    """
    Checks if playing in a column avoids setting up the opponent 
    for a win above our piece.
    """
    opponent = 3 - piece
    temp_board = ConnectFourBoard()
    temp_board.board = board_obj.get_board()
    
    # Place our piece
    row = temp_board.get_next_open_row(col)
    if row == -1:
        return True  # Column is full, shouldn't happen but return True
        
    temp_board.drop_piece(col, piece)
    
    # Check if placing opponent's piece above would create a win
    if row > 0:  # If not at top row
        temp_board.board[row-1][col] = opponent
        if temp_board.is_winning_move(opponent):
            return False
    
    return True

def _creates_alignment(board_obj, col, piece, min_count=2):
    """
    Checks if playing in column creates an alignment of at least min_count pieces.
    """
    temp_board = ConnectFourBoard()
    temp_board.board = board_obj.get_board()
    row = temp_board.get_next_open_row(col)
    if row == -1:
        return False
    
    # Place the piece
    temp_board.board[row][col] = piece
    
    # Check horizontal
    count = 0
    for c in range(max(0, col-3), min(COLUMN_COUNT, col+4)):
        if c < 0 or c >= COLUMN_COUNT:
            continue
        if temp_board.board[row][c] == piece:
            count += 1
            if count >= min_count:
                return True
        else:
            count = 0
    
    # Check vertical
    count = 0
    for r in range(max(0, row-3), min(ROW_COUNT, row+4)):
        if r < 0 or r >= ROW_COUNT:
            continue
        if temp_board.board[r][col] == piece:
            count += 1
            if count >= min_count:
                return True
        else:
            count = 0
            
    # Check diagonal /
    count = 0
    for i in range(-3, 4):
        r, c = row-i, col+i
        if r < 0 or r >= ROW_COUNT or c < 0 or c >= COLUMN_COUNT:
            continue
        if temp_board.board[r][c] == piece:
            count += 1
            if count >= min_count:
                return True
        else:
            count = 0
            
    # Check diagonal \
    count = 0
    for i in range(-3, 4):
        r, c = row+i, col+i
        if r < 0 or r >= ROW_COUNT or c < 0 or c >= COLUMN_COUNT:
            continue
        if temp_board.board[r][c] == piece:
            count += 1
            if count >= min_count:
                return True
        else:
            count = 0
            
    return False

# --- Helper Functions for Rule Evaluation ---

def _check_immediate_win(board_obj, piece):
    """
    Checks if placing a piece in any valid column results in an immediate win.

    Parameters:
    - board_obj: An instance of ConnectFourBoard
    - piece: The piece to check for (1 or 2)

    Returns:
    - col: The column number for the winning move, or None if no immediate win exists.
    """
    valid_locations = board_obj.get_valid_locations()
    for col in valid_locations:
        # Simulate placing the piece
        row = board_obj.get_next_open_row(col)
        # Important: Use a copy to avoid modifying the original board state during check
        temp_board = ConnectFourBoard()
        temp_board.board = board_obj.get_board() # Get a copy
        temp_board.board[row][col] = piece # Simulate the move

        # Check if this simulated move is a win
        if temp_board.is_winning_move(piece):
            return col # Found a winning move
    return None # No immediate winning move found

def _is_move_safe(board_obj, col, piece):
    """
    Enhanced version that checks if a move is safe from immediate and near-future threats.
    
    Returns:
    - True if the move is safe, False otherwise.
    """
    opponent_piece = 3 - piece
    temp_board = ConnectFourBoard()
    temp_board.board = board_obj.get_board()
    row = temp_board.get_next_open_row(col)
    
    if row == -1:
        return False
    
    # Make the move
    temp_board.drop_piece(col, piece)
    
    # 1. Check for immediate winning response by opponent
    opponent_win = _check_immediate_win(temp_board, opponent_piece)
    if opponent_win is not None:
        return False
    
    # 2. Check for setting up a vertical win for opponent (if we're not at top)
    if row > 0:
        temp_board_future = ConnectFourBoard()
        temp_board_future.board = temp_board.get_board()
        temp_board_future.board[row-1][col] = opponent_piece
        if temp_board_future.is_winning_move(opponent_piece):
            return False
    
    return True


def _get_preferred_move_order(board_obj):
    """
    Returns a list of columns ordered by preference (center first).

    Parameters:
    - board_obj: An instance of ConnectFourBoard.

    Returns:
    - List of column indices, ordered from most to least preferred.
    """
    center_col = COLUMN_COUNT // 2
    preferred_order = [center_col]
    # Add columns spreading outwards from the center
    for offset in range(1, COLUMN_COUNT // 2 + 1):
        if center_col + offset < COLUMN_COUNT:
            preferred_order.append(center_col + offset)
        if center_col - offset >= 0:
            preferred_order.append(center_col - offset)
    return preferred_order

# --- Enhanced Main Expert System Logic ---

def find_best_move(board_obj, piece):
    """
    Determines the best move based on an extensive set of prioritized rules.
    This is the core of the expert system.
    """
    opponent_piece = 3 - piece
    valid_locations = board_obj.get_valid_locations()
    
    if not valid_locations:
        return None
    
    # Get current game phase to adjust strategy
    game_phase = _get_game_phase(board_obj)
    
    # --- Rule 1: Win if possible (highest priority) ---
    winning_move = _check_immediate_win(board_obj, piece)
    if winning_move is not None:
        return winning_move
    
    # --- Rule 2: Block opponent's immediate win ---
    blocking_move = _check_immediate_win(board_obj, opponent_piece)
    if blocking_move is not None:
        return blocking_move
    
    # --- Rule 2.5: Block opponent's developing traps ---
    # This detects scenarios that could lead to unblockable threats
    developing_trap = _detect_developing_trap(board_obj, opponent_piece)
    if developing_trap is not None:
        return developing_trap
    
    # --- Rule 2.6: Block opponent's open-ended three in a row ---
    # This is a special case that needs immediate attention
    open_trap_block = _detect_open_ended_three_in_a_row(board_obj, opponent_piece)
    if open_trap_block is not None:
        return open_trap_block
      
    # --- Rule 3: Block opponent's traps ---
    # Use the improved trap detection function
    opponent_trap = _detect_trap_threat(board_obj, opponent_piece)
    if opponent_trap is not None:
        return opponent_trap
    
    # --- Rule 4: Create a double threat (forced win) if possible ---
    # First create developing threats for ourselves
    our_developing_trap = _detect_developing_trap(board_obj, piece)
    if our_developing_trap is not None:
        return our_developing_trap
    
    # Then check for open-ended three in a row for ourselves
    our_open_trap = _detect_open_ended_three_in_a_row(board_obj, piece)
    if our_open_trap is not None:
        return our_open_trap
        
    # Then check for double threats
    for col in valid_locations:
        if _detect_double_threat(board_obj, col, piece):
            return col
    
    # --- Rule 5: Create our own traps ---
    our_trap = _detect_trap_threat(board_obj, piece)
    if our_trap is not None:
        return our_trap
  
    # --- Rule 6: Find safe moves that create alignments ---
    safe_moves = []
    good_moves = []
    for col in valid_locations:
        if _is_move_safe(board_obj, col, piece):
            safe_moves.append(col)
            
            # Among safe moves, prefer those that create alignments
            if _creates_alignment(board_obj, col, piece, min_count=2):
                good_moves.append(col)
    
    # --- Rule 7: Apply phase-specific strategy ---
    preferred_order = _get_preferred_move_order(board_obj)
    
    # In opening phase, prioritize center and avoid setting up opponent
    if game_phase == 'opening':
        for col in preferred_order:
            if col in safe_moves and _avoids_setting_up_opponent(board_obj, col, piece):
                return col
    
    # In midgame, prioritize moves that create alignments
    if game_phase == 'midgame':
        if good_moves:
            for col in preferred_order:
                if col in good_moves:
                    return col
            return random.choice(good_moves)
    
    # In endgame, be more aggressive with creating alignments
    if game_phase == 'endgame':
        if good_moves:
            return random.choice(good_moves)
    
    # --- Rule 8: Fall back to safe moves with center preference ---
    if safe_moves:
        for col in preferred_order:
            if col in safe_moves:
                return col
        return random.choice(safe_moves)
    
    # --- Rule 9: If no safe moves, choose any valid move (prefer center) ---
    for col in preferred_order:
        if col in valid_locations:
            return col
            
    return random.choice(valid_locations)

# --- Required Public Interface Functions ---

def get_move(board_state, piece):
    """
    Public interface function to get the AI's move.
    Creates a ConnectFourBoard object and uses the expert system.
    """
    board_obj = ConnectFourBoard()
    board_obj.board = board_state.copy()
    
    best_move = find_best_move(board_obj, piece)
    return best_move
  
def name():
    """Returns the name of this AI algorithm"""
    return "Leo algo"