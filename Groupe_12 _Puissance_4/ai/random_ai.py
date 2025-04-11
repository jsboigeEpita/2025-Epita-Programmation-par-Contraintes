import random
import numpy as np
from board import ConnectFourBoard

def get_move(board, piece):
    """
    Returns a random valid move for the given board state.
    
    Parameters:
    - board: numpy array - The Connect Four board state
    - piece: int - The player's piece (1 or 2)
    
    Returns:
    - col: int - The column where the AI wants to place its piece
    """
    # Create a temporary board object to use its methods
    temp_board = ConnectFourBoard()
    temp_board.board = board.copy()
    
    # Use the board's method to get valid locations
    valid_locations = temp_board.get_valid_locations()
    
    if not valid_locations:
        return None  # No valid moves
    
    # Choose a random column from valid moves
    return random.choice(valid_locations)

def name():
    """
    Returns the name of this AI algorithm
    """
    return "Random"