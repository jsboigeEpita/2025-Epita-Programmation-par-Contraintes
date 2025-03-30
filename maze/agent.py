from typing import Tuple, Set, Dict, List

class Agent:
    """
    Represents an individual agent in the maze.
    """
    
    def __init__(self, agent_id: int, team_id: int, x: int, y: int, vision_range: int = 3):
        """
        Initialize an agent.
        """
        self.agent_id = agent_id
        self.team_id = team_id
        self.x = x
        self.y = y
        self.vision_range = vision_range
        self.discovered_tiles: Set[Tuple[int, int]] = set()
        self.reached_goal = False
    
    def move(self, dx: int, dy: int) -> Tuple[int, int]:
        """
        Get the new position after moving by the specified delta. Does not update the agent's position.
        """
        return self.x + dx, self.y + dy
    
    def update_position(self, x: int, y: int):
        """
        Update the agent's position.
        """
        self.x, self.y = x, y
    
    def update_discovered_tiles(self, visible_tiles: Set[Tuple[int, int]]):
        """
        Update the set of tiles discovered by this agent.
        """
        self.discovered_tiles.update(visible_tiles)
    
    def check_goal_reached(self, goal_position: Tuple[int, int]):
        """
        Check if the agent has reached the goal position.
        """
        if (self.x, self.y) == goal_position:
            self.reached_goal = True
        return self.reached_goal
    
    def __str__(self):
        """
        String representation of the agent.
        """
        return f"Agent {self.agent_id} (Team {self.team_id}) at position ({self.x}, {self.y})"
