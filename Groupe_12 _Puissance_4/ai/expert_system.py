import numpy as np
from board import ConnectFourBoard
import random

# Constants
AI_PIECE = 2
PLAYER_PIECE = 1
EMPTY = 0
ROWS = 6
COLS = 7

def _get_game_phase(board):
    """Returns 'opening', 'midgame', or 'endgame' based on board fullness"""
    piece_count = np.count_nonzero(board.board)
    if piece_count < 12:  # ~30% filled
        return 'opening'
    elif piece_count < 29:  # ~70% filled
        return 'midgame'
    else:
        return 'endgame'

def _detect_horizontal_trap(board, piece):
    """Finds horizontal traps like XX_X or X_XX"""
    for row in range(ROWS):
        for col in range(COLS - 3):
            window = [board.board[row][col+i] for i in range(4)]
            if window.count(piece) == 3 and window.count(EMPTY) == 1:
                empty_pos = col + window.index(EMPTY)
                # Only return if we can actually play at this position
                if board.is_valid_location(empty_pos) and board.get_next_open_row(empty_pos) == row:
                    return empty_pos
    return None

def _detect_vertical_trap(board, piece):
    """Detects vertical traps"""
    board_array = board.board
    
    # Check for 3 consecutive pieces with space above
    for col in range(COLS):
        consecutive_count = 0
        for row in range(ROWS-1, -1, -1):  # Start from bottom
            if board_array[row][col] == piece:
                consecutive_count += 1
            else:
                break
                
        if consecutive_count == 3:
            top_row = ROWS - consecutive_count - 1
            if top_row >= 0 and board_array[top_row][col] == EMPTY:
                if board.get_next_open_row(col) == top_row:
                    return col
    
    # Check for 2 pieces with 2 spaces above (potential trap)
    for col in range(COLS):
        for row in range(ROWS - 2):
            if (row + 3 < ROWS and
                board_array[row+2][col] == piece and
                board_array[row+3][col] == piece and
                board_array[row+1][col] == EMPTY and
                board_array[row][col] == EMPTY):
                if board.get_next_open_row(col) == row+1:
                    return col
    
    return None

def _detect_diagonal_trap(board, piece):
    """Detects diagonal traps in both directions"""
    board_array = board.board
    
    # Positive diagonal (/)
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            window = [board_array[row+i][col+i] for i in range(4)]
            if window.count(piece) == 3 and window.count(EMPTY) == 1:
                empty_idx = window.index(EMPTY)
                empty_row, empty_col = row + empty_idx, col + empty_idx
                if (board.is_valid_location(empty_col) and 
                    board.get_next_open_row(empty_col) == empty_row):
                    return empty_col
    
    # Negative diagonal (\)
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            window = [board_array[row-i][col+i] for i in range(4)]
            if window.count(piece) == 3 and window.count(EMPTY) == 1:
                empty_idx = window.index(EMPTY)
                empty_row, empty_col = row - empty_idx, col + empty_idx
                if (board.is_valid_location(empty_col) and 
                    board.get_next_open_row(empty_col) == empty_row):
                    return empty_col
    
    # Developing diagonal patterns (XX__)
    for row in range(1, ROWS - 2):
        for col in range(1, COLS - 2):
            # Positive diagonal pattern
            if (board_array[row][col] == piece and
                board_array[row+1][col+1] == piece and
                board_array[row+2][col+2] == EMPTY and
                board_array[row-1][col-1] == EMPTY):
                if (board.is_valid_location(col+2) and board.get_next_open_row(col+2) == row+2):
                    return col+2
                if (board.is_valid_location(col-1) and board.get_next_open_row(col-1) == row-1):
                    return col-1
            
            # Negative diagonal pattern
            if row >= 2 and (board_array[row][col] == piece and
                board_array[row-1][col+1] == piece and
                board_array[row-2][col+2] == EMPTY and
                board_array[row+1][col-1] == EMPTY):
                if (board.is_valid_location(col+2) and board.get_next_open_row(col+2) == row-2):
                    return col+2
                if (board.is_valid_location(col-1) and board.get_next_open_row(col-1) == row+1):
                    return col-1
    
    return None

