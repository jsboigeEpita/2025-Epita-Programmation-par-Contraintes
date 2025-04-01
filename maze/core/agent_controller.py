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
        Update all agents on each turn, taking selfishness into account
        """
        if self.game_controller.game_over:
            return
            
        # Process each team's agents
        for team_id, team in self.game_controller.teams.items():
            for agent_id, agent in team.agents.items():
                discovered_tiles = agent.get_discovered_tiles()
                
                if agent.reached_goal:
                    continue  # Skip agents that have reached the goal
                
                # If goal is known and teammates remain, decide whether to help based on selfishness
                if self.maze.goal_position in discovered_tiles and self.agents_reached_goal() < len(team.agents):
                    # Calculate whether to be selfish or helpful based on team's selfishness parameter
                    selfish_choice = random.random() < team.selfishness
                    
                    # If not being selfish, try to find a teammate to help
                    if not selfish_choice:
                        teammate = self.find_closest_teammate(agent, discovered_tiles)
                        if teammate:
                            # Move toward the teammate to share vision
                            move_dir = self.get_move_toward_target(agent, (teammate.x, teammate.y), discovered_tiles)
                            if move_dir:
                                self.game_controller.move_agent(agent_id, team_id, move_dir[0], move_dir[1])
                                continue
                
                # Determine next move
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
            if path and len(path) > 1:
                next_pos = path[1]  # First step is current position, second is next
                return next_pos[0] - agent.x, next_pos[1] - agent.y
        
        # If no path to goal, explore
        return self.explore_strategy(agent, discovered_tiles)
    
    def find_path(self, agent, target_pos, discovered_tiles) -> List[Tuple[int, int]]:
        """
        Find a path from agent position to target position using BFS
        """
        cache_key = (agent.x, agent.y, target_pos[0], target_pos[1])
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
            
        start = (agent.x, agent.y)
        queue = deque([start])
        visited = {start: None}
        
        while queue:
            current = queue.popleft()
            if current == target_pos:
                path = []
                while current is not None:
                    path.append(current)
                    current = visited[current]
                path.reverse()
                self.path_cache[cache_key] = path
                return path
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = current[0] + dx, current[1] + dy
                next_pos = (nx, ny)
                if (next_pos in discovered_tiles and 
                    next_pos not in visited and 
                    self.is_valid_move(nx, ny, agent.team_id)):
                    visited[next_pos] = current
                    queue.append(next_pos)
        
        return []
    
    def is_valid_move(self, x, y, team_id) -> bool:
        """
        Check if a move to position (x,y) is valid for a team
        """
        if not self.maze.is_valid_move(x, y):
            return False
        
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
        possible_moves = []
        unexplored_moves = []
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = agent.x + dx, agent.y + dy
            
            if self.is_valid_move(nx, ny, agent.team_id):
                possible_moves.append((dx, dy))
                
                for vx in range(nx - agent.vision_range, nx + agent.vision_range + 1):
                    for vy in range(ny - agent.vision_range, ny + agent.vision_range + 1):
                        if abs(vx - nx) + abs(vy - ny) <= agent.vision_range:
                            if (vx, vy) not in discovered_tiles:
                                unexplored_moves.append((dx, dy))
                                break
        
        if unexplored_moves:
            return random.choice(unexplored_moves)
        elif possible_moves:
            return random.choice(possible_moves)
        
        return None  
    
    def agents_reached_goal(self) -> int:
        """
        Check the number of agents that have reached the goal
        """
        reached = 0
        for team in self.game_controller.teams.values():
            for agent in team.agents.values():
                if agent.check_goal_reached(self.maze.goal_position):
                    reached += 1
        return reached
    
    def find_closest_teammate(self, agent, discovered_tiles):
        """
        Find the closest teammate that doesn't know about the goal position
        """
        team = self.game_controller.teams[agent.team_id]
        closest_teammate = None
        min_distance = float('inf')
        
        for teammate_id, teammate in team.agents.items():
            # Skip if it's the same agent or if teammate already reached the goal
            if teammate.agent_id == agent.agent_id or teammate.reached_goal:
                continue
            
            # Skip if teammate already knows about the goal
            if self.maze.goal_position in teammate.discovered_tiles:
                continue
                
            # Calculate Manhattan distance
            distance = abs(agent.x - teammate.x) + abs(agent.y - teammate.y)
            
            if distance < min_distance:
                min_distance = distance
                closest_teammate = teammate
        
        return closest_teammate
    
    def get_move_toward_target(self, agent, target_pos, discovered_tiles) -> Optional[Tuple[int, int]]:
        """
        Get the best move to head toward a target position
        """
        # Try to find a path if the target is in discovered territory
        if target_pos in discovered_tiles:
            path = self.find_path(agent, target_pos, discovered_tiles)
            if path and len(path) > 1:
                next_pos = path[1]
                return next_pos[0] - agent.x, next_pos[1] - agent.y
        
        # If no path, move in the general direction
        best_move = None
        min_distance = float('inf')
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = agent.x + dx, agent.y + dy
            
            if self.is_valid_move(nx, ny, agent.team_id):
                # Calculate Manhattan distance to target
                distance = abs(nx - target_pos[0]) + abs(ny - target_pos[1])
                
                if distance < min_distance:
                    min_distance = distance
                    best_move = (dx, dy)
        
        return best_move
    
    def clear_path_cache(self):
        """
        Clear the path cache
        """
        self.path_cache = {}
