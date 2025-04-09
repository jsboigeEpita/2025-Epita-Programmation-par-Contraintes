import numpy as np
from board import ConnectFourBoard
import random

# Constants
ROW_COUNT = 6
COLUMN_COUNT = 7
EMPTY = 0
CENTER_COLUMN = COLUMN_COUNT // 2  # Column 3 in standard Connect Four

# --- Pattern Database ---
# Each pattern is represented as a 2D numpy array where:
# - 1 represents AI's pieces
# - 2 represents opponent's pieces
# - 0 represents empty spaces
# - -1 represents "don't care" positions (can be any value)
# Each pattern also includes the recommended move column(s)

class Pattern:
    def __init__(self, name, grid_pattern, response_columns, priority=1):
        """
        Initialize a pattern with its recognition grid and response moves.
        
        Parameters:
        - name: String identifier for the pattern
        - grid_pattern: 2D numpy array representing the pattern
        - response_columns: List of column indices for the recommended moves
        - priority: Integer priority (higher means more important)
        """
        self.name = name
        self.grid_pattern = np.array(grid_pattern)
        self.response_columns = response_columns
        self.priority = priority
        
    def __str__(self):
        return f"Pattern: {self.name} (priority: {self.priority})"

# --- Opening Patterns ---
OPENING_PATTERNS = [
    Pattern("Center Opening", 
           [[-1, -1, -1, 0, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [CENTER_COLUMN], 5),
           
    Pattern("Respond to Center", 
           [[-1, -1, -1, 2, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [CENTER_COLUMN-1, CENTER_COLUMN+1], 4)
]

# --- Tactical Patterns ---
# Win Patterns
WIN_PATTERNS = [
    Pattern("Horizontal Win", 
           [[-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 1, 1, 1, 0, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [5], 100),  # Example: win by completing a horizontal line
    
    Pattern("Vertical Win", 
           [[-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 0, -1, -1, -1, -1],
            [-1, -1, 1, -1, -1, -1, -1],
            [-1, -1, 1, -1, -1, -1, -1],
            [-1, -1, 1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [2], 100),  # Example: win by completing a vertical line
           
    # Diagonal patterns would be similar
]

# Blocking Patterns
BLOCKING_PATTERNS = [
    Pattern("Horizontal Block", 
           [[-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 2, 2, 2, 0, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [5], 90),  # Example: block opponent's horizontal win
           
    # More blocking patterns would follow the same structure
]

# Trap/Setup Patterns
TRAP_PATTERNS = [
    Pattern("Double Threat Setup", 
           [[-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 0, -1, -1, -1, -1],
            [-1, -1, 1, 0, 1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [3], 80),  # Creating a potential double threat
           
    Pattern("Block Double Threat", 
           [[-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, 0, -1, -1, -1, -1],
            [-1, -1, 2, 0, 2, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1]], 
           [3], 70)   # Prevent opponent from creating double threat
]

# --- All patterns combined with priority order ---
ALL_PATTERNS = WIN_PATTERNS + BLOCKING_PATTERNS + TRAP_PATTERNS + OPENING_PATTERNS

# --- Pattern Recognition Functions ---

def normalize_board_for_pattern_matching(board_array, piece):
    """
    Normalizes the board for pattern matching. Our patterns assume:
    - 1 represents the AI's pieces
    - 2 represents the opponent's pieces
    - 0 represents empty
    
    This function converts the actual board to this normalized form.
    """
    normalized = np.copy(board_array)
    # Make sure AI's pieces are always represented as 1
    if piece == 2:
        # Swap 1 and 2 in the board
        normalized[normalized == 1] = 3  # Temporarily use 3
        normalized[normalized == 2] = 1
        normalized[normalized == 3] = 2
    return normalized

def rotate_pattern(pattern_grid):
    """Rotate the pattern 90 degrees clockwise."""
    return np.rot90(pattern_grid, k=1, axes=(1, 0))

def flip_pattern_horizontal(pattern_grid):
    """Flip the pattern horizontally."""
    return np.fliplr(pattern_grid)

def pattern_matches(board_section, pattern_grid):
    """
    Check if the board section matches the pattern grid.
    A pattern matches if all non-(-1) positions in the pattern
    match the corresponding positions in the board.
    """
    mask = (pattern_grid != -1)
    return np.all(board_section[mask] == pattern_grid[mask])

def scan_board_for_pattern(board_array, pattern):
    """
    Scan the entire board for occurrences of the pattern.
    Returns list of (row, col) tuples where pattern was found.
    """
    pattern_height, pattern_width = pattern.grid_pattern.shape
    board_height, board_width = board_array.shape
    matches = []
    
    # Scan all possible positions where the pattern could fit
    for row in range(board_height - pattern_height + 1):
        for col in range(board_width - pattern_width + 1):
            board_section = board_array[row:row+pattern_height, col:col+pattern_width]
            if pattern_matches(board_section, pattern.grid_pattern):
                # Found a match - record its position
                matches.append((row, col))
    
    return matches

def find_matching_patterns(board_array, patterns_list, piece):
    """
    Find all patterns that match the current board state.
    Returns list of (pattern, position) tuples ordered by priority.
    """
    normalized_board = normalize_board_for_pattern_matching(board_array, piece)
    matched_patterns = []
    
    for pattern in patterns_list:
        # Check original pattern
        matches = scan_board_for_pattern(normalized_board, pattern)
        for match_pos in matches:
            matched_patterns.append((pattern, match_pos))
        
        # Check rotated pattern (90 degrees)
        rotated_pattern = Pattern(
            pattern.name + " (rotated)", 
            rotate_pattern(pattern.grid_pattern),
            pattern.response_columns,  # Response columns need translation based on rotation
            pattern.priority
        )
        matches = scan_board_for_pattern(normalized_board, rotated_pattern)
        for match_pos in matches:
            matched_patterns.append((rotated_pattern, match_pos))
            
        # Check flipped pattern
        flipped_pattern = Pattern(
            pattern.name + " (flipped)", 
            flip_pattern_horizontal(pattern.grid_pattern),
            [COLUMN_COUNT - 1 - col for col in pattern.response_columns],  # Adjust response columns
            pattern.priority
        )
        matches = scan_board_for_pattern(normalized_board, flipped_pattern)
        for match_pos in matches:
            matched_patterns.append((flipped_pattern, match_pos))
    
    # Sort by priority (highest first)
    return sorted(matched_patterns, key=lambda x: x[0].priority, reverse=True)

def translate_pattern_move_to_board_move(pattern_move, pattern_pos, board_obj, piece):
    """
    Translate a move recommended by the pattern to an actual board column,
    taking into account the position where the pattern was found.
    
    Also verify the move is valid before returning.
    """
    row_offset, col_offset = pattern_pos
    board_col = pattern_move + col_offset
    
    # Ensure the move is within board bounds
    if 0 <= board_col < COLUMN_COUNT and board_obj.is_valid_location(board_col):
        return board_col
    return None

def get_winning_move(board_obj, piece):
    """Check if there's an immediate winning move."""
    for col in range(COLUMN_COUNT):
        if board_obj.is_valid_location(col):
            temp_board = ConnectFourBoard()
            temp_board.board = board_obj.get_board()
            row = temp_board.get_next_open_row(col)
            if row != -1:
                temp_board.board[row][col] = piece
                if temp_board.is_winning_move(piece):
                    return col
    return None

def get_blocking_move(board_obj, piece):
    """Check if opponent has a winning move that needs to be blocked."""
    opponent = 3 - piece
    for col in range(COLUMN_COUNT):
        if board_obj.is_valid_location(col):
            temp_board = ConnectFourBoard()
            temp_board.board = board_obj.get_board()
            row = temp_board.get_next_open_row(col)
            if row != -1:
                temp_board.board[row][col] = opponent
                if temp_board.is_winning_move(opponent):
                    return col
    return None

# --- Main AI Function ---

def get_move(board_state, piece):
    """
    Get the AI's move using pattern matching.
    
    Parameters:
    - board_state: numpy array - The Connect Four board state
    - piece: int - The player's piece (1 or 2)
    
    Returns:
    - col: int - The column where the AI wants to place its piece
    """
    # Create a board object for analysis
    board_obj = ConnectFourBoard()
    board_obj.board = np.copy(board_state)
    
    # Priority 1: Check for immediate winning move
    winning_move = get_winning_move(board_obj, piece)
    if winning_move is not None:
        return winning_move
        
    # Priority 2: Check for opponent's winning move to block
    blocking_move = get_blocking_move(board_obj, piece)
    if blocking_move is not None:
        return blocking_move
    
    # Priority 3: Use pattern matching
    matched_patterns = find_matching_patterns(board_state, ALL_PATTERNS, piece)
    
    # Try each matched pattern's recommended move
    for pattern, position in matched_patterns:
        for recommended_col in pattern.response_columns:
            actual_col = translate_pattern_move_to_board_move(
                recommended_col, position, board_obj, piece)
            if actual_col is not None:
                # Debug: Print what pattern was matched
                # print(f"Matched pattern: {pattern.name} at {position}, playing column {actual_col}")
                return actual_col
    
    # Priority 4: If no patterns match or all recommended moves are invalid,
    # default to center preference
    valid_locations = board_obj.get_valid_locations()
    if not valid_locations:
        return None  # Board is full
    
    # Prefer center column, then columns progressively further from center
    preferred_columns = [CENTER_COLUMN]
    for i in range(1, COLUMN_COUNT//2 + 1):
        if CENTER_COLUMN + i < COLUMN_COUNT:
            preferred_columns.append(CENTER_COLUMN + i)
        if CENTER_COLUMN - i >= 0:
            preferred_columns.append(CENTER_COLUMN - i)
            
    for col in preferred_columns:
        if col in valid_locations:
            return col
            
    # Fallback - should rarely happen if patterns and preferences are comprehensive
    return random.choice(valid_locations)
    
def name():
    """Return the name of the algorithm."""
    return "Pattern-Based"