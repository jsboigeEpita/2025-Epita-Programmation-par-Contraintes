import numpy as np

class ConnectFourBoard:
    """
    A class representing the Connect Four game board and its logic.
    """
    
    # Board dimensions
    ROW_COUNT = 6
    COLUMN_COUNT = 7
    
    def __init__(self):
        """
        Initialize a new Connect Four board
        """
        self.board = np.zeros((self.ROW_COUNT, self.COLUMN_COUNT))
        self.game_over = False
        self.winner = None
    
    def get_board(self):
        """
        Returns a copy of the current board state
        """
        return self.board.copy()
    
    def drop_piece(self, col, piece):
        """
        Place a piece in the specified column. 
        Returns the row where the piece was placed, or -1 if the column is full.
        
        Parameters:
        - col: int - The column to place the piece
        - piece: int - The player's piece (1 or 2)
        
        Returns:
        - row: int - The row where the piece was placed, or -1 if invalid
        """
        # Find the lowest empty row in the column
        row = self.get_next_open_row(col)
        
        if row != -1:  # If column is not full
            self.board[row][col] = piece
            
            # Check if this move wins the game
            if self.is_winning_move(piece):
                self.game_over = True
                self.winner = piece
                
            # Check if board is full (tie)
            if len(self.get_valid_locations()) == 0:
                self.game_over = True
                
            return row
        return -1
    
    def is_valid_location(self, col):
        """
        Check if a column has an available space
        """
        return (0 <= col < self.COLUMN_COUNT) and (self.board[0][col] == 0)
    
    def get_next_open_row(self, col):
        """
        Find the lowest empty row in a given column
        """
        for r in range(self.ROW_COUNT-1, -1, -1):
            if self.board[r][col] == 0:
                return r
        return -1  # Column is full
    
    def get_valid_locations(self):
        """
        Find all valid locations to place a piece
        """
        valid_locations = []
        for col in range(self.COLUMN_COUNT):
            if self.is_valid_location(col):
                valid_locations.append(col)
        return valid_locations
    
    def is_winning_move(self, piece):
        """
        Check if the last move resulted in a win
        """
        # Check horizontal
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT):
                if (self.board[r][c] == piece and 
                    self.board[r][c+1] == piece and 
                    self.board[r][c+2] == piece and 
                    self.board[r][c+3] == piece):
                    return True
    
        # Check vertical
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT-3):
                if (self.board[r][c] == piece and 
                    self.board[r+1][c] == piece and 
                    self.board[r+2][c] == piece and 
                    self.board[r+3][c] == piece):
                    return True
    
        # Check positively sloped diagonals
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT-3):
                if (self.board[r][c] == piece and 
                    self.board[r+1][c+1] == piece and 
                    self.board[r+2][c+2] == piece and 
                    self.board[r+3][c+3] == piece):
                    return True
    
        # Check negatively sloped diagonals
        for c in range(self.COLUMN_COUNT-3):
            for r in range(3, self.ROW_COUNT):
                if (self.board[r][c] == piece and 
                    self.board[r-1][c+1] == piece and 
                    self.board[r-2][c+2] == piece and 
                    self.board[r-3][c+3] == piece):
                    return True
    
        return False
    
    def print_board(self):
        """
        Print the board to the console (for debugging)
        """
        print(np.flip(self.board, 0))
    
    def reset(self):
        """
        Reset the board to a new game state
        """
        self.board = np.zeros((self.ROW_COUNT, self.COLUMN_COUNT))
        self.game_over = False
        self.winner = None