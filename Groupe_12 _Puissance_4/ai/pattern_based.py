import numpy as np
from board import ConnectFourBoard
import random

# Constants
ROWS = 6
COLS = 7
EMPTY = 0
CENTER = COLS // 2

class Pattern:
    def __init__(self, name, grid, response_cols, priority=1):
        self.name = name
        self.grid = np.array(grid)
        self.responses = response_cols
        self.priority = priority

# --- Pattern Database ---
# Win patterns (priority 100)
WIN_PATTERNS = [
    Pattern("Horizontal Win", 
           [[-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 1, 1, 1, 0, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [5], 100),
    
    Pattern("Vertical Win", 
           [[-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 0, -1, -1, -1, -1],
            [-1, -1, 1, -1, -1, -1, -1],
            [-1, -1, 1, -1, -1, -1, -1],
            [-1, -1, 1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [2], 100),
]

# Blocking patterns (priority 90)
BLOCK_PATTERNS = [
    Pattern("Horizontal Block", 
           [[-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 2, 2, 2, 0, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [5], 90),
]

# Trap/Setup patterns (priority 70-80)
TRAP_PATTERNS = [
    Pattern("Double Threat Setup", 
           [[-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 0, -1, -1, -1, -1],
            [-1, -1, 1, 0, 1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [3], 80),
           
    Pattern("Block Double Threat", 
           [[-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 0, -1, -1, -1, -1],
            [-1, -1, 2, 0, 2, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [3], 70)
]

# Opening patterns (priority 4-5)
OPENING_PATTERNS = [
    Pattern("Center Opening", 
           [[-1, -1, -1, 0, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [CENTER], 5),
           
    Pattern("Respond to Center", 
           [[-1, -1, -1, 2, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [CENTER-1, CENTER+1], 4)
]

# All patterns combined in priority order
ALL_PATTERNS = WIN_PATTERNS + BLOCK_PATTERNS + TRAP_PATTERNS + OPENING_PATTERNS

def normalize_board(board, piece):
    """Convert board so AI is piece 1, opponent is piece 2"""
    result = np.copy(board)
    if piece == 2:  # Swap 1 and 2
        result[result == 1] = 3  # Use 3 as temp
        result[result == 2] = 1
        result[result == 3] = 2
    return result

def pattern_matches(section, pattern):
    """Check if board section matches pattern where -1 means "don't care"""
    mask = (pattern != -1)
    return np.all(section[mask] == pattern[mask])

def find_matches(board, pattern, piece):
    """Find all positions where pattern matches on the board"""
    normalized = normalize_board(board, piece)
    h, w = pattern.grid.shape
    board_h, board_w = normalized.shape
    matches = []
    
    # Check original pattern
    for row in range(board_h - h + 1):
        for col in range(board_w - w + 1):
            section = normalized[row:row+h, col:col+w]
            if pattern_matches(section, pattern.grid):
                matches.append((pattern, (row, col)))
    
    # Check rotated pattern (90° clockwise)
    rotated = np.rot90(pattern.grid, k=1, axes=(1, 0))
    for row in range(board_h - rotated.shape[0] + 1):
        for col in range(board_w - rotated.shape[1] + 1):
            section = normalized[row:row+rotated.shape[0], col:col+rotated.shape[1]]
            if pattern_matches(section, rotated):
                # Need to adjust response columns for rotation - simplified here
                matches.append((Pattern(pattern.name, rotated, pattern.responses, pattern.priority), 
                               (row, col)))
    
    # Check horizontally flipped pattern
    flipped = np.fliplr(pattern.grid)
    flipped_responses = [COLS - 1 - col for col in pattern.responses]
    for row in range(board_h - h + 1):
        for col in range(board_w - w + 1):
            section = normalized[row:row+h, col:col+w]
            if pattern_matches(section, flipped):
                matches.append((Pattern(pattern.name, flipped, flipped_responses, pattern.priority), 
                               (row, col)))
                
    return matches

def find_all_matches(board, patterns, piece):
    """Find all pattern matches across the board"""
    results = []
    for pattern in patterns:
        results.extend(find_matches(board, pattern, piece))
    
    # Sort by priority (highest first)
    return sorted(results, key=lambda x: x[0].priority, reverse=True)

def translate_move(pattern_col, offset, board):
    """Convert pattern-relative column to actual board column"""
    board_col = pattern_col + offset
    if 0 <= board_col < COLS and board.is_valid_location(board_col):
        return board_col
    return None

def check_immediate_win(board, piece):
    """Find any column that gives an immediate win"""
    for col in range(COLS):
        if board.is_valid_location(col):
            row = board.get_next_open_row(col)
            if row == -1:
                continue
                
            # Try the move
            temp = ConnectFourBoard()
            temp.board = board.get_board()
            temp.board[row][col] = piece
            
            if temp.is_winning_move(piece):
                return col
    return None

def get_move(board_state, piece):
    """Get best move using pattern matching"""
    board = ConnectFourBoard()
    board.board = np.copy(board_state)
    opponent = 3 - piece
    
    # 1. Win if possible
    winning_move = check_immediate_win(board, piece)
    if winning_move is not None:
        return winning_move
        
    # 2. Block opponent's win
    blocking_move = check_immediate_win(board, opponent)
    if blocking_move is not None:
        return blocking_move
    
    # 3. Use pattern matching
    matches = find_all_matches(board_state, ALL_PATTERNS, piece)
    
    # Try each matched pattern's recommended move
    for pattern, (row, col) in matches:
        for rec_col in pattern.responses:
            actual_col = translate_move(rec_col, col, board)
            if actual_col is not None:
                return actual_col
    
    # 4. Default to center preference
    valid_cols = board.get_valid_locations()
    if not valid_cols:
        return None
    
    # Prefer center, then outward
    preferred = [CENTER]
    for i in range(1, COLS//2 + 1):
        if CENTER + i < COLS:
            preferred.append(CENTER + i)
        if CENTER - i >= 0:
            preferred.append(CENTER - i)
            
    for col in preferred:
        if col in valid_cols:
            return col
            
    return random.choice(valid_cols)
    
def name():
    return "Pattern-Based"