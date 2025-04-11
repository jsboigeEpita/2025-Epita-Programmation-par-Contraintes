import pygame
import numpy as np
import sys
from board import ConnectFourBoard

# Colors for the game
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Size of each cell in the board
SQUARESIZE = 100
# Width and height of the board
WIDTH = ConnectFourBoard.COLUMN_COUNT * SQUARESIZE
HEIGHT = (ConnectFourBoard.ROW_COUNT + 1) * SQUARESIZE  # Extra row for piece drop animation
RADIUS = int(SQUARESIZE/2 - 5)

class GameGUI:
    """
    Class to handle the graphical user interface for Connect Four
    """
    def __init__(self, player1_name="Player 1", player2_name="Player 2"):
        """
        Initialize the GUI
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font = pygame.font.SysFont("monospace", 45)
        self.player_names = [player1_name, player2_name]
    
    def draw_board(self, board_state):
        """
        Draw the Connect Four board with pieces
        
        Parameters:
        - board_state: numpy array - The current board state
        """
        # Make sure we don't draw over the top indicator area
        pygame.draw.rect(self.screen, BLACK, (0, SQUARESIZE, WIDTH, HEIGHT - SQUARESIZE))
        
        # Draw the blue board with empty circles
        for c in range(ConnectFourBoard.COLUMN_COUNT):
            for r in range(ConnectFourBoard.ROW_COUNT):
                pygame.draw.rect(self.screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
                pygame.draw.circle(self.screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), 
                                                  int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
        
        # Draw the game pieces (red or yellow)
        for c in range(ConnectFourBoard.COLUMN_COUNT):
            for r in range(ConnectFourBoard.ROW_COUNT):
                if board_state[r][c] == 1:  # Player 1 (red)
                    pygame.draw.circle(self.screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), 
                                                    int((r+1)*SQUARESIZE+SQUARESIZE/2)), RADIUS)
                elif board_state[r][c] == 2:  # Player 2 (yellow)
                    pygame.draw.circle(self.screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), 
                                                      int((r+1)*SQUARESIZE+SQUARESIZE/2)), RADIUS)
        
        # Update only the board area, not the top row
        pygame.display.update(pygame.Rect(0, SQUARESIZE, WIDTH, HEIGHT - SQUARESIZE))
    
    def animate_drop(self, board_state, row, col, piece, speed=15):
        """
        Animate the piece dropping into the board with proper rendering
        
        Parameters:
        - board_state: numpy array - The current board state
        - row: int - The row where the piece will land
        - col: int - The column where the piece is dropping
        - piece: int - The player's piece (1 or 2)
        - speed: int - The animation speed
        """
        color = RED if piece == 1 else YELLOW
        
        # Calculate final position
        final_y = int((row+1)*SQUARESIZE+SQUARESIZE/2)
        
        # Start position (just below the top bar)
        y_pos = SQUARESIZE + RADIUS
        
        # Create a copy of the board state that doesn't include the piece we're dropping
        temp_board = board_state.copy()
        temp_board[row][col] = 0  # Remove the piece from its final position
        
        # Ensure top row is black
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
        pygame.display.update(pygame.Rect(0, 0, WIDTH, SQUARESIZE))
        
        while y_pos < final_y:
            pygame.event.pump() # To avoid annoying "Application not responding" messages
            # First, redraw the entire board to clear any visual artifacts
            self.draw_board(temp_board)
            
            # Then draw the falling piece at its current position
            pygame.draw.circle(self.screen, color, (int(col*SQUARESIZE+SQUARESIZE/2), int(y_pos)), RADIUS)
            
            # Update the display
            pygame.display.update()
            
            # Wait a bit
            pygame.time.Clock().tick(60)
            
            # Move piece down
            y_pos += speed
        
        # Once animation is complete, draw the board with the piece in its final position
        self.draw_board(board_state)
        
        # Ensure top row is black
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
        pygame.display.update(pygame.Rect(0, 0, WIDTH, SQUARESIZE))
    
    def update_player_indicator(self, turn):
        """
        Update the player indicator at the top of the screen
        
        Parameters:
        - turn: int - 0 for player 1's turn, 1 for player 2's turn
        """
        # Clear only the top indicator area
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
        
        # Draw player indicator
        color = RED if turn == 0 else YELLOW
        name = self.player_names[turn]
        text = self.font.render(f"{name}'s turn", True, color)
        self.screen.blit(text, (WIDTH / 2 - text.get_width() / 2, SQUARESIZE / 2 - text.get_height() / 2))
        
        # Update only the top part of the screen
        pygame.display.update(pygame.Rect(0, 0, WIDTH, SQUARESIZE))
    
    def draw_piece_at_mouse(self, x_pos, turn):
        """
        Draw the current player's piece at the mouse position
        
        Parameters:
        - x_pos: int - Mouse x position
        - turn: int - 0 for player 1's turn, 1 for player 2's turn
        """
        # Completely clear the top area
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
        
        # Make sure x_pos is within bounds
        x_pos = max(RADIUS, min(WIDTH - RADIUS, x_pos))
        
        # Draw the hovering piece
        color = RED if turn == 0 else YELLOW
        pygame.draw.circle(self.screen, color, (x_pos, int(SQUARESIZE/2)), RADIUS)
        
        # Update only the top part of the screen
        pygame.display.update(pygame.Rect(0, 0, WIDTH, SQUARESIZE))
    
    def show_winner(self, player):
        """
        Display the winner message
        
        Parameters:
        - player: int - The winning player (1 or 2)
        """
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
        name = self.player_names[player - 1]
        color = RED if player == 1 else YELLOW
        label = self.font.render(f"{name} (Player {player}) wins!", True, color)
        self.screen.blit(label, (WIDTH / 2 - label.get_width() / 2, SQUARESIZE / 2 - label.get_height() / 2))
        pygame.display.update()
    
    def show_tie(self):
        """
        Display the tie game message
        """
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
        label = self.font.render("It's a tie!", True, BLUE)
        self.screen.blit(label, (WIDTH / 2 - label.get_width() / 2, SQUARESIZE / 2 - label.get_height() / 2))
        pygame.display.update()
