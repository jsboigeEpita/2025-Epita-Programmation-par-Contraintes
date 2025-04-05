"""Example of a simple nurse scheduling problem."""
from ortools.sat.python import cp_model
from matplotlib.colors import ListedColormap
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random

shift_names = ["Morning", "Evening", "Night"]

def generate_nurse_preference_matrices(num_nurses, num_days, num_shifts=3):
    """
    Generate random matrices for nurse scheduling preferences.
    
    Parameters:
    - num_nurses: Number of nurses
    - num_days: Number of days in the scheduling period
    - num_shifts: Number of shifts per day (default: 3, representing morning, evening, and night shifts)
    
    Returns:
    - shift_requests: 3D array [nurse][day][shift] = 1 if nurse requests that shift
    - day_off_requests: 2D array [nurse][day] = 1 if nurse requests that day off
    """
    # Initialize matrices with zeros
    shift_requests = [[[0 for _ in range(num_shifts)] for _ in range(num_days)] for _ in range(num_nurses)]
    day_off_requests = [[0 for _ in range(num_days)] for _ in range(num_nurses)]
    
    # Generate shift requests
    # Each nurse will request 2-4 specific shifts per week
    for n in range(num_nurses):
        # Determine how many shift requests this nurse will make
        num_shift_requests = random.randint(2, 4)
        
        # Randomly assign shift requests
        for _ in range(num_shift_requests):
            day = random.randint(0, num_days - 1)
            shift = random.randint(0, num_shifts - 1)
            shift_requests[n][day][shift] = 1
    
    # Generate day off requests
    # Each nurse will request 1-2 days off per week
    for n in range(num_nurses):
        # Determine how many days off this nurse will request
        num_days_off = random.randint(1, 2)
        
        # Randomly assign day off requests
        days_assigned = 0
        while days_assigned < num_days_off:
            day = random.randint(0, num_days - 1)
            # Only assign if not already assigned
            if day_off_requests[n][day] == 0:
                day_off_requests[n][day] = 1
                days_assigned += 1
    
    return shift_requests, day_off_requests

def main() -> None:
    # Data.
    num_nurses = 7
    num_shifts = 3
    num_days = 10
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    
    shift_requests, day_off_requests = generate_nurse_preference_matrices(num_nurses=num_nurses, num_days=num_days)

    # Creates the model.
    model = cp_model.CpModel()
    model.enumerate_all_solutions = True

    # Creates shift variables.
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.new_bool_var(f"shift_n{n}_d{d}_s{s}")

    # Each shift is assigned to exactly one nurse in the schedule period.
    for d in all_days:
        for s in all_shifts:
            model.add_exactly_one(shifts[(n, d, s)] for n in all_nurses)

    # Each nurse works at most one shift per day.
    for n in all_nurses:
        for d in all_days:
            model.add_at_most_one(shifts[(n, d, s)] for s in all_shifts)

    # Try to distribute the shifts evenly, so that each nurse works
    # min_shifts_per_nurse shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of nurses, some nurses will
    # be assigned one more shift.
    min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
    if num_shifts * num_days % num_nurses == 0:
        max_shifts_per_nurse = min_shifts_per_nurse
    else:
        max_shifts_per_nurse = min_shifts_per_nurse + 1
    for n in all_nurses:
        shifts_worked = []
        for d in all_days:
            for s in all_shifts:
                shifts_worked.append(shifts[(n, d, s)])
        model.add(min_shifts_per_nurse <= sum(shifts_worked))
        model.add(sum(shifts_worked) <= max_shifts_per_nurse)

    # Add objective function to maximize the number of respected preferences
    model.maximize(
        # Reward for respecting shift requests
        sum(
            shift_requests[n][d][s] * shifts[(n, d, s)]
            for n in all_nurses
            for d in all_days
            for s in all_shifts
        )+
        # Reward for respecting day-off requests
        sum(
            # 1 - sum(...) is 1 when nurse n doesn't work any shift on day d
            (1 - sum(shifts[(n, d, s)] for s in all_shifts)) * day_off_requests[n][d]
            for n in all_nurses
            for d in all_days
        )
    )

    # Creates the solver.
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True  # Enumerate multiple solutions


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

        def visualize_solution(self, solution_index=0):
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
            colors = ['#8dd3c7', '#ffffb3', '#bebada', '#f0f0f0']
            cmap = ListedColormap(colors)
            
            # Plot the heatmap
            plt.figure(figsize=(10, 6))
            sns.heatmap(df_numeric, annot=df, fmt='', cmap=cmap, cbar=False, linewidths=.5)
            plt.title(f"Optimal Schedule (Objective Value: {self._best_objective})")
            plt.show()

        def solution_count(self):
            return self._solution_count

    solution_printer = SolutionPrinter(shifts, num_nurses, num_days, num_shifts, 
                                          shift_requests, day_off_requests)

    # Solve the model
    status = solver.solve(model, solution_printer)
    
    # Print status
    print(f"Solver status: {solver.StatusName(status)}")
    
    # Print solution details
    solution = solution_printer.print_best_solutions()
    
    # Visualize the solution
    solution_printer.visualize_solution()
    
    # Print statistics
    print("\nStatistics")
    print(f"  - Conflicts: {solver.num_conflicts}")
    print(f"  - Branches : {solver.num_branches}")
    print(f"  - Wall time: {solver.wall_time} seconds")
    print(f"  - Solutions: {solution_printer.solution_count()}")

if __name__ == "__main__":
    main()
