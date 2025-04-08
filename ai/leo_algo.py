import numpy as np
from board import ConnectFourBoard

def get_move(board, piece):
    """
    Returns the best move for the given board state using a simple heuristic.
    
    Parameters:
    - board: numpy array - The Connect Four board state
    - piece: int - The player's piece (1 or 2)
    
    Returns:
    - col: int - The column where the AI wants to place its piece
    """
    # Create a temporary board object to use its methods
    temp_board = ConnectFourBoard()
    temp_board.board = board.copy()
    
    # Check for winning move
    for col in range(temp_board.COLUMN_COUNT):
        if temp_board.is_valid_location(col):
            row = temp_board.get_next_open_row(col)
            temp_board.drop_piece(col, piece) 
            if temp_board.is_winning_move(piece):
                return col
            temp_board.board[row][col] = 0
    
    # Check if opponent can win in the next move, if they can block
    for col in range(temp_board.COLUMN_COUNT):
        if temp_board.is_valid_location(col):
            row = temp_board.get_next_open_row(col)
            temp_board.drop_piece(col, 3 - piece) 
            if temp_board.is_winning_move(3 - piece):
                return col
            temp_board.board[row][col] = 0
            
    # For horizontal checks, we need to stop 3 columns before the end
    for col in range(temp_board.COLUMN_COUNT - 3):
        for row in range(temp_board.ROW_COUNT):
            # Check for horizontal potential double threat
            if (temp_board.board[row][col] == 0 and
                temp_board.board[row][col+1] == 3 - piece and
                temp_board.board[row][col+2] == 3 - piece and
                temp_board.board[row][col+3] == 0 and
                temp_board.is_valid_location(col) and
                temp_board.is_valid_location(col+3) and
                temp_board.get_next_open_row(col) == row and
                temp_board.get_next_open_row(col+3) == row):
                # Block one of the sides
                return col if np.random.random() < 0.5 else col + 3
    
    # If no winning move or block, choose a move that doesn't give opponent a win
    valid_locations = temp_board.get_valid_locations()
    if not valid_locations:
        return None  # No valid moves
    
    # Find moves that don't give the opponent an immediate win
    safe_moves = []
    opponent_piece = 3 - piece
    
    for col in valid_locations:
        # Create a copy of the board to simulate our move
        board_copy = ConnectFourBoard()
        board_copy.board = temp_board.board.copy()
        
        # Simulate dropping our piece
        row = board_copy.get_next_open_row(col)
        board_copy.drop_piece(col, piece)
        
        # Now check if opponent would have a winning move
        gives_win_to_opponent = False
        
        # Check each column the opponent could play in
        for opp_col in board_copy.get_valid_locations():
            opp_row = board_copy.get_next_open_row(opp_col)
            
            # Try placing opponent's piece and see if they win
            board_copy.board[opp_row][opp_col] = opponent_piece
            if board_copy.is_winning_move(opponent_piece):
                gives_win_to_opponent = True
                board_copy.board[opp_row][opp_col] = 0  # Undo move
                break
            
            # Undo the opponent's move
            board_copy.board[opp_row][opp_col] = 0
        
        if not gives_win_to_opponent:
            safe_moves.append(col)
    
    # If there are safe moves, choose one randomly
    if safe_moves:
        return np.random.choice(safe_moves)
    
    # If there are no safe moves, just pick any valid move
    # (we're going to lose anyway if all moves give opponent a win)
    return np.random.choice(valid_locations)
  
def name():
    """
    Returns the name of this AI algorithm
    """
    return "leo AI"