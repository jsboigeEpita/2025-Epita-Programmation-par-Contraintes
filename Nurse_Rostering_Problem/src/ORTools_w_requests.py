"""Example of a simple nurse scheduling problem."""
from ortools.sat.python import cp_model
from matplotlib.colors import ListedColormap
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from SolutionPrinter import SolutionPrinter
from ORTools_basic import create_basic_model

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
    # Each nurse will request 1-2 days off per period
    for n in range(num_nurses):
        # Determine how many days off this nurse will request
        num_days_off = random.randint(1, 2)
        
        # Randomly assign day off requests
        days_assigned = 0
        while days_assigned < num_days_off:
            day = random.randint(0, num_days - 1)
            # Only assign if not already assigned
            if day_off_requests[n][day] == 0 and shift_requests[n][day].count(1) == 0:
                day_off_requests[n][day] = 1
                days_assigned += 1
    
    return shift_requests, day_off_requests

# Data.
num_nurses = 7
num_shifts = 3
num_days = 10
all_nurses = range(num_nurses)
all_shifts = range(num_shifts)
all_days = range(num_days)

shift_requests, day_off_requests = generate_nurse_preference_matrices(num_nurses=num_nurses, num_days=num_days)

def create_model_with_preferences():
    """Create a model with both essential constraints and nurse preferences."""
    
    # Start with the basic model
    model, shifts = create_basic_model()
    
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
    
    return model, shifts

def create_advanced_model():
    """Create an advanced model with additional constraints."""
    
    # Start with the basic model with preferences
    model, shifts = create_model_with_preferences()
    
    # Additional Constraint 1: Consecutive Shifts
    # Nurses should not work night shift followed by morning shift the next day
    night_shift = 2  # Index for night shift
    morning_shift = 0  # Index for morning shift
    
    for n in all_nurses:
        for d in range(num_days - 1):  # All days except the last
            # If nurse n works night shift on day d, they cannot work morning shift on day d+1
            model.add(shifts[(n, d, night_shift)] + shifts[(n, d + 1, morning_shift)] <= 1)
    
    # Additional Constraint 2: Skill Requirements
    # Let's assume nurses 0 and 2 are senior and at least one senior nurse must be present each day
    senior_nurses = [0, 2]
    
    for d in all_days:
        # At least one senior nurse must work on day d (any shift)
        model.add(
            sum(shifts[(n, d, s)] for n in senior_nurses for s in all_shifts) >= 1
        )
    
    # Additional Constraint 3: Consecutive Work Days
    # Nurses should not work more than 3 consecutive days
    max_consecutive_days = 3
    
    for n in all_nurses:
        for d in range(num_days - max_consecutive_days + 1):
            # Calculate if nurse n works on each of the consecutive days
            works_on_days = [
                shifts[(n, d + i, s)] for i in range(max_consecutive_days) for s in all_shifts
            ]
            # Ensure at least one day off after max_consecutive_days
            model.add(sum(works_on_days) <= max_consecutive_days)
    
    return model, shifts

def solve_model(model, shifts, model_name, with_preferences=False):
    """Solve the model and print/visualize the solution."""
    print(f"\n=== Solving {model_name} ===\n")
    
    # Create the solver
    solver = cp_model.CpSolver()
    
    # Create the solution printer
    if with_preferences:
        solver.parameters.enumerate_all_solutions = True
        solution_printer = SolutionPrinter(shifts, num_nurses, num_days, num_shifts, 
                                        shift_requests, day_off_requests)
    else:
        solution_printer = SolutionPrinter(shifts, num_nurses, num_days, num_shifts)
    
    # Solve the model
    status = solver.solve(model, solution_printer)
    
    # Print status
    print(f"Solver status: {solver.StatusName(status)}")
    
    # Print solution details
    solution = solution_printer.print_best_solutions()
    
    # Visualize the solution
    solution_printer.visualize_solution(preferences=with_preferences)
    
    # Print statistics
    print("\nStatistics")
    print(f"  - Conflicts: {solver.num_conflicts}")
    print(f"  - Branches : {solver.num_branches}")
    print(f"  - Wall time: {solver.wall_time} seconds")
    print(f"  - Solutions: {solution_printer.solution_count()}")

def main() -> None:
    
    advanced_model, advanced_shifts = create_advanced_model()

    solve_model(advanced_model, advanced_shifts, "Advanced Model", with_preferences=True)

if __name__ == "__main__":
    main()