def _detect_developing_trap(board, piece):
    """Detects developing traps that could become dangerous"""
    board_array = board.board
    
    # Critical case: bottom row 0XX0 pattern
    bottom_row = ROWS - 1
    for col in range(1, COLS - 2):
        if (board_array[bottom_row][col] == piece and
            board_array[bottom_row][col+1] == piece and
            board_array[bottom_row][col-1] == EMPTY and
            board_array[bottom_row][col+2] == EMPTY):
            
            if board.is_valid_location(col-1):
                return col-1
            if board.is_valid_location(col+2):
                return col+2
    
    # Check horizontal patterns (XX00, 00XX, X0X0, 0X0X)
    for row in range(ROWS):
        for col in range(COLS - 3):
            # Pattern XX00
            if (board_array[row][col] == piece and
                board_array[row][col+1] == piece and
                board_array[row][col+2] == EMPTY and
                board_array[row][col+3] == EMPTY):
                
                if (row == ROWS - 1 or board_array[row+1][col+2] != EMPTY):
                    if board.is_valid_location(col+2):
                        return col+2
            
            # Pattern 00XX
            if (board_array[row][col] == EMPTY and
                board_array[row][col+1] == EMPTY and 
                board_array[row][col+2] == piece and
                board_array[row][col+3] == piece):
                
                if (row == ROWS - 1 or board_array[row+1][col+1] != EMPTY):
                    if board.is_valid_location(col+1):
                        return col+1
            
            # Pattern X0X0
            if (board_array[row][col] == piece and
                board_array[row][col+1] == EMPTY and
                board_array[row][col+2] == piece and
                board_array[row][col+3] == EMPTY):
                
                if (row == ROWS - 1 or board_array[row+1][col+1] != EMPTY):
                    if board.is_valid_location(col+1):
                        return col+1
            
            # Pattern 0X0X
            if (board_array[row][col] == EMPTY and
                board_array[row][col+1] == piece and
                board_array[row][col+2] == EMPTY and
                board_array[row][col+3] == piece):
                
                if (row == ROWS - 1 or board_array[row+1][col+2] != EMPTY):
                    if board.is_valid_location(col+2):
                        return col+2
    
    return None

def _detect_open_ended_three_in_a_row(board, piece):
    """Detects 0XXX0 pattern that creates a double threat"""
    board_array = board.board
    
    for row in range(ROWS):
        for col in range(1, COLS - 3):
            if (col-1 >= 0 and
                board_array[row][col] == piece and
                board_array[row][col+1] == piece and
                board_array[row][col+2] == piece and
                board_array[row][col-1] == EMPTY and
                board_array[row][col+3] == EMPTY):
                
                # Check if we can play at either open end
                if (row == ROWS - 1 or board_array[row+1][col-1] != EMPTY):
                    if board.is_valid_location(col-1):
                        return col-1
                
                if (row == ROWS - 1 or board_array[row+1][col+3] != EMPTY):
                    if board.is_valid_location(col+3):
                        return col+3
    
    return None

def _detect_trap_threat(board, piece):
    """Consolidates trap detection and prioritizes threats"""
    # Collect all potential traps with priorities
    traps = []
    
    # Check traps in order of priority
    open_trap = _detect_open_ended_three_in_a_row(board, piece)
    if open_trap is not None:
        traps.append((open_trap, 4))  # Highest priority
    
    v_trap = _detect_vertical_trap(board, piece)
    if v_trap is not None:
        traps.append((v_trap, 3))
        
    h_trap = _detect_horizontal_trap(board, piece)
    if h_trap is not None:
        traps.append((h_trap, 2))
        
    d_trap = _detect_diagonal_trap(board, piece)
    if d_trap is not None:
        traps.append((d_trap, 1))
    
    developing_trap = _detect_developing_trap(board, piece)
    if developing_trap is not None:
        traps.append((developing_trap, 0))
    
    # Verify traps and return highest priority one
    for col, priority in sorted(traps, key=lambda x: x[1], reverse=True):
        temp_board = ConnectFourBoard()
        temp_board.board = board.get_board()
        row = temp_board.get_next_open_row(col)
        if row != -1:
            temp_board.board[row][col] = piece
            # High priority traps (4) are pre-verified
            if priority == 4 or temp_board.is_winning_move(piece):
                return col
    
    return None

def _detect_double_threat(board, col, piece):
    """Checks if move creates two or more winning threats"""
    temp_board = ConnectFourBoard()
    temp_board.board = board.get_board()
    row = temp_board.get_next_open_row(col)
    if row == -1:
        return False
        
    temp_board.drop_piece(col, piece)
    
    # Count potential winning moves after this move
    winning_columns = []
    for next_col in range(COLS):
        if temp_board.is_valid_location(next_col):
            next_row = temp_board.get_next_open_row(next_col)
            temp_board.board[next_row][next_col] = piece
            if temp_board.is_winning_move(piece):
                winning_columns.append(next_col)
            temp_board.board[next_row][next_col] = EMPTY
    
    return len(winning_columns) >= 2

def _is_move_safe(board, col, piece):
    """Checks if move allows opponent to win next turn"""
    opponent = 3 - piece
    temp_board = ConnectFourBoard()
    temp_board.board = board.get_board()
    row = temp_board.get_next_open_row(col)
    
    if row == -1:
        return False
    
    temp_board.drop_piece(col, piece)
    
    # Check if opponent can win immediately
    for opp_col in temp_board.get_valid_locations():
        opp_row = temp_board.get_next_open_row(opp_col)
        temp_board.board[opp_row][opp_col] = opponent
        if temp_board.is_winning_move(opponent):
            return False
        temp_board.board[opp_row][opp_col] = EMPTY
    
    # Check if placing our piece sets up a vertical win for opponent
    if row > 0:
        temp_board.board[row-1][col] = opponent
        if temp_board.is_winning_move(opponent):
            return False
    
    return True

