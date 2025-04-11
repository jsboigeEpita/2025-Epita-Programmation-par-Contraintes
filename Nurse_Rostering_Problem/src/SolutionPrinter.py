from ortools.sat.python import cp_model
import matplotlib
from matplotlib.colors import ListedColormap
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random

shift_names = ["Morning", "Evening", "Night"]

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, shifts, num_nurses, num_days, num_shifts, shift_requests=None, day_off_requests=None):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._num_nurses = num_nurses
        self._num_days = num_days
        self._num_shifts = num_shifts
        self._solution_count = 0
        self._best_objective = float('-inf')
        self._best_solutions = []
        self._shift_requests = shift_requests
        self._day_off_requests = day_off_requests

    def on_solution_callback(self):
        self._solution_count += 1
        current_objective = self.ObjectiveValue()

        # If this is a better solution, reset best solutions list
        if current_objective > self._best_objective:
            self._best_objective = current_objective
            self._best_solutions = [self.extract_solution()]
        elif current_objective == self._best_objective:
            self._best_solutions.append(self.extract_solution())

    def extract_solution(self):
        """Extracts the solution as a structured format."""
        solution = []
        for d in range(self._num_days):
            day_schedule = []
            for n in range(self._num_nurses):
                shifts_worked = []
                for s in range(self._num_shifts):
                    if self.value(self._shifts[(n, d, s)]):
                        shifts_worked.append(shift_names[s])
                day_schedule.append((n, shifts_worked))
            solution.append(day_schedule)
        return solution

    def print_best_solutions(self):
        print(f"\nBest Objective Value: {self._best_objective}")
        print(f"Total optimal solutions found: {len(self._best_solutions)}")

        total_requests = 0
        if self._shift_requests and self._day_off_requests:
            total_requests = sum(sum(sum(day) for day in nurse) for nurse in self._shift_requests) + \
                          sum(sum(day) for day in self._day_off_requests)

        for i, sol in enumerate(self._best_solutions[:1]):  # Print only the first solution for brevity
            print(f"\nOptimal Solution {i + 1}:")
            respected_requests = 0

            for d, day_schedule in enumerate(sol):
                print(f"Day {d + 1}:")
                for nurse, shifts in day_schedule:
                    shift_str = ', '.join(shifts) if shifts else "No shift"
                    requested = False
                    
                    if self._shift_requests and self._day_off_requests:
                        if not shifts and self._day_off_requests[nurse][d] == 1:
                            requested = True
                            respected_requests += 1
                        elif shifts and any(self._shift_requests[nurse][d][s] == 1 
                                     for s in range(self._num_shifts) 
                                     if shift_names[s] in shifts):
                            requested = True
                            respected_requests += 1
                        
                    print(f"  Nurse {nurse}: {shift_str} {'(requested)' if requested else '(not requested)'}")
                print()
                
            if total_requests > 0:
                print(f"Total respected requests: {respected_requests} / {total_requests}")
                
        return self._best_solutions[0] if self._best_solutions else None

    def visualize_solution(self, solution_index=0, preferences=True):
        """Visualize the solution using a heatmap."""
        if not self._best_solutions:
            print("No solutions to visualize.")
            return
            
        solution = self._best_solutions[solution_index]
        
        # Create a matrix to represent the schedule
        schedule_matrix = [['' for _ in range(self._num_days)] for _ in range(self._num_nurses)]
        
        for d, day_schedule in enumerate(solution):
            for nurse, shifts in day_schedule:
                if shifts:
                    schedule_matrix[nurse][d] = shifts[0][0]  # First letter of shift
                else:
                    schedule_matrix[nurse][d] = '-'  # No shift
        
        # Convert to DataFrame for easier visualization
        df = pd.DataFrame(schedule_matrix, 
                        index=[f"Nurse {n}" for n in range(self._num_nurses)],
                        columns=[f"Day {d+1}" for d in range(self._num_days)])
        
        # Create a numerical mapping for the shifts
        shift_to_num = {'M': 0, 'E': 1, 'N': 2, '-': 3}
        df_numeric = df.applymap(lambda x: shift_to_num.get(x, 3))
        
        # Define colors for each shift type
        basic_colors = {'M': '#8dd3c7', 'E': '#2F81D0', 'N': '#bebada', '-': '#f0f0f0'}
        colors = ['#f0f0f0', '#f0f0f0', '#f0f0f0', '#f0f0f0']
        cmap = ListedColormap(colors)
        
        # Plot the heatmap
        plt.figure(figsize=(10, 6))
        ax = sns.heatmap(df_numeric, cmap=cmap, cbar=False, linewidths=.5)
        plt.title(f"Optimal Schedule (Objective Value: {self._best_objective})")

        # Loop over the DataFrame to add annotations with conditional colors
        for i in range(df_numeric.shape[0]):       # iterate over nurses (rows)
            for j in range(df_numeric.shape[1]):   # iterate over days (columns)
                # Get the letter for the current cell
                letter = df.iloc[i, j]
                if not preferences:
                    cell_color = basic_colors.get(letter, '#f0f0f0')
                else:
                    # Determine the color based on the conditions:
                    if self._day_off_requests and self._day_off_requests[i][j] == 1:
                        if letter == '-':
                            cell_color = 'green'
                        else:
                            cell_color = 'orange'
                    else:
                        # Map letter to its shift index (M=0, E=1, N=2)
                        if letter == 'M':
                            shift_index = 0
                        elif letter == 'E':
                            shift_index = 1
                        elif letter == 'N':
                            shift_index = 2
                        else:
                            shift_index = None
                        
                        if self._shift_requests and self._shift_requests[i][j]==[0,0,0]:
                            cell_color = 'grey'
                        elif shift_index is None:
                            cell_color = 'orange'
                        # If the nurse requested the assigned shift, set the cell to green.
                        elif self._shift_requests and self._shift_requests[i][j][shift_index] == 1:
                            cell_color = 'green'
                        else:
                            cell_color = 'orange'
                
                # Create and add a rectangle patch for the cell.
                # Note: The heatmap grid coordinates start at (0,0) at the top left.
                rect = plt.Rectangle((j, i), 1, 1, facecolor=cell_color,
                                    edgecolor='white', lw=0.5, alpha=0.6)
                ax.add_patch(rect)
                
                # Optionally, overlay the shift letter on top of the colored cell.
                # Here, we choose white text for better contrast on dark backgrounds.
                ax.text(j + 0.5, i + 0.5, letter, ha='center', va='center', color='white')

        plt.show()

    def solution_count(self):
        return self._solution_count