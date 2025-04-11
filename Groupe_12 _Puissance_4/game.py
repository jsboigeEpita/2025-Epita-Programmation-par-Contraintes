import numpy as np
import pygame
import sys
import importlib
import os
from board import ConnectFourBoard
from gui import GameGUI, SQUARESIZE, WIDTH, HEIGHT, RADIUS, RED, YELLOW, BLACK, BLUE
import logging
import importlib.util

# Set up logging with lower verbosity
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger('connect4')

class Game:
    def __init__(self):
        pygame.init()
        self.board = ConnectFourBoard()
        self.gui = GameGUI()
        self.ai_modules = self._load_ai_modules()
    
    def _load_ai_modules(self):
        ai_modules = {}
        ai_dir = "ai"
        
        if not os.path.exists(ai_dir):
            logger.error(f"AI directory '{ai_dir}' not found")
            return ai_modules
            
        for file in os.listdir(ai_dir):
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                full_module_path = f"{ai_dir}.{module_name}"
                file_path = os.path.join(ai_dir, file)
                
                try:
                    # Try direct import
                    module = importlib.import_module(full_module_path)
                except ImportError:
                    # Try alternative import
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, file_path)
                        if spec is None:
                            continue
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                    except Exception as e:
                        logger.error(f"Failed to load {module_name}: {e}")
                        continue
                
                # Verify module interface
                if hasattr(module, 'get_move'):
                    ai_name = module.name() if hasattr(module, 'name') else module_name
                    ai_modules[ai_name] = module
        
        logger.info(f"Loaded {len(ai_modules)} AIs: {list(ai_modules.keys())}")
        return ai_modules
    
    def _handle_game_over(self):
        """Common game over handling"""
        if self.board.winner:
            self.gui.show_winner(self.board.winner)
        else:
            self.gui.show_tie()
        pygame.time.wait(3000)
        return True
    
    def human_vs_human(self):
        self.board.reset()
        screen = self.gui.screen
        pygame.display.set_caption('Connect 4 - Human vs Human')
        
        screen.fill(BLACK)
        pygame.display.update()
        self.gui.draw_board(self.board.get_board())
        
        game_over = False
        turn = 0  # Player 1 starts
        
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEMOTION and not game_over:
                    self.gui.draw_piece_at_mouse(event.pos[0], turn)
                
                if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                    col = int(event.pos[0] // SQUARESIZE)
                    
                    if self.board.is_valid_location(col):
                        current_player = 1 if turn == 0 else 2
                        row = self.board.drop_piece(col, current_player)
                        self.gui.animate_drop(self.board.get_board(), row, col, current_player)
                        
                        if self.board.game_over:
                            game_over = self._handle_game_over()
                        else:
                            turn = (turn + 1) % 2
    
    def human_vs_ai(self, ai_module):
        self.board.reset()
        screen = self.gui.screen
        pygame.display.set_caption(f'Connect 4 - Human vs {ai_module.name()}')
        
        screen.fill(BLACK)
        pygame.display.update()
        self.gui.draw_board(self.board.get_board())
        
        game_over = False
        turn = 0  # Human starts (player 1)
        ai_piece = 2
        human_piece = 1
        
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Human's turn
                if turn == 0:
                    if event.type == pygame.MOUSEMOTION and not game_over:
                        self.gui.draw_piece_at_mouse(event.pos[0], turn)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                        col = int(event.pos[0] // SQUARESIZE)
                        
                        if self.board.is_valid_location(col):
                            row = self.board.drop_piece(col, human_piece)
                            self.gui.animate_drop(self.board.get_board(), row, col, human_piece)
                            
                            if self.board.game_over:
                                game_over = self._handle_game_over()
                            else:
                                turn = 1
            
            # AI's turn
            if turn == 1 and not game_over:
                pygame.time.wait(500)  # Small delay for better UX
                
                col = ai_module.get_move(self.board.get_board(), ai_piece)
                if col is not None and self.board.is_valid_location(col):
                    row = self.board.drop_piece(col, ai_piece)
                    self.gui.animate_drop(self.board.get_board(), row, col, ai_piece)
                    
                    if self.board.game_over:
                        game_over = self._handle_game_over()
                    else:
                        turn = 0
    
    def ai_vs_ai(self, ai_module1, ai_module2):
        self.board.reset()
        screen = self.gui.screen
        pygame.display.set_caption(f'Connect 4 - {ai_module1.name()} vs {ai_module2.name()}')
        
        screen.fill(BLACK)
        pygame.display.update()
        self.gui.draw_board(self.board.get_board())
        
        game_over = False
        current_ai = 0  # AI 1 starts
        
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Pause/resume with space bar
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = True
                    while waiting:
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                                waiting = False
            
            pygame.time.wait(1000)  # Delay between AI moves
            
            current_module = ai_module1 if current_ai == 0 else ai_module2
            current_piece = 1 if current_ai == 0 else 2
            
            col = current_module.get_move(self.board.get_board(), current_piece)
            if col is not None and self.board.is_valid_location(col):
                row = self.board.drop_piece(col, current_piece)
                self.gui.animate_drop(self.board.get_board(), row, col, current_piece)
                
                if self.board.game_over:
                    game_over = self._handle_game_over()
                else:
                    current_ai = (current_ai + 1) % 2
    
    def main_menu(self):
        screen = self.gui.screen
        pygame.display.set_caption('Connect 4 - Main Menu')
        
        # Setup constants
        font = pygame.font.SysFont("monospace", 36)
        title_font = pygame.font.SysFont("monospace", 48, bold=True)
        title = title_font.render("Connect 4", 1, BLACK)
        
        # Menu options
        main_options = [
            ("Human vs Human", lambda: self.human_vs_human()),
            ("Human vs AI", "human_vs_ai"),
            ("AI vs AI", "ai_vs_ai"),
            ("Exit", lambda: sys.exit())
        ]
        
        # Menu state
        ai_available = len(self.ai_modules) > 0
        ai_names = list(self.ai_modules.keys())
        show_ai_selection = False
        selecting_for_human = False
        first_ai_selected = None
        current_menu_buttons = []
        current_ai_buttons = []
        
        def draw_main_menu():
            nonlocal current_menu_buttons
            screen.fill(BLUE)
            screen.blit(title, (WIDTH/2 - title.get_width()/2, 30))
            
            buttons = []
            y_offset = 150
            
            for i, (text, action) in enumerate(main_options):
                text_surface = font.render(text, 1, BLACK)
                button_rect = pygame.Rect(WIDTH/2 - 200, y_offset + i * 80, 400, 60)
                buttons.append((button_rect, action))
                
                # Gray out unavailable options
                button_color = (150, 150, 0) if (text in ["Human vs AI", "AI vs AI"] and not ai_available) else YELLOW
                pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
                screen.blit(text_surface, (button_rect.centerx - text_surface.get_width()/2, 
                                         button_rect.centery - text_surface.get_height()/2))
            
            current_menu_buttons = buttons
            pygame.display.update()
        
        def draw_ai_selection(title_text):
            nonlocal current_ai_buttons
            screen.fill(BLUE)
            selection_title = title_font.render(title_text, 1, BLACK)
            screen.blit(selection_title, (WIDTH/2 - selection_title.get_width()/2, 30))
            
            ai_buttons = []
            y_offset = 150
            
            # AI selection buttons
            for i, ai_name in enumerate(ai_names):
                text_surface = font.render(ai_name, 1, BLACK)
                button_rect = pygame.Rect(WIDTH/2 - 150, y_offset + i * 50, 300, 40)
                ai_buttons.append((button_rect, ai_name))
                pygame.draw.rect(screen, YELLOW, button_rect, border_radius=10)
                screen.blit(text_surface, (button_rect.centerx - text_surface.get_width()/2, 
                                         button_rect.centery - text_surface.get_height()/2))
            
            # Back button
            back_text = font.render("Back", 1, BLACK)
            back_rect = pygame.Rect(WIDTH/2 - 150, y_offset + len(ai_names) * 50 + 20, 300, 40)
            ai_buttons.append((back_rect, "back"))
            pygame.draw.rect(screen, (100, 100, 255), back_rect, border_radius=10)
            screen.blit(back_text, (back_rect.centerx - back_text.get_width()/2, 
                                  back_rect.centery - back_text.get_height()/2))
            
            current_ai_buttons = ai_buttons
            pygame.display.update()
        
        # Initial menu draw
        draw_main_menu()
        
        # Main menu loop
        while True:
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
                                # AI selection options
                                if action == "human_vs_ai" and ai_available:
                                    show_ai_selection = True
                                    selecting_for_human = True
                                    draw_ai_selection("Select AI Opponent")
                                
                                elif action == "ai_vs_ai" and ai_available:
                                    show_ai_selection = True
                                    selecting_for_human = False
                                    first_ai_selected = None
                                    draw_ai_selection("Select First AI")
                                
                                # Direct actions
                                elif callable(action):
                                    action()
                                    draw_main_menu()
                    else:
                        # AI selection handling
                        for button, action in current_ai_buttons:
                            if button.collidepoint(mouse_pos):
                                if action == "back":
                                    if selecting_for_human or first_ai_selected is None:
                                        show_ai_selection = False
                                        draw_main_menu()
                                    else:
                                        first_ai_selected = None
                                        draw_ai_selection("Select First AI")
                                
                                elif selecting_for_human:
                                    show_ai_selection = False
                                    self.human_vs_ai(self.ai_modules[action])
                                    draw_main_menu()
                                
                                elif first_ai_selected is None:
                                    first_ai_selected = action
                                    draw_ai_selection("Select Second AI")
                                
                                else:
                                    show_ai_selection = False
                                    self.ai_vs_ai(
                                        self.ai_modules[first_ai_selected], 
                                        self.ai_modules[action]
                                    )
                                    draw_main_menu()
                                break
            
            pygame.time.wait(10)

if __name__ == "__main__":
    game = Game()
    game.main_menu()