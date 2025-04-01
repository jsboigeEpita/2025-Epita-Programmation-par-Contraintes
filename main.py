from maze.environments.static_maze import MazeEnvironment
from maze.environments.dynamic_maze import DynamicMazeEnvironment
from maze.core.game_controller import GameController
from maze.visualization.visualizer import MazeVisualizer
import numpy as np
from maze.core.agent_controller import AgentController

def create_sample_maze() -> MazeEnvironment:
    maze = MazeEnvironment(10, 10)
    
    walls = [
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 7), (1, 8),
        (2, 5), (3, 2), (3, 3), (3, 5), (3, 7),
        (4, 1), (4, 5), (4, 7), (5, 3), (5, 7),
        (6, 1), (6, 3), (6, 5), (6, 7), (6, 8),
        (7, 1), (7, 5), (8, 3), (8, 7)
    ]
    maze.add_walls(walls)
    
    maze.set_start_positions(1, [(0, 0), (0, 1)])
    maze.set_start_positions(2, [(9, 0), (9, 1)])
    
    maze.set_goal_position(5, 9)
    
    return maze

def create_dynamic_maze() -> DynamicMazeEnvironment:
    """
    Create a sample maze with dynamic elements
    """
    maze = DynamicMazeEnvironment(15, 15)
    
    # Set start positions for two teams
    maze.set_start_positions(1, [(1, 1), (1, 2)])
    maze.set_start_positions(2, [(13, 13), (13, 12)])
    
    # Set goal position in the center
    maze.set_goal_position(7, 7)
    
    # Generate a random maze pattern
    maze.generate_maze_pattern(wall_density=0.3)
    # Add dynamic walls
    maze.create_random_dynamic_walls(15)
    
    return maze

def run_agent_competition(dynamic=True, max_turns=100, delay=0.2, team1_selfishness=0.0, team2_selfishness=0.0):
    """
    Run a competition between AI-controlled teams of agents
    
    Parameters:
    dynamic: Whether to use a dynamic maze with moving walls
    max_turns: Maximum number of turns before ending simulation
    delay: Time delay between turns (seconds)
    team1_selfishness: Selfishness parameter for team 1 (0.0-1.0)
    team2_selfishness: Selfishness parameter for team 2 (0.0-1.0)
    """
    # Create the maze
    if dynamic:
        maze = create_dynamic_maze()
        print("Dynamic maze created")
    else:
        maze = create_sample_maze()
        print("Static maze created")
    
    # Create game controller
    game = GameController(maze)
    
    # Add teams with selfishness parameters
    team1 = game.add_team(1, "Red", selfishness=team1_selfishness)
    team2 = game.add_team(2, "Blue", selfishness=team2_selfishness)
    
    # Initialize teams with agents
    game.initialize_teams()
    
    # Create the agent controller
    agent_controller = AgentController(game)
    
    # Create visualizer
    visualizer = MazeVisualizer(game, cell_size=40)
    
    # Display team selfishness information
    print(f"Team 1 (Red) selfishness: {team1_selfishness:.2f}")
    print(f"Team 2 (Blue) selfishness: {team2_selfishness:.2f}")
    
    # Run the visualization and simulation with AI control
    print("Starting AI competition...")
    run_ai_simulation(visualizer, agent_controller, max_turns, delay)
    
    print("Simulation complete!")
    if game.game_over:
        print(f"Team {game.winning_team} wins!")
    else:
        print("No winner determined.")

def run_ai_simulation(visualizer, agent_controller, max_turns=100, delay=0.2):
    """
    Run the simulation with AI controlling the agents
    """
    import pygame
    import time
    
    game = visualizer.game_controller
    clock = pygame.time.Clock()
    running = True
    
    while running and game.current_turn < max_turns and not game.game_over:
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update game state
        if not game.game_over:
            # First, have AI determine agent moves
            agent_controller.update()
            
            # Then update the game state
            game.update()
            
            # If maze is dynamic, clear path cache
            if hasattr(game.maze, 'update_dynamic_walls'):
                agent_controller.clear_path_cache()
        
        # Update animation variables
        visualizer.update_animation()
        
        # Draw everything
        visualizer.draw_maze()
        visualizer.draw_vision_radius()
        visualizer.draw_agents()
        visualizer.draw_game_info()
        
        # Draw selfishness info for each team
        font = pygame.font.SysFont('Arial', 16)
        for i, team_id in enumerate(game.teams.keys()):
            team = game.teams[team_id]
            team_color = visualizer.TEAM_COLORS.get(team_id, (255, 255, 255))
            selfishness_text = f"Team {team_id} selfishness: {team.selfishness:.2f}"
            text_surface = font.render(selfishness_text, True, team_color)
            visualizer.screen.blit(text_surface, (10, visualizer.height - 60 + i*20))
        
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
        visualizer.draw_maze()
        visualizer.draw_vision_radius()
        visualizer.draw_agents()
        visualizer.draw_game_info()
        
        # Draw selfishness info for each team
        font = pygame.font.SysFont('Arial', 16)
        for i, team_id in enumerate(game.teams.keys()):
            team = game.teams[team_id]
            team_color = visualizer.TEAM_COLORS.get(team_id, (255, 255, 255))
            selfishness_text = f"Team {team_id} selfishness: {team.selfishness:.2f}"
            text_surface = font.render(selfishness_text, True, team_color)
            visualizer.screen.blit(text_surface, (10, visualizer.height - 60 + i*20))
        
        # Draw "Simulation Complete" message
        font = pygame.font.SysFont('Arial', 24)
        
        if game.game_over:
            winner_color = visualizer.TEAM_COLORS.get(game.winning_team, (255, 255, 255))
            end_text = f"Team {game.winning_team} wins! Press ESC to exit."
            text_surface = font.render(end_text, True, winner_color)
        else:
            end_text = "Simulation Complete! No winner. Press ESC to exit."
            text_surface = font.render(end_text, True, (255, 255, 255))
            
        text_rect = text_surface.get_rect(center=(visualizer.width // 2, visualizer.height - 30))
        visualizer.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    # Run a competition with autonomous agents
    run_agent_competition(
        dynamic=True, 
        max_turns=100, 
        delay=0.5,
        team1_selfishness=0.0,
        team2_selfishness=1
    )
