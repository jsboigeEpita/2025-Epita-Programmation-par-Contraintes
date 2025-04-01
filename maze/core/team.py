from typing import Dict, List, Tuple, Set
from .agent import Agent

class Team:
    def __init__(self, team_id: int, color: str = None, communication_range: int = 3):
        """
        Initialize a team.
        
        Parameters:
        team_id: The team identifier
        color: Color name for visualization
        communication_range: Max distance at which agents can share information
        """
        self.team_id = team_id
        self.agents: Dict[int, Agent] = {}  # agent_id: Agent
        self.color = color or f"Team {team_id}"
        self.communication_range = communication_range
    
    def add_agent(self, agent: Agent):
        """
        Add an agent to the team.
        """
        if agent.team_id == self.team_id:
            self.agents[agent.agent_id] = agent
    
    def remove_agent(self, agent_id: int):
        """
        Remove an agent from the team.
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    def get_agent_positions(self) -> Dict[int, Tuple[int, int]]:
        """
        Get current positions of all agents in the team.
        """
        return {agent_id: (agent.x, agent.y) for agent_id, agent in self.agents.items()}
    
    def get_discovered_tiles(self) -> Set[Tuple[int, int]]:
        """
        Get union of all tiles discovered by the team's agents.
        """
        if not self.agents:
            return set()
        
        all_discovered = set()
        for agent in self.agents.values():
            all_discovered.update(agent.discovered_tiles)
        return all_discovered
    
    def share_vision(self):
        """
        Share vision between agents within communication range of each other.
        Also, prioritize sharing goal information.
        """
        # First, check if any agent has discovered the goal
        goal_discoverers = []
        
        for agent in self.agents.values():
            goal_found = False
            for teammate in self.agents.values():
                if hasattr(teammate, 'discovered_tiles') and hasattr(teammate.discovered_tiles, '__contains__'):
                    # Only check if the agent has the expected attributes and methods
                    if hasattr(teammate, 'maze') and hasattr(teammate.maze, 'goal_position'):
                        if teammate.maze.goal_position in teammate.discovered_tiles:
                            goal_found = True
                            break
            
            if goal_found:
                goal_discoverers.append(agent)
        
        # Group agents by proximity to share vision
        agent_groups = []
        processed_agents = set()
        
        for agent_id, agent in self.agents.items():
            if agent_id in processed_agents:
                continue
                
            # Start a new group with this agent
            current_group = [agent]
            processed_agents.add(agent_id)
            
            # Find all agents within communication range
            for other_id, other_agent in self.agents.items():
                if other_id in processed_agents:
                    continue
                    
                # Calculate Manhattan distance
                distance = abs(agent.x - other_agent.x) + abs(agent.y - other_agent.y)
                
                if distance <= self.communication_range:
                    current_group.append(other_agent)
                    processed_agents.add(other_id)
            
            if len(current_group) > 1:
                agent_groups.append(current_group)
        
        # For each group, share discovered tiles
        for group in agent_groups:
            # Union of all discovered tiles by agents in this group
            all_discovered = set()
            for agent in group:
                all_discovered.update(agent.discovered_tiles)
            
            # Share with all agents in this group
            for agent in group:
                agent.discovered_tiles.update(all_discovered)
        
        # Additionally, prioritize sharing goal information
        # If an agent has found the goal, make sure to share this info with nearby agents
        for goal_agent in goal_discoverers:
            for agent in self.agents.values():
                if agent.agent_id != goal_agent.agent_id:
                    distance = abs(goal_agent.x - agent.x) + abs(goal_agent.y - agent.y)
                    
                    # If within extended communication range, share goal location
                    if distance <= self.communication_range * 1.5:  # Extend range for critical information
                        if hasattr(goal_agent, 'maze') and hasattr(goal_agent.maze, 'goal_position'):
                            agent.discovered_tiles.add(goal_agent.maze.goal_position)
    
    def has_won(self, goal_position: Tuple[int, int]) -> bool:
        """
        Check if all agents in the team have reached the goal.
        """
        if not self.agents:
            return False
        return all(agent.check_goal_reached(goal_position) for agent in self.agents.values())
    
    def __str__(self):
        """
        String representation of the team.
        """
        return f"{self.color} with {len(self.agents)} agents"
