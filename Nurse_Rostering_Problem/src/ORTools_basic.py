"""Example of a simple nurse scheduling problem."""
from ortools.sat.python import cp_model
from SolutionPrinter import SolutionPrinter

shift_names = ["Morning", "Evening", "Night"]

# Data.
num_nurses = 7
num_shifts = 3
num_days = 10
all_nurses = range(num_nurses)
all_shifts = range(num_shifts)
all_days = range(num_days)

def create_basic_model():
        """Create a basic model with essential constraints but no preferences."""
        
        # Create the model
        model = cp_model.CpModel()
        
        # Create shift variables
        # shifts[(n, d, s)] = 1 if nurse n works shift s on day d, 0 otherwise
        shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    shifts[(n, d, s)] = model.new_bool_var(f"shift_n{n}_d{d}_s{s}")
        
        # Add essential constraints
        
        # Constraint 1: Each shift is assigned to exactly one nurse
        for d in all_days:
            for s in all_shifts:
                model.add_exactly_one(shifts[(n, d, s)] for n in all_nurses)
        
        # Constraint 2: Each nurse works at most one shift per day
        for n in all_nurses:
            for d in all_days:
                model.add_at_most_one(shifts[(n, d, s)] for s in all_shifts)
        
        # Constraint 3: Fair distribution of shifts
        min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
        max_shifts_per_nurse = min_shifts_per_nurse + (1 if (num_shifts * num_days) % num_nurses != 0 else 0)
        
        for n in all_nurses:
            num_shifts_worked = sum(shifts[(n, d, s)] for d in all_days for s in all_shifts)
            model.add(min_shifts_per_nurse <= num_shifts_worked)
            model.add(num_shifts_worked <= max_shifts_per_nurse)
        
        return model, shifts

def solve_model(model, shifts, model_name, with_preferences=False):
    """Solve the model and print/visualize the solution."""
    print(f"\n=== Solving {model_name} ===\n")
    
    # Create the solver
    solver = cp_model.CpSolver()
    
    # Create the solution printer
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

    basic_model, basic_shifts = create_basic_model()
    solve_model(basic_model, basic_shifts, "Basic Model")


if __name__ == "__main__":
    main()