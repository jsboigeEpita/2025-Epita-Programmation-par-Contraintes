import random
import numpy as np
from typing import List, Tuple, Dict, Set
from .static_maze import MazeEnvironment

class DynamicMazeEnvironment(MazeEnvironment):
    """Extension of MazeEnvironment with dynamic wall capabilities"""
    
    def __init__(self, width: int, height: int):
        """Initialize a dynamic maze environment."""
        super().__init__(width, height)
        self.dynamic_walls = []  # List of walls that can change
        self.change_probability = 0.05  # Probability of a dynamic wall changing per turn
    
    def add_dynamic_wall(self, x: int, y: int):
        """Mark a position as a dynamic wall that can change"""
        if 0 <= x < self.width and 0 <= y < self.height:
            if (x, y) not in self.dynamic_walls:
                self.dynamic_walls.append((x, y))
    
    def add_dynamic_walls(self, positions: List[Tuple[int, int]]):
        """Add multiple dynamic walls"""
        for x, y in positions:
            self.add_dynamic_wall(x, y)
    
    def toggle_wall(self, x: int, y: int):
        """Toggle a wall on or off"""
        if 0 <= x < self.width and 0 <= y < self.height:
            # Don't toggle walls at start or goal positions
            if hasattr(self, 'goal_position') and (x, y) == self.goal_position:
                return
                
            for team_id, positions in self.start_positions.items():
                if (x, y) in positions:
                    return
            
            # Toggle the wall state
            self.grid[y, x] = 1 - self.grid[y, x]
    
    def update_dynamic_walls(self):
        """Update dynamic walls with random changes"""
        for x, y in self.dynamic_walls:
            if random.random() < self.change_probability:
                self.toggle_wall(x, y)
    
    def create_random_dynamic_walls(self, count: int = 10):
        """Add random dynamic walls to the maze"""
        attempts = 0
        added = 0
        
        while added < count and attempts < 100:
            attempts += 1
            x = random.randint(1, self.width-2)  # Avoid border
            y = random.randint(1, self.height-2)  # Avoid border
            
            # Don't add dynamic walls at start or goal positions
            if hasattr(self, 'goal_position') and (x, y) == self.goal_position:
                continue
                
            skip = False
            for team_id, positions in self.start_positions.items():
                if (x, y) in positions:
                    skip = True
                    break
            
            if skip:
                continue
                
            self.add_dynamic_wall(x, y)
            added += 1
    
    def generate_maze_pattern(self, wall_density=0.3):
        """Generate a random maze pattern with the given wall density"""
        # Clear existing walls
        self.grid = np.zeros((self.height, self.width), dtype=int)
        
        # Add border walls
        for i in range(self.width):
            self.add_wall(i, 0)
            self.add_wall(i, self.height-1)
        
        for i in range(self.height):
            self.add_wall(0, i)
            self.add_wall(self.width-1, i)
        
        # Add random internal walls
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                # Check if this position is a start or goal position
                if hasattr(self, 'goal_position') and (x, y) == self.goal_position:
                    continue
            
                skip = False
                for team_id, positions in self.start_positions.items():
                    if (x, y) in positions:
                        skip = True
                        break

                if skip:
                    continue
                if random.random() < wall_density:
                    self.add_wall(x, y)
        
        # Ensure the maze is solvable (simple approach: add some random paths)
        # This doesn't guarantee solvability but increases chances
        for _ in range(int(self.width * self.height * 0.1)):
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)
            self.grid[y, x] = 0  # Clear path
