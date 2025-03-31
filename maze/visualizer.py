import pygame
import random
import time
import numpy as np

class MazeVisualizer:
    # Colors
    BACKGROUND = (50, 50, 50)
    PATH = (200, 200, 200)
    WALL = (20, 20, 50)
    GOAL = (0, 255, 0)
    START = (0, 0, 255)
    FOG = (30, 30, 30, 180)  # Semi-transparent for fog of war
    GRID_LINE = (100, 100, 100)
    
    # Team colors
    TEAM_COLORS = {
        1: (255, 50, 50),   # Red team
        2: (50, 50, 255),   # Blue team
        3: (255, 255, 0),   # Yellow team
        4: (0, 255, 255)    # Cyan team
    }
    
    def __init__(self, game_controller, cell_size=50):
        """Initialize the visualizer with the game controller"""
        self.game_controller = game_controller
        self.maze = game_controller.maze
        self.cell_size = cell_size
        
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Dynamic Maze Simulation")
        
        # Calculate window size
        self.width = self.maze.width * self.cell_size
        self.height = self.maze.height * self.cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # Font for text
        self.font = pygame.font.SysFont('Arial', 16)
        
        # Animation variables
        self.animation_step = 0
        
    def draw_maze(self):
        """Draw the current state of the maze"""
        self.screen.fill(self.BACKGROUND)
        
        # Draw grid and walls
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                rect = pygame.Rect(
                    x * self.cell_size, 
                    y * self.cell_size,
                    self.cell_size, 
                    self.cell_size
                )
                
                # Draw the cell background
                if self.maze.grid[y, x] == 1:  # Wall
                    pygame.draw.rect(self.screen, self.WALL, rect)
                else:  # Path
                    pygame.draw.rect(self.screen, self.PATH, rect)
                
                # Draw grid lines
                pygame.draw.rect(self.screen, self.GRID_LINE, rect, 1)
        
        # Draw goal position
        if hasattr(self.maze, 'goal_position') and self.maze.goal_position:
            x, y = self.maze.goal_position
            goal_rect = pygame.Rect(
                x * self.cell_size, 
                y * self.cell_size,
                self.cell_size, 
                self.cell_size
            )
            pygame.draw.rect(self.screen, self.GOAL, goal_rect)
            
            # Add a pulsing effect to the goal
            pulse_radius = int(self.cell_size * 0.6 + self.animation_step * 0.2)
            pygame.draw.circle(
                self.screen,
                self.GOAL, 
                (x * self.cell_size + self.cell_size // 2, 
                 y * self.cell_size + self.cell_size // 2),
                pulse_radius,
                3  # circle width
            )
        
        # Draw start positions
        if hasattr(self.maze, 'start_positions'):
            for team_id, positions in self.maze.start_positions.items():
                for pos in positions:
                    if isinstance(pos, tuple) and len(pos) == 2:
                        x, y = pos
                        start_rect = pygame.Rect(
                            x * self.cell_size, 
                            y * self.cell_size,
                            self.cell_size, 
                            self.cell_size
                        )
                        team_color = self.TEAM_COLORS.get(team_id, self.START)
                        lighter_color = tuple(min(255, c + 50) for c in team_color)
                        pygame.draw.rect(self.screen, lighter_color, start_rect, 2)
        
        # Draw fog of war - overlay all undiscovered tiles with fog
        if self.game_controller.teams:
            all_discovered = set()
            for team in self.game_controller.teams.values():
                all_discovered.update(team.get_discovered_tiles())
            
            fog_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            fog_surface.fill((30, 30, 30, 180))  # semi-transparent dark color
            
            # Clear fog from discovered areas
            for x, y in all_discovered:
                if 0 <= x < self.maze.width and 0 <= y < self.maze.height:
                    rect = pygame.Rect(
                        x * self.cell_size, 
                        y * self.cell_size,
                        self.cell_size, 
                        self.cell_size
                    )
                    pygame.draw.rect(fog_surface, (0, 0, 0, 0), rect)
                    
            self.screen.blit(fog_surface, (0, 0))
    
    def draw_agents(self):
        """Draw all agents from all teams"""
        for team_id, team in self.game_controller.teams.items():
            team_color = self.TEAM_COLORS.get(team_id, (255, 255, 255))
            
            for agent_id, agent in team.agents.items():
                # Draw agent as a circle
                center_x = agent.x * self.cell_size + self.cell_size // 2
                center_y = agent.y * self.cell_size + self.cell_size // 2
                radius = int(self.cell_size * 0.35)
                
                # Draw a shadow
                shadow_offset = 3
                pygame.draw.circle(
                    self.screen,
                    (30, 30, 30),
                    (center_x + shadow_offset, center_y + shadow_offset),
                    radius
                )
                
                # Draw the agent
                pygame.draw.circle(self.screen, team_color, (center_x, center_y), radius)
                
                # Draw agent ID
                text_surface = self.font.render(str(agent_id), True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(center_x, center_y))
                self.screen.blit(text_surface, text_rect)
    
    def draw_vision_radius(self):
        """Draw the vision radius around each agent"""
        for team_id, team in self.game_controller.teams.items():
            team_color = self.TEAM_COLORS.get(team_id, (255, 255, 255))
            vision_color = (*team_color[:3], 70)  # Semi-transparent
            
            for agent_id, agent in team.agents.items():
                center_x = agent.x * self.cell_size + self.cell_size // 2
                center_y = agent.y * self.cell_size + self.cell_size // 2
                vision_radius = agent.vision_range * self.cell_size
                
                # Draw vision circle
                vision_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.circle(
                    vision_surface,
                    vision_color,
                    (center_x, center_y),
                    vision_radius
                )
                self.screen.blit(vision_surface, (0, 0))
    
    def draw_game_info(self):
        """Draw game information"""
        # Draw turn number
        turn_text = f"Turn: {self.game_controller.current_turn}"
        text_surface = self.font.render(turn_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))
        
        # Draw game status
        if self.game_controller.game_over:
            winner = f"Team {self.game_controller.winning_team} wins!"
            text_surface = self.font.render(winner, True, (255, 255, 0))
            text_rect = text_surface.get_rect(center=(self.width // 2, 20))
            self.screen.blit(text_surface, text_rect)
    
    def update_animation(self):
        """Update animation variables"""
        self.animation_step = (self.animation_step + 1) % 20
    
    def run_simulation(self, max_turns=1000, delay=0.2):
        """Run the automated simulation"""
        clock = pygame.time.Clock()
        running = True
        
        while running and self.game_controller.current_turn < max_turns and not self.game_controller.game_over:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Update game state (automated)
            if not self.game_controller.game_over:
                self.game_controller.update()
            
            # Update animation variables
            self.update_animation()
            
            # Draw everything
            self.draw_maze()
            self.draw_vision_radius()
            self.draw_agents()
            self.draw_game_info()
            
            # Update the display
            pygame.display.flip()
            
            # Add delay to make simulation visible
            time.sleep(delay)
            
            # Cap the frame rate
            clock.tick(60)
        
        # If simulation ended but window is still open, keep displaying final state
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Draw final state
            self.draw_maze()
            self.draw_vision_radius()
            self.draw_agents()
            self.draw_game_info()
            
            # Draw "Simulation Complete" message
            font = pygame.font.SysFont('Arial', 24)
            end_text = "Simulation Complete! Press ESC to exit."
            text_surface = font.render(end_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.width // 2, self.height - 30))
            self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()