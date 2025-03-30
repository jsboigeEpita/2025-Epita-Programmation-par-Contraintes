from typing import Dict, List, Tuple, Set
from .agent import Agent

class Team:
    """
    Represents a team of agents.
    """
    
    def __init__(self, team_id: int, color: str = None):
        """
        Initialize a team.
        """
        self.team_id = team_id
        self.agents: Dict[int, Agent] = {}  # agent_id: Agent
        self.color = color or f"Team {team_id}"
    
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
        Share vision between agents on the same tile.
        """
        # Group agents by position
        agents_by_pos: Dict[Tuple[int, int], List[Agent]] = {}
        for agent in self.agents.values():
            pos = (agent.x, agent.y)
            if pos not in agents_by_pos:
                agents_by_pos[pos] = []
            agents_by_pos[pos].append(agent)
        
        # For each position with multiple agents, share discovered tiles
        for position, agents_at_pos in agents_by_pos.items():
            if len(agents_at_pos) > 1:
                # Union of all discovered tiles by agents at this position
                all_discovered = set()
                for agent in agents_at_pos:
                    all_discovered.update(agent.discovered_tiles)
                
                # Share with all agents at this position
                for agent in agents_at_pos:
                    agent.discovered_tiles.update(all_discovered)
    
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
