from maze.environment import MazeEnvironment
from maze.dynamic_environment import DynamicMazeEnvironment
from maze.game_controller import GameController
from maze.visualizer import MazeVisualizer
import numpy as np  # Make sure numpy is imported for your existing code

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
    """Create a sample maze with dynamic elements"""
    maze = DynamicMazeEnvironment(15, 15)
    
    # Generate a random maze pattern
    maze.generate_maze_pattern(wall_density=0.3)
    
    # Set start positions for two teams
    maze.set_start_positions(1, [(1, 1), (1, 2)])
    maze.set_start_positions(2, [(13, 13), (13, 12)])
    
    # Set goal position in the center
    maze.set_goal_position(7, 7)
    
    # Add dynamic walls
    maze.create_random_dynamic_walls(15)
    
    return maze

def manual_game_test():
    maze = create_sample_maze()
    print("Maze created:")
    print(maze)
    
    # Create game controller
    game = GameController(maze)
    
    team1 = game.add_team(1, "Red")
    team2 = game.add_team(2, "Blue")
    
    # Initialize teams with agents
    game.initialize_teams()
    print("Game initialized:")
    print(game)

def visualized_game():
    # Create a dynamic maze
    maze = create_dynamic_maze()
    print("Dynamic maze created")
    
    # Create game controller
    game = GameController(maze)
    
    # Add teams
    team1 = game.add_team(1, "Red")
    team2 = game.add_team(2, "Blue")
    
    # Initialize teams with agents
    game.initialize_teams()
    
    # Create visualizer
    visualizer = MazeVisualizer(game, cell_size=40)
    
    # Run the visualization and simulation
    print("Starting visualization...")
    visualizer.run_simulation(max_turns=100, delay=0.5)
    
    print("Simulation complete!")
    if game.game_over:
        print(f"Team {game.winning_team} wins!")
    else:
        print("No winner determined.")

if __name__ == "__main__":
    visualized_game()