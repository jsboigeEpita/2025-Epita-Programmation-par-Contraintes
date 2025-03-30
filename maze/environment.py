import numpy as np
from typing import List, Tuple, Dict, Set

class MazeEnvironment:
    def __init__(self, width: int, height: int):
        """
        Initialize a maze environment.
        """
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)  # 0: open path, 1: wall
        self.start_positions: Dict[int, List[Tuple[int, int]]] = {}  # Team ID: list of start positions
        self.goal_position: Tuple[int, int] = None
        
    def add_wall(self, x: int, y: int):
        """
        Add a wall at the specified position.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = 1
    
    def add_walls(self, wall_positions: List[Tuple[int, int]]):
        """
        Add multiple walls at the specified positions.
        """
        for x, y in wall_positions:
            self.add_wall(x, y)
    
    def set_start_positions(self, team_id: int, positions: List[Tuple[int, int]]):
        """
        Set start positions for a team.
        """
        valid_positions = []
        for x, y in positions:
            if 0 <= x < self.width and 0 <= y < self.height and self.grid[y, x] == 0:
                valid_positions.append((x, y))
        
        if valid_positions:
            self.start_positions[team_id] = valid_positions
    
    def set_goal_position(self, x: int, y: int):
        """
        Set the goal position.
        """
        if 0 <= x < self.width and 0 <= y < self.height and self.grid[y, x] == 0:
            self.goal_position = (x, y)
    
    def is_valid_move(self, x: int, y: int) -> bool:
        """
        Check if a move to the specified position is valid.
        """
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                self.grid[y, x] == 0)
    
    def get_visible_tiles(self, x: int, y: int, vision_range: int) -> Set[Tuple[int, int]]:
        """
        Get all tiles visible from a position within the vision range.
        """
        visible_tiles = set()
        
        for dx in range(-vision_range, vision_range + 1):
            for dy in range(-vision_range, vision_range + 1):
                # using Manhattan distance
                if abs(dx) + abs(dy) <= vision_range:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        visible_tiles.add((nx, ny))
        
        return visible_tiles
    
    def load_from_file(self, filename: str):
        """
        Load maze configuration from a file.
        """
        pass
    
    def save_to_file(self, filename: str):
        """
        Save the current maze configuration to a file.
        """
        pass
    
    def __str__(self):
        """
        String representation of the maze.
        """
        maze_str = ""
        for y in range(self.height):
            for x in range(self.width):
                if self.goal_position == (x, y):
                    maze_str += "G "
                elif any(positions and (x, y) in positions 
                         for positions in self.start_positions.values()):
                    maze_str += "S "
                elif self.grid[y, x] == 1:
                    maze_str += "# "  # Wall
                else:
                    maze_str += ". "  # Open path
            maze_str += "\n"
        return maze_str
