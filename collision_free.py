from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional, Any
import heapq
import itertools
import copy

@dataclass
class Robot:
    id: int
    speed: float  # Units per time
    current_location: Tuple[int, int]  # (x, y) coordinates

@dataclass                                                                          
class Goal:
    id: int
    location: Tuple[int, int]  # (x, y) coordinates

class PathFinder:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        self.distance_cache = {}  # Cache for path distances
        
    def set_obstacle(self, x: int, y: int):
        """Mark a cell as an obstacle"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = '#'
            
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is valid (within bounds and not an obstacle)"""
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                self.grid[y][x] != '#')
    
    def get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring positions (4-directional movement)"""
        x, y = position
        neighbors = []
        
        # Check all four directions (up, right, down, left)
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny):
                neighbors.append((nx, ny))
                
        return neighbors
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Find a path from start to goal using A* algorithm"""
        if not self.is_valid_position(*start) or not self.is_valid_position(*goal):
            return None
            
        # Check cache first
        cache_key = (start, goal)
        if cache_key in self.distance_cache:
            return self.distance_cache[cache_key]['path']
            
        # Priority queue for open set
        open_set = []
        # Start with the start position
        heapq.heappush(open_set, start)
        
        # For each node, which node it came from
        came_from = {}
        
        # For each node, the cost of getting from start to that node
        g_score = {start: 0}
        
        # Set of positions in the open set
        open_set_hash = {start}
        
        while open_set:
            # Get the position
            current = heapq.heappop(open_set)
            open_set_hash.remove(current)
            
            # If we've reached the goal, reconstruct the path
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                
                # Cache the result
                self.distance_cache[cache_key] = {
                    'path': path,
                    'distance': len(path) - 1
                }
                
                return path
            
            # Check all neighbors
            for neighbor in self.get_neighbors(current):
                # Distance from start to neighbor through current
                tentative_g_score = g_score[current] + 1
                
                # If we found a better path to neighbor
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # Update our path
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, neighbor)
                        open_set_hash.add(neighbor)
        
        # No path found
        self.distance_cache[cache_key] = {'path': None, 'distance': float('inf')}
        return None
    
    def find_optimal_goal_assignment(self, robots: List[Robot], goals: List[Goal]) -> Dict[int, List[Tuple[int, List[Tuple[int, int]]]]]:
        """
        Find the optimal assignment of goals to robots to minimize total time
        This solution is based on the Multiple Travelling Salesman Problem
        Returns: Dictionary mapping robot ID to list of (goal_id, path) tuples
        """
        # Make a copy of robots so we can update their positions during calculation
        robots_copy = [copy.deepcopy(robot) for robot in robots]
        
        # Precompute all possible paths and distances between robots and goals
        # and between goals themselves
        distance_matrix = {}
        path_matrix = {}
        
        # Compute distances from each robot to each goal
        for robot in robots_copy:
            robot_loc = robot.current_location
            for goal in goals:
                goal_loc = goal.location
                path = self.find_path(robot_loc, goal_loc)
                if path:
                    distance = len(path) - 1
                    distance_matrix[(robot.id, goal.id)] = distance / robot.speed
                    path_matrix[(robot.id, goal.id)] = path
                else:
                    distance_matrix[(robot.id, goal.id)] = float('inf')
                    path_matrix[(robot.id, goal.id)] = None
        
        # Compute distances between all goals
        for goal1 in goals:
            for goal2 in goals:
                if goal1.id != goal2.id:
                    path = self.find_path(goal1.location, goal2.location)
                    if path:
                        distance = len(path) - 1
                        distance_matrix[(goal1.id, goal2.id)] = distance
                        path_matrix[(goal1.id, goal2.id)] = path
                    else:
                        distance_matrix[(goal1.id, goal2.id)] = float('inf')
                        path_matrix[(goal1.id, goal2.id)] = None
        
        # Strategy: Try different distributions of goals to robots and pick the best
        best_assignment = None
        best_max_time = float('inf')
        
        # Generate all possible ways to assign goals to robots
        goal_ids = [goal.id for goal in goals]
        
        # Generate all possible partitions of goals among robots
        for partition in self._generate_partitions(goal_ids, len(robots_copy)):
            # Skip partitions that leave robots without goals if we have enough robots
            if len(robots_copy) <= len(goals) and any(not part for part in partition):
                continue
            
            # Map each partition subset to a robot (try all permutations)
            for robot_assignment in itertools.permutations(range(len(partition)), len(partition)):
                # Calculate the time for each robot to complete its assigned goals
                robot_times = []
                robot_paths = []
                
                for robot_idx, goals_subset_idx in enumerate(robot_assignment):
                    goals_subset = partition[goals_subset_idx]
                    
                    if not goals_subset:  # No goals for this robot
                        robot_times.append(0)
                        robot_paths.append([])
                        continue
                    
                    robot = robots_copy[robot_idx]
                    
                    # Try all possible orderings of goals for this robot
                    best_time_for_robot = float('inf')
                    best_paths_for_robot = []
                    
                    for goal_order in itertools.permutations(goals_subset):
                        # Start at robot's position
                        current_pos = robot.current_location
                        total_time = 0
                        paths_for_ordering = []
                        
                        for goal_id in goal_order:
                            # Get the goal location
                            goal_loc = next(g.location for g in goals if g.id == goal_id)
                            
                            # Find the path from current position to goal
                            path = self.find_path(current_pos, goal_loc)
                            
                            if not path:
                                # No path found, this ordering is invalid
                                total_time = float('inf')
                                break
                            
                            # Calculate time to travel this path, adjusted for robot speed
                            time_to_goal = (len(path) - 1) / robot.speed
                            total_time += time_to_goal
                            
                            # Store the goal and its path
                            paths_for_ordering.append((goal_id, path))
                            
                            # Update current position to the goal's position
                            current_pos = goal_loc
                        
                        # Update best time and paths for this robot if better
                        if total_time < best_time_for_robot:
                            best_time_for_robot = total_time
                            best_paths_for_robot = paths_for_ordering
                    
                    robot_times.append(best_time_for_robot)
                    robot_paths.append(best_paths_for_robot)
                
                # The overall time is the maximum time any robot takes
                max_time = max(robot_times)
                
                # Update best assignment if better
                if max_time < best_max_time:
                    best_max_time = max_time
                    
                    # Construct the assignment
                    best_assignment = {}
                    for robot_idx, paths in enumerate(robot_paths):
                        robot_id = robots_copy[robot_idx].id
                        best_assignment[robot_id] = paths
        
        return best_assignment
    
    def _generate_partitions(self, items, bins):
        """Generate all possible ways to partition items into exactly bins bins"""
        if not items:
            yield [[] for _ in range(bins)]
            return
            
        # Try placing the first item in each bin
        first, rest = items[0], items[1:]
        
        for i in range(bins):
            for parts in self._generate_partitions(rest, bins):
                parts[i].append(first)
                yield copy.deepcopy(parts)
    
    def check_collision(self, robot1_path: List[Tuple[int, int]], robot1_speed: float,
                      robot2_path: List[Tuple[int, int]], robot2_speed: float) -> bool:
        """
        Check if two robot paths would result in a collision
        Returns True if collision detected, False otherwise
        """
        if not robot1_path or not robot2_path:
            return False
            
        # Calculate the position of each robot at each time step
        robot1_positions = {}
        robot2_positions = {}
        
        # Calculate positions at each time step
        for i in range(len(robot1_path) - 1):
            # Time to reach this position
            time = i / robot1_speed
            robot1_positions[time] = robot1_path[i]
            
        for i in range(len(robot2_path) - 1):
            # Time to reach this position
            time = i / robot2_speed
            robot2_positions[time] = robot2_path[i]
            
        # Add final positions (robots stay at their goals)
        robot1_final_time = (len(robot1_path) - 1) / robot1_speed
        robot1_final_pos = robot1_path[-1]
        
        robot2_final_time = (len(robot2_path) - 1) / robot2_speed
        robot2_final_pos = robot2_path[-1]
        
        # Check for collisions at each time step
        all_times = sorted(set(list(robot1_positions.keys()) + list(robot2_positions.keys())))
        
        for time in all_times:
            # Get robot 1 position at this time
            r1_pos = None
            if time in robot1_positions:
                r1_pos = robot1_positions[time]
            elif time > robot1_final_time:
                r1_pos = robot1_final_pos
            else:
                # Interpolate position
                prev_time = max([t for t in robot1_positions.keys() if t < time], default=0)
                next_time = min([t for t in robot1_positions.keys() if t > time], default=robot1_final_time)
                
                if prev_time in robot1_positions and next_time in robot1_positions:
                    # Simple linear interpolation
                    progress = (time - prev_time) / (next_time - prev_time)
                    prev_pos = robot1_positions[prev_time]
                    next_pos = robot1_positions[next_time]
                    
                    # Interpolate x and y
                    x = int(prev_pos[0] + progress * (next_pos[0] - prev_pos[0]))
                    y = int(prev_pos[1] + progress * (next_pos[1] - prev_pos[1]))
                    r1_pos = (x, y)
            
            # Get robot 2 position at this time
            r2_pos = None
            if time in robot2_positions:
                r2_pos = robot2_positions[time]
            elif time > robot2_final_time:
                r2_pos = robot2_final_pos
            else:
                # Interpolate position
                prev_time = max([t for t in robot2_positions.keys() if t < time], default=0)
                next_time = min([t for t in robot2_positions.keys() if t > time], default=robot2_final_time)
                
                if prev_time in robot2_positions and next_time in robot2_positions:
                    # Simple linear interpolation
                    progress = (time - prev_time) / (next_time - prev_time)
                    prev_pos = robot2_positions[prev_time]
                    next_pos = robot2_positions[next_time]
                    
                    # Interpolate x and y
                    x = int(prev_pos[0] + progress * (next_pos[0] - prev_pos[0]))
                    y = int(prev_pos[1] + progress * (next_pos[1] - prev_pos[1]))
                    r2_pos = (x, y)
            
            # Check for collision
            if r1_pos and r2_pos and r1_pos == r2_pos:
                return True
                
        return False
    
    def resolve_collision(self, 
                           robot1_path: List[Tuple[int, int]], 
                           robot1_speed: float,
                           robot2_path: List[Tuple[int, int]], 
                           robot2_speed: float) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Resolve a collision between two robots by delaying one robot
        Returns modified paths for both robots
        """
        # Strategy 1: Delay the start of robot2
        path1 = robot1_path.copy()
        
        # Calculate how long robot1 takes to complete its path
        robot1_time = (len(robot1_path) - 1) / robot1_speed
        
        # Create a new path for robot2 that waits at the start until robot1 is done
        path2 = robot2_path.copy()
        
        # Check if this resolves the collision
        if not self.check_collision(path1, robot1_speed, path2, robot2_speed):
            return path1, path2
            
        # If still collision, try alternating wait times
        max_wait = 10  # Maximum wait steps to try
        
        for wait_steps in range(1, max_wait + 1):
            # Try making robot2 wait
            path2 = [robot2_path[0]] * wait_steps + robot2_path
            
            if not self.check_collision(path1, robot1_speed, path2, robot2_speed):
                return path1, path2
                
            # Try making robot1 wait
            path1 = [robot1_path[0]] * wait_steps + robot1_path
            path2 = robot2_path.copy()  # Reset path2
            
            if not self.check_collision(path1, robot1_speed, path2, robot2_speed):
                return path1, path2
                
        # If all else fails, make robot2 wait until robot1 completes
        # This is a guaranteed solution but may not be optimal
        wait_time = robot1_time
        wait_steps = int(wait_time * robot2_speed) + 1
        path2 = [robot2_path[0]] * wait_steps + robot2_path
        
        return path1, path2
            
    def find_collision_free_paths(self, robots: List[Robot], assignment: Dict[int, List[Tuple[int, List[Tuple[int, int]]]]]) -> Dict[int, List[Tuple[int, List[Tuple[int, int]]]]]:
        """
        Modify paths to avoid collisions between robots
        Returns updated assignment with collision-free paths
        """
        # Make a deep copy of the assignment to modify
        new_assignment = copy.deepcopy(assignment)
        
        # Create a map of robot ID to robot
        robot_map = {robot.id: robot for robot in robots}
        
        # Check all pairs of robots for collisions
        robot_ids = list(new_assignment.keys())
        
        for i in range(len(robot_ids)):
            robot1_id = robot_ids[i]
            robot1_paths = new_assignment[robot1_id]
            
            for j in range(i + 1, len(robot_ids)):
                robot2_id = robot_ids[j]
                robot2_paths = new_assignment[robot2_id]
                
                # Skip if either robot has no paths
                if not robot1_paths or not robot2_paths:
                    continue
                
                # Concatenate all paths for each robot
                robot1_full_path = []
                robot1_speed = robot_map[robot1_id].speed
                
                robot2_full_path = []
                robot2_speed = robot_map[robot2_id].speed
                
                # Build full paths for each robot
                for _, path in robot1_paths:
                    if path:
                        # Skip the first point if not the first path segment
                        if robot1_full_path:
                            robot1_full_path.extend(path[1:])
                        else:
                            robot1_full_path.extend(path)
                
                for _, path in robot2_paths:
                    if path:
                        # Skip the first point if not the first path segment
                        if robot2_full_path:
                            robot2_full_path.extend(path[1:])
                        else:
                            robot2_full_path.extend(path)
                
                # Check for collision
                if self.check_collision(robot1_full_path, robot1_speed, robot2_full_path, robot2_speed):
                    # Resolve collision
                    new_path1, new_path2 = self.resolve_collision(
                        robot1_full_path, robot1_speed,
                        robot2_full_path, robot2_speed
                    )
                    
                    # Split the new paths back into segments for each goal
                    self._update_robot_paths(new_assignment, robot1_id, robot1_paths, new_path1)
                    self._update_robot_paths(new_assignment, robot2_id, robot2_paths, new_path2)
        
        return new_assignment
    
    def _update_robot_paths(self, assignment: Dict[int, List[Tuple[int, List[Tuple[int, int]]]]], 
                           robot_id: int, original_paths: List[Tuple[int, List[Tuple[int, int]]]], 
                           new_full_path: List[Tuple[int, int]]) -> None:
        """
        Update the paths for a robot in the assignment dictionary
        """
        if not original_paths or not new_full_path:
            return
            
        new_paths = []
        path_index = 0
        
        for goal_id, original_path in original_paths:
            path_length = len(original_path)
            
            # Extract the corresponding segment from the new full path
            if path_index + path_length <= len(new_full_path):
                new_segment = new_full_path[path_index:path_index + path_length]
                path_index += path_length - 1  # Subtract 1 to account for overlap
                new_paths.append((goal_id, new_segment))
            else:
                # If we've run out of path, use the last segment
                new_paths.append((goal_id, original_path))
        
        # Update the assignment
        assignment[robot_id] = new_paths
        
    def update_robot_positions(self, robots: List[Robot], goals: List[Goal], assignment: Dict[int, List[Tuple[int, List[Tuple[int, int]]]]]) -> None:
        """Update robot positions based on their assigned goals"""
        # Get a mapping of goal ID to location
        goal_locations = {goal.id: goal.location for goal in goals}
        
        for robot in robots:
            robot_paths = assignment.get(robot.id, [])
            
            # If the robot has goals assigned, update its position to the last goal
            if robot_paths:
                last_goal_id = robot_paths[-1][0]  # Get the ID of the last goal
                robot.current_location = goal_locations[last_goal_id]  # Update the robot's position
    
    def execute_assignments(self, robots: List[Robot], goals: List[Goal], assignment: Dict[int, List[Tuple[int, List[Tuple[int, int]]]]]) -> Dict[int, List[Dict[str, Any]]]:
        """
        Execute the assigned paths for all robots, returning a detailed execution plan
        Returns: Dictionary mapping robot ID to execution steps
        """
        # Get a mapping of goal ID to location
        goal_locations = {goal.id: goal.location for goal in goals}
        
        execution_plan = {}
        
        for robot in robots:
            robot_id = robot.id
            robot_paths = assignment.get(robot_id, [])
            robot_plan = []
            
            for goal_id, path in robot_paths:
                # Calculate the time to reach this goal
                time_to_goal = (len(path) - 1) / robot.speed
                
                # Add to the plan
                robot_plan.append({
                    'goal_id': goal_id,
                    'goal_location': goal_locations[goal_id],
                    'path': path,
                    'time': time_to_goal
                })
            
            # Add this robot's plan to the overall execution plan
            execution_plan[robot_id] = robot_plan
            
            # Update the robot's position to its final goal
            if robot_paths:
                last_goal_id = robot_paths[-1][0]
                robot.current_location = goal_locations[last_goal_id]
        
        return execution_plan
    
    def visualize_assignment(self, robots: List[Robot], goals: List[Goal], assignment: Dict[int, List[Tuple[int, List[Tuple[int, int]]]]]) -> str:
        """Visualize the grid with all robots, goals, and paths"""
        # Create a copy of the grid for visualization
        vis_grid = [row[:] for row in self.grid]
        
        # Create a color map for visualization (using ASCII characters)
        color_map = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        
        # Mark all robots
        for i, robot in enumerate(robots):
            x, y = robot.current_location
            robot_symbol = color_map[i % len(color_map)]
            vis_grid[y][x] = f'R{robot_symbol}'
        
        # Mark all goals
        for goal in goals:
            x, y = goal.location
            vis_grid[y][x] = f'G{goal.id}'
        
        # Dictionary to keep track of path symbols for each robot
        path_symbols = {}
        
        # Mark the paths
        for i, robot in enumerate(robots):
            robot_symbol = color_map[i % len(color_map)]
            path_symbols[robot.id] = robot_symbol
            
            # Get the paths for this robot
            paths = assignment.get(robot.id, [])
            
            if not paths:
                continue
            
            for _, path in paths:
                if path:
                    # Mark the path (skip start position)
                    for j, (x, y) in enumerate(path):
                        # Skip first position (already marked as robot or previous goal)
                        if j == 0:
                            continue
                        
                        # Don't overwrite robots or goals
                        if vis_grid[y][x] == ' ':
                            vis_grid[y][x] = robot_symbol
        
        # Convert the grid to a string
        result = ""
        for row in vis_grid:
            line = ""
            for cell in row:
                if len(cell) == 1:
                    line += f' {cell} '
                else:
                    line += f'{cell} '
            result += '|' + line + '|\n'
        
        return result

# Example usage
def example_collision_avoidance():
    # Create a 20x20 grid
    width, height = 10, 10
    pathfinder = PathFinder(width, height)
    
    # Create multiple robots with different speeds
    robots = [
        Robot(id=1, speed=1.0, current_location=(0, 0)),
        Robot(id=2, speed=1.5, current_location=(9, 0)),
        Robot(id=3, speed=0.8, current_location=(0, 9))
    ]
    
    # Create multiple goals
    goals = [
        Goal(id=1, location=(4, 9)),
        Goal(id=2, location=(8, 7)),
        Goal(id=3, location=(0, 7)),
        Goal(id=4, location=(5, 2)),
        Goal(id=5, location=(1, 3)),
        Goal(id=6, location=(6, 4)),
        Goal(id=7, location=(9, 3))
    ]
    
    # Find the optimal assignment of goals to robots
    print("Finding optimal goal assignment...")
    assignment = pathfinder.find_optimal_goal_assignment(robots, goals)
    
    # Print the assignment
    print("\nInitial Goal Assignment:")
    for robot_id, paths in assignment.items():
        print(f"Robot {robot_id}:")
        if not paths:
            print("  No goals assigned")
        else:
            print(f"  Goals: {[goal_id for goal_id, _ in paths]}")
    
    # Check and resolve collisions
    print("\nChecking for collisions...")
    collision_free_assignment = pathfinder.find_collision_free_paths(robots, assignment)
    
    # Execute the assignment and get the detailed execution plan
    print("\nExecuting collision-free assignment...")
    execution_plan = pathfinder.execute_assignments(robots, goals, collision_free_assignment)
    
    # Print execution details
    print("\nExecution Plan:")
    for robot_id, steps in execution_plan.items():
        print(f"Robot {robot_id}:")
        total_time = sum(step['time'] for step in steps)
        print(f"  Total time: {total_time:.2f} time units")
        for i, step in enumerate(steps):
            print(f"  Step {i+1}: Go to Goal {step['goal_id']} at {step['goal_location']} (time: {step['time']:.2f})")
    
    # Visualize the assignment
    print("\nGrid Visualization (Collision Free):")
    print(pathfinder.visualize_assignment(robots, goals, collision_free_assignment))

if __name__ == "__main__":
    example_collision_avoidance()