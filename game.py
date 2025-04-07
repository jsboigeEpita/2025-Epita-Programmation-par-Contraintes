import numpy as np
import pygame
import sys
import importlib
import os
from board import ConnectFourBoard
from gui import GameGUI, SQUARESIZE, WIDTH, HEIGHT, RADIUS, RED, YELLOW, BLACK, BLUE
import logging
import importlib.util
import traceback


# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger('connect4')


class Game:
    """
    Main game class to handle game modes and logic
    """
    
    def __init__(self):
        """
        Initialize the game
        """
        pygame.init()
        self.board = ConnectFourBoard()
        self.gui = GameGUI()
        self.ai_modules = self._load_ai_modules()
    
    def _load_ai_modules(self):
        """
        Load all AI modules from the ai directory with detailed logging
        """
        ai_modules = {}
        ai_dir = "ai"
        
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Looking for AI modules in directory: {ai_dir}")
        logger.info(f"Python path: {sys.path}")
        
        try:
            # Check if directory exists
            if not os.path.exists(ai_dir):
                logger.error(f"AI directory '{ai_dir}' does not exist")
                return ai_modules
                
            # List all files in the ai directory
            files = os.listdir(ai_dir)
            logger.info(f"Files in AI directory: {files}")
            
            # List all Python files in the ai directory
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    module_name = file[:-3]  # Remove .py extension
                    full_module_path = f"{ai_dir}.{module_name}"
                    file_path = os.path.join(ai_dir, file)
                    
                    logger.info(f"Attempting to import module: {full_module_path}")
                    logger.info(f"File path: {file_path}")
                    
                    try:
                        # Try direct import first
                        logger.debug(f"Trying direct import for {full_module_path}")
                        module = importlib.import_module(full_module_path)
                        logger.info(f"Successfully imported {full_module_path}")
                        
                    except ImportError as e:
                        logger.warning(f"Direct import failed for {full_module_path}: {e}")
                        logger.debug(f"Traceback: {traceback.format_exc()}")
                        
                        # Try alternative import method
                        try:
                            logger.debug(f"Trying spec-based import for {module_name}")
                            spec = importlib.util.spec_from_file_location(module_name, file_path)
                            if spec is None:
                                logger.error(f"Could not find spec for {module_name} at {file_path}")
                                continue
                                
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[module_name] = module  # Register in sys.modules
                            spec.loader.exec_module(module)
                            logger.info(f"Successfully imported {module_name} via spec")
                            
                        except Exception as e:
                            logger.error(f"Spec-based import failed for {module_name}: {e}")
                            logger.debug(f"Traceback: {traceback.format_exc()}")
                            continue
                    
                    # Check if the module has the required functions
                    if hasattr(module, 'get_move'):
                        if hasattr(module, 'name'):
                            ai_name = module.name()
                        else:
                            ai_name = module_name
                            
                        logger.info(f"Successfully loaded AI: {ai_name}")
                        ai_modules[ai_name] = module
                    else:
                        logger.error(f"Module {module_name} is missing the required get_move function")
                        
        except Exception as e:
            logger.error(f"Error loading AI modules: {e}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
        
        logger.info(f"Loaded {len(ai_modules)} AI modules: {list(ai_modules.keys())}")
        return ai_modules
    
    def human_vs_human(self):
        """
        Run a human vs human game
        """
        self.board.reset()
        screen = self.gui.screen
        pygame.display.set_caption('Connect 4 - Human vs Human')
        
        # First ensure the entire screen is black to clear the blue from menu
        screen.fill(BLACK)
        pygame.display.update()
        
        # Draw initial board
        self.gui.draw_board(self.board.get_board())
        
        # Game state
        game_over = False
        turn = 0  # Player 1 starts
        
        # Main game loop
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Show piece indicator at top when moving mouse
                if event.type == pygame.MOUSEMOTION and not game_over:
                    self.gui.draw_piece_at_mouse(event.pos[0], turn)
                
                # Drop piece on mouse click
                if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                    
                    # Get player move
                    posx = event.pos[0]
                    col = int(posx // SQUARESIZE)
                    
                    if self.board.is_valid_location(col):
                        # Get the player's piece
                        current_player = 1 if turn == 0 else 2
                        
                        # Drop piece and get row where it landed
                        row = self.board.drop_piece(col, current_player)
                        
                        # Animate the piece dropping
                        self.gui.animate_drop(self.board.get_board(), row, col, current_player)
                        
                        # Check for game over
                        if self.board.game_over:
                            if self.board.winner:
                                self.gui.show_winner(self.board.winner)
                            else:
                                self.gui.show_tie()
                            game_over = True
                            pygame.time.wait(3000)
                        else:
                            # Switch turns
                            turn = (turn + 1) % 2
    
    def human_vs_ai(self, ai_module):
        """
        Run a human vs AI game
        
        Parameters:
        - ai_module: module - The AI module to use
        """
        self.board.reset()
        screen = self.gui.screen
        pygame.display.set_caption(f'Connect 4 - Human vs {ai_module.name()}')
        
        # First ensure the entire screen is black to clear the blue from menu
        screen.fill(BLACK)
        pygame.display.update()
        
        # Draw initial board
        self.gui.draw_board(self.board.get_board())
        
        # Game state
        game_over = False
        turn = 0  # Human starts (player 1)
        ai_piece = 2
        human_piece = 1
        
        # Main game loop
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Human's turn
                if turn == 0:
                    # Show piece indicator at top when moving mouse
                    if event.type == pygame.MOUSEMOTION and not game_over:
                        self.gui.draw_piece_at_mouse(event.pos[0], turn)
                    
                    # Drop piece on mouse click
                    if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                        
                        # Get player move
                        posx = event.pos[0]
                        col = int(posx // SQUARESIZE)
                        
                        if self.board.is_valid_location(col):
                            # Drop piece and get row where it landed
                            row = self.board.drop_piece(col, human_piece)
                            
                            # Animate the piece dropping
                            self.gui.animate_drop(self.board.get_board(), row, col, human_piece)
                            
                            # Check for game over
                            if self.board.game_over:
                                if self.board.winner:
                                    self.gui.show_winner(self.board.winner)
                                else:
                                    self.gui.show_tie()
                                game_over = True
                                pygame.time.wait(3000)
                            else:
                                # Switch to AI's turn
                                turn = 1
            
            # AI's turn
            if turn == 1 and not game_over:
                # Add a small delay so the AI doesn't move instantly
                pygame.time.wait(500)
                
                # Get AI's move
                col = ai_module.get_move(self.board.get_board(), ai_piece)
                
                if col is not None and self.board.is_valid_location(col):
                    # Drop piece and get row where it landed
                    row = self.board.drop_piece(col, ai_piece)
                    
                    # Animate the piece dropping
                    self.gui.animate_drop(self.board.get_board(), row, col, ai_piece)
                    
                    # Check for game over
                    if self.board.game_over:
                        if self.board.winner:
                            self.gui.show_winner(self.board.winner)
                        else:
                            self.gui.show_tie()
                        game_over = True
                        pygame.time.wait(3000)
                    else:
                        # Switch to human's turn
                        turn = 0
    
    def ai_vs_ai(self, ai_module1, ai_module2):
        """
        Run an AI vs AI game
        
        Parameters:
        - ai_module1: module - The first AI module
        - ai_module2: module - The second AI module
        """
        self.board.reset()
        screen = self.gui.screen
        pygame.display.set_caption(f'Connect 4 - {ai_module1.name()} vs {ai_module2.name()}')
        
        # First ensure the entire screen is black to clear the blue from menu
        screen.fill(BLACK)
        pygame.display.update()
        
        # Draw initial board
        self.gui.draw_board(self.board.get_board())
        
        # Game state
        game_over = False
        current_ai = 0  # AI 1 starts
        
        # Main game loop
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Add a way to pause/play the AI game
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Wait for another space key press
                        waiting = True
                        while waiting:
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                                    waiting = False
            
            # Add a delay between moves
            pygame.time.wait(1000)
            
            # Current AI's turn
            current_module = ai_module1 if current_ai == 0 else ai_module2
            current_piece = 1 if current_ai == 0 else 2
            
            # Get AI's move
            col = current_module.get_move(self.board.get_board(), current_piece)
            
            if col is not None and self.board.is_valid_location(col):
                # Drop piece and get row where it landed
                row = self.board.drop_piece(col, current_piece)
                
                # Animate the piece dropping
                self.gui.animate_drop(self.board.get_board(), row, col, current_piece)
                
                # Check for game over
                if self.board.game_over:
                    if self.board.winner:
                        self.gui.show_winner(self.board.winner)
                    else:
                        self.gui.show_tie()
                    game_over = True
                    pygame.time.wait(3000)
                else:
                    # Switch to other AI's turn
                    current_ai = (current_ai + 1) % 2
    
    def main_menu(self):
        """
        Display the main menu for game mode selection with AI selection options
        """
        screen = self.gui.screen
        pygame.display.set_caption('Connect 4 - Main Menu')
        
        # Fill the background
        screen.fill(BLUE)
        
        # Font for menu
        font = pygame.font.SysFont("monospace", 36)
        title_font = pygame.font.SysFont("monospace", 48, bold=True)
        
        # Check if we have any AI modules loaded
        ai_available = len(self.ai_modules) > 0
        ai_names = list(self.ai_modules.keys())
        
        # Menu state variables
        show_ai_selection = False
        selecting_for_human = False
        first_ai_selected = None
        current_menu_buttons = []
        current_ai_buttons = []
        
        # Title
        title = title_font.render("Connect 4", 1, BLACK)
        
        # Main menu options
        main_options = [
            ("Human vs Human", lambda: self.human_vs_human()),
            ("Human vs AI", None),  # Will be handled separately
            ("AI vs AI", None),     # Will be handled separately
            ("Exit", lambda: sys.exit())
        ]
        
        # Function to draw main menu
        def draw_main_menu():
            nonlocal current_menu_buttons
            screen.fill(BLUE)
            screen.blit(title, (WIDTH/2 - title.get_width()/2, 30))
            
            buttons = []
            y_offset = 150
            for i, (text, _) in enumerate(main_options):
                text_surface = font.render(text, 1, BLACK)
                button_rect = pygame.Rect(WIDTH/2 - 200, y_offset + i * 80, 400, 60)
                
                # Store button with its function or special handling for AI options
                if text == "Human vs AI":
                    buttons.append((button_rect, "human_vs_ai"))
                elif text == "AI vs AI":
                    buttons.append((button_rect, "ai_vs_ai"))
                else:
                    buttons.append((button_rect, main_options[i][1]))
                
                # Disable AI options if no AI available
                if (text == "Human vs AI" or text == "AI vs AI") and not ai_available:
                    # Gray out buttons
                    pygame.draw.rect(screen, (150, 150, 0), button_rect, border_radius=10)
                else:
                    pygame.draw.rect(screen, YELLOW, button_rect, border_radius=10)
                    
                screen.blit(text_surface, (button_rect.centerx - text_surface.get_width()/2, 
                                         button_rect.centery - text_surface.get_height()/2))
            
            current_menu_buttons = buttons
            pygame.display.update()
        
        # Function to draw AI selection menu
        def draw_ai_selection(title_text):
            nonlocal current_ai_buttons
            screen.fill(BLUE)
            selection_title = title_font.render(title_text, 1, BLACK)
            screen.blit(selection_title, (WIDTH/2 - selection_title.get_width()/2, 30))
            
            ai_buttons = []
            y_offset = 150
            
            # Add a button for each AI
            for i, ai_name in enumerate(ai_names):
                text_surface = font.render(ai_name, 1, BLACK)
                button_rect = pygame.Rect(WIDTH/2 - 200, y_offset + i * 80, 400, 60)
                ai_buttons.append((button_rect, ai_name))
                
                pygame.draw.rect(screen, YELLOW, button_rect, border_radius=10)
                screen.blit(text_surface, (button_rect.centerx - text_surface.get_width()/2, 
                                         button_rect.centery - text_surface.get_height()/2))
            
            # Add back button
            back_text = font.render("Back", 1, BLACK)
            back_rect = pygame.Rect(WIDTH/2 - 200, y_offset + len(ai_names) * 80, 400, 60)
            ai_buttons.append((back_rect, "back"))
            
            pygame.draw.rect(screen, (100, 100, 255), back_rect, border_radius=10)
            screen.blit(back_text, (back_rect.centerx - back_text.get_width()/2, 
                                  back_rect.centery - back_text.get_height()/2))
            
            current_ai_buttons = ai_buttons
            pygame.display.update()
        
        # Initial menu draw
        draw_main_menu()
        
        # Main menu loop
        running = True
        while running:
            # Process all events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    if not show_ai_selection:
                        # Main menu handling
                        for button, action in current_menu_buttons:
                            if button.collidepoint(mouse_pos):
                                if action == "human_vs_ai" and ai_available:
                                    # Show AI selection for human vs AI
                                    show_ai_selection = True
                                    selecting_for_human = True
                                    draw_ai_selection("Select AI Opponent")
                                    break
                                
                                elif action == "ai_vs_ai" and ai_available:
                                    # Show AI selection for AI vs AI
                                    show_ai_selection = True
                                    selecting_for_human = False
                                    first_ai_selected = None
                                    draw_ai_selection("Select First AI")
                                    break
                                
                                elif callable(action):
                                    # Execute the action (e.g., Human vs Human or Exit)
                                    action()
                                    # Redraw the main menu after returning from a game
                                    draw_main_menu()
                                    break
                    
                    else:
                        # AI selection handling
                        button_clicked = False
                        for button, action in current_ai_buttons:
                            if button.collidepoint(mouse_pos):
                                button_clicked = True
                                
                                if action == "back":
                                    if selecting_for_human or first_ai_selected is None:
                                        # Return to main menu
                                        show_ai_selection = False
                                        draw_main_menu()
                                    else:
                                        # Go back to selecting first AI
                                        first_ai_selected = None
                                        draw_ai_selection("Select First AI")
                                
                                elif selecting_for_human:
                                    # Start human vs selected AI
                                    show_ai_selection = False
                                    self.human_vs_ai(self.ai_modules[action])
                                    draw_main_menu()
                                
                                elif first_ai_selected is None:
                                    # Store first AI and move to selecting second AI
                                    first_ai_selected = action
                                    draw_ai_selection("Select Second AI")
                                
                                else:
                                    # Start AI vs AI with selected AIs
                                    show_ai_selection = False
                                    self.ai_vs_ai(
                                        self.ai_modules[first_ai_selected], 
                                        self.ai_modules[action]
                                    )
                                    draw_main_menu()
                                
                                break
            
            # Small delay to prevent high CPU usage
            pygame.time.wait(10)


if __name__ == "__main__":
    game = Game()
    game.main_menu()