def _creates_alignment(board, col, piece, min_count=2):
    """Checks if move creates an alignment of pieces"""
    temp_board = ConnectFourBoard()
    temp_board.board = board.get_board()
    row = temp_board.get_next_open_row(col)
    if row == -1:
        return False
    
    temp_board.board[row][col] = piece
    board_array = temp_board.board
    
    # Check all directions for alignments
    directions = [
        [(0, 1), (0, -1)],   # horizontal
        [(1, 0), (-1, 0)],   # vertical
        [(1, 1), (-1, -1)],  # diagonal \
        [(1, -1), (-1, 1)]   # diagonal /
    ]
    
    for dir_pair in directions:
        count = 1  # Start with current piece
        for dx, dy in dir_pair:
            r, c = row, col
            for _ in range(3):  # Check up to 3 in each direction
                r, c = r + dy, c + dx
                if 0 <= r < ROWS and 0 <= c < COLS and board_array[r][c] == piece:
                    count += 1
                else:
                    break
            if count >= min_count:
                return True
    
    return False

def _check_immediate_win(board, piece):
    """Checks for an immediate winning move"""
    for col in board.get_valid_locations():
        row = board.get_next_open_row(col)
        temp_board = ConnectFourBoard()
        temp_board.board = board.get_board()
        temp_board.board[row][col] = piece
        if temp_board.is_winning_move(piece):
            return col
    return None

def find_best_move(board, piece):
    """Core expert system logic to find the best move"""
    opponent = 3 - piece
    valid_cols = board.get_valid_locations()
    
    if not valid_cols:
        return None
    
    # Center column is preferred, then radiating outward
    center_col = COLS // 2
    preferred_cols = [center_col]
    for offset in range(1, COLS // 2 + 1):
        if center_col + offset < COLS:
            preferred_cols.append(center_col + offset)
        if center_col - offset >= 0:
            preferred_cols.append(center_col - offset)
    
    # Game phase affects strategy
    game_phase = _get_game_phase(board)
    
    # --- Rule 1: Win if possible ---
    win_move = _check_immediate_win(board, piece)
    if win_move is not None:
        return win_move
    
    # --- Rule 2: Block opponent's win ---
    block_move = _check_immediate_win(board, opponent)
    if block_move is not None:
        return block_move
    
    # --- Rule 3: Block opponent's developing traps ---
    dev_trap = _detect_developing_trap(board, opponent)
    if dev_trap is not None:
        return dev_trap
    
    # --- Rule 4: Block opponent's open-ended threats ---
    open_trap = _detect_open_ended_three_in_a_row(board, opponent)
    if open_trap is not None:
        return open_trap
      
    # --- Rule 5: Block opponent's other traps ---
    opp_trap = _detect_trap_threat(board, opponent)
    if opp_trap is not None:
        return opp_trap
    
    # --- Rule 6: Create our own threats ---
    # First check developing threats
    our_dev_trap = _detect_developing_trap(board, piece)
    if our_dev_trap is not None:
        return our_dev_trap
    
    # Then check open-ended threats
    our_open_trap = _detect_open_ended_three_in_a_row(board, piece)
    if our_open_trap is not None:
        return our_open_trap
        
    # Then check double threats
    for col in valid_cols:
        if _detect_double_threat(board, col, piece):
            return col
    
    # Then check regular traps
    our_trap = _detect_trap_threat(board, piece)
    if our_trap is not None:
        return our_trap
  
    # --- Rule 7: Find safe moves that create alignments ---
    safe_moves = []
    good_moves = []
    for col in valid_cols:
        if _is_move_safe(board, col, piece):
            safe_moves.append(col)
            if _creates_alignment(board, col, piece):
                good_moves.append(col)
    
    # --- Rule 8: Phase-specific strategy ---
    if game_phase == 'opening':
        # Prioritize center in opening
        for col in preferred_cols:
            if col in safe_moves:
                return col
    
    elif game_phase == 'midgame':
        # Prioritize alignment moves in midgame
        if good_moves:
            for col in preferred_cols:
                if col in good_moves:
                    return col
            return random.choice(good_moves)
    
    else:  # endgame
        # Be more aggressive in endgame
        if good_moves:
            return random.choice(good_moves)
    
    # --- Rule 9: Fall back to safe moves ---
    if safe_moves:
        for col in preferred_cols:
            if col in safe_moves:
                return col
        return random.choice(safe_moves)
    
    # --- Rule 10: Last resort - any valid move ---
    for col in preferred_cols:
        if col in valid_cols:
            return col
            
    return random.choice(valid_cols)

# --- Public Interface ---

def get_move(board_state, piece):
    """Returns best move for the current board state"""
    board = ConnectFourBoard()
    board.board = board_state.copy()
    return find_best_move(board, piece)
  
def name():
    """Returns the algorithm name"""
    return "Expert System"