import random
import numpy as np
from board import ConnectFourBoard

def get_move(board, piece):
    """
    Always place at first column if available.
    """
    # Create a temporary board object to use its methods
    temp_board = ConnectFourBoard()
    temp_board.board = board.copy()
    
    # Use the board's method to get valid locations
    valid_locations = temp_board.get_valid_locations()
    
    if not valid_locations:
        return None  # No valid moves
    
    # Choose a random column from valid moves
    return valid_locations[0]  # Always choose the first valid column
  
def name():
    """
    Returns the name of this AI algorithm
    """
    return "Always First"