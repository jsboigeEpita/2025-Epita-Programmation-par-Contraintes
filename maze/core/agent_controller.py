from typing import Dict, Tuple, List, Set, Optional
import random
import numpy as np
from collections import deque

class AgentController:
    def __init__(self, game_controller):
        """
        Initialize with a reference to the game controller
        """
        self.game_controller = game_controller
        self.maze = game_controller.maze
        self.path_cache = {}
        
    def update(self):
        """
        Update all agents on each turn
        """
        if self.game_controller.game_over:
            return
            
        # Process each team's agents
        for team_id, team in self.game_controller.teams.items():
            discovered_tiles = team.get_discovered_tiles()
            
            for agent_id, agent in team.agents.items():
                if agent.reached_goal:
                    continue  # Skip agents that have reached the goal
                    
                # Determine next move for this agent
                move_dir = self.get_next_move(agent, discovered_tiles)
                
                if move_dir:
                    dx, dy = move_dir
                    self.game_controller.move_agent(agent_id, team_id, dx, dy)
    
    def get_next_move(self, agent, discovered_tiles) -> Optional[Tuple[int, int]]:
        """
        Determine the next move for an agent.
        """
        # If goal is known, try to path to it
        if self.maze.goal_position in discovered_tiles:
            path = self.find_path(agent, self.maze.goal_position, discovered_tiles)
            if path:
                next_pos = path[1]  # First step is current position, second is next
                return next_pos[0] - agent.x, next_pos[1] - agent.y
        
        # If no path to goal, explore undiscovered areas
        return self.explore_strategy(agent, discovered_tiles)
    
    def find_path(self, agent, target_pos, discovered_tiles) -> List[Tuple[int, int]]:
        """
        Find a path from agent position to target position using BFS
        """
        # Check cache first
        cache_key = (agent.x, agent.y, target_pos[0], target_pos[1])
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
            
        # Initialize BFS
        start = (agent.x, agent.y)
        queue = deque([start])
        visited = {start: None}  # Maps position to its predecessor
        
        while queue:
            current = queue.popleft()
            
            # If we've reached the target
            if current == target_pos:
                # Reconstruct path
                path = []
                while current is not None:
                    path.append(current)
                    current = visited[current]
                path.reverse()
                
                # Cache the result
                self.path_cache[cache_key] = path
                return path
            
            # Try all four directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = current[0] + dx, current[1] + dy
                next_pos = (nx, ny)
                
                # Check if the move is valid and the tile is discovered
                if (next_pos in discovered_tiles and 
                    next_pos not in visited and 
                    self.is_valid_move(next_pos[0], next_pos[1], agent.team_id)):
                    visited[next_pos] = current
                    queue.append(next_pos)
        
        # No path found
        return []
    
    def is_valid_move(self, x, y, team_id) -> bool:
        """
        Check if a move to position (x,y) is valid for a team
        """
        # Check maze boundaries and walls
        if not self.maze.is_valid_move(x, y):
            return False
            
        # Check for other agents (can't move to a position occupied by another team)
        for other_team_id, other_team in self.game_controller.teams.items():
            if other_team_id != team_id:
                for other_agent in other_team.agents.values():
                    if other_agent.x == x and other_agent.y == y:
                        return False
                        
        return True
    
    def explore_strategy(self, agent, discovered_tiles) -> Optional[Tuple[int, int]]:
        """
        Strategy for exploring undiscovered areas
        """
        # Priority of moves: unexplored tiles first, then random valid move
        
        # Check all adjacent tiles
        possible_moves = []
        unexplored_moves = []
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = agent.x + dx, agent.y + dy
            
            if self.is_valid_move(nx, ny, agent.team_id):
                possible_moves.append((dx, dy))
                
                # Check if moving there would reveal new tiles
                for vx in range(nx - agent.vision_range, nx + agent.vision_range + 1):
                    for vy in range(ny - agent.vision_range, ny + agent.vision_range + 1):
                        if abs(vx - nx) + abs(vy - ny) <= agent.vision_range:  # Manhattan distance
                            if (vx, vy) not in discovered_tiles:
                                unexplored_moves.append((dx, dy))
                                break
        
        # Prefer moves that lead to unexplored areas
        if unexplored_moves:
            return random.choice(unexplored_moves)
        elif possible_moves:
            return random.choice(possible_moves)
        
        return None  # No valid moves
        
    def clear_path_cache(self):
        """
        Clear the path cache
        """
        self.path_cache = {}
