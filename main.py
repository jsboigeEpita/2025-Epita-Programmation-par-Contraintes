from maze.environment import MazeEnvironment
from maze.game_controller import GameController

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
    for team_id, team in game.teams.items():
        print(f"Team {team_id} discovered tiles: {team.get_discovered_tiles()}")
    
    print("\nMoving Team 1, Agent 0 down")
    game.move_agent(0, 1, 0, 1)  # Move agent 0 of team 1 down
    
    print("\nMoving Team 2, Agent 2 left")
    game.move_agent(2, 2, -1, 0)  # Move agent 2 of team 2 left

    print("\nMoving Team 1, Agent 0 left") # illegal! 
    game.move_agent(0, 1, -1, 0)  # Move agent 0 of team 1 left
    
    game.update()
    print("\nAfter update:")
    print(game)
    
    for team_id, team in game.teams.items():
        print(f"Team {team_id} discovered tiles: {team.get_discovered_tiles()}")

if __name__ == "__main__":
    manual_game_test()
