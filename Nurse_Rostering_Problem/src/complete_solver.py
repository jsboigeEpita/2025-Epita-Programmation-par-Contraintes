# Import required libraries
from ortools.sat.python import cp_model
from matplotlib.colors import ListedColormap
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import json
import os
from SolutionPrinter import SolutionPrinter

# Define constants that will be used throughout the notebook
shift_names = ["Morning", "Evening", "Night"]

def collect_nurse_rostering_parameters():
    # System message: instruct the assistant on its role and output format.
    system_message = {
        "role": "system",
        "content": (
         "You are a helpful assistant for scheduling nurse shifts. Your goal is to converse naturally with the user "
            "and collect all required parameters. The mandatory parameters are:\n"
            "  - num_days: number of days of planning (an integer).\n"
            "  - num_nurses: number of nurses (an integer).\n"
            "  - max_consecutive_days: maximum consecutive work days (an integer).\n"
            "  - num_senior_nurses: number of available senior nurses (an integer).\n\n"
            "Additionally, optionally collect preferred constraints:\n"
            "  - preferred_day_offs: a 2D array (list of lists) with dimensions [num_nurses][num_days]. "
            "Each element is 1 if that nurse (indexed from 0) requests that day off, or 0 otherwise.\n"
            "  - preferred_shifts: a 3D array (list of lists of lists) with dimensions [num_nurses][num_days][num_shifts]. "
            "Each element is 1 if that nurse (indexed from 0) requests that shift on that day, or 0 otherwise.\n\n"
            "If the user declines to provide the optional matrices, output them as null. Also, if the user mentions nurse names "
            "and their preferences (e.g., 'Stephany would like to work the 2nd shift on the 1st Monday'), use your parsing skills "
            "to map the nurse name to a nurse index (starting at 0) and the day/shift to their corresponding indices (also starting at 0). "
            "Make sure that the final JSON object exactly contains the following keys: num_days, num_nurses, max_consecutive_days, "
            "num_senior_nurses, preferred_day_offs, and preferred_shifts, and nothing else.\n\n"
            "When all parameters have been collected, output a final message that starts with the token 'PARAMETERS:' followed immediately "
            "by a valid JSON object with the required keys. Do not include any extra text or inline comments in the JSON output."
        ) 
    }

    messages = [system_message]

    # Set your API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    print("Please answer the assistant's questions as naturally as possible.\n")
    
    # Conversation loop.
    while True:
        user_input = input("User: ")
        messages.append({"role": "user", "content": user_input})

        # Call the ChatCompletion API
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # or another model of your choice
            messages=messages,
            temperature=0.7
        )

        # Extract the assistant's reply
        try:
            reply = completion.choices[0].message["content"]
        except Exception as e:
            print("Error extracting reply:", e)
            continue

        print("Assistant:", "\033[33m" + reply + '\033[0m')
        messages.append({"role": "assistant", "content": reply})

        # If the assistant signals that all parameters are collected with "PARAMETERS:" prefix, break the loop.
        if "PARAMETERS:" in reply.strip():
            break

    # Extract the JSON part.
    # Expecting a reply like: PARAMETERS: { "num_days": 7, "num_nurses": 10, ... }
    try:
        json_str = reply.split("PARAMETERS:", 1)[1].strip()
        params = json.loads(json_str)
    except Exception as e:
        print("Error parsing JSON from the assistant's output:", e)
        params = {}

    return params

params = collect_nurse_rostering_parameters()
print(params)

# Problem parameters
num_nurses = params.get('num_nurses')  # Number of nurses
num_shifts = 3  # Number of shifts per day (Morning, Evening, Night)
num_days = params.get('num_days')   # Planning horizon
max_consecutive_days = params.get('max_consecutive_days')  # Maximum consecutive work days
num_senior_nurses = params.get('num_senior_nurses')  # Number of available senior nurses
day_off_requests = params.get('preferred_day_offs')  # Day off preferences
shift_requests = params.get('preferred_shifts')  # Shift preferences

# Define ranges for convenience
all_nurses = range(num_nurses)
all_shifts = range(num_shifts)
all_days = range(num_days)

# Display problem parameters
print(f"Problem size: {num_nurses} nurses, {num_shifts} shifts per day, {num_days} days")
print(f"Total shifts to assign: {num_shifts * num_days}")
print(f"Minimum shifts per nurse: {(num_shifts * num_days) // num_nurses}")
print(f"Maximum shifts per nurse: {(num_shifts * num_days) // num_nurses + (1 if (num_shifts * num_days) % num_nurses != 0 else 0)}")

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

# Create the basic model
basic_model, basic_shifts = create_basic_model()
print("Basic model created with essential constraints.")

def visualize_requests():
    plt.figure(figsize=(14, 8))
    
    plt.subplot(1, 2, 1)
    shift_data = []
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                if shift_requests[n][d][s] == 1:
                    shift_data.append((f"Nurse {n}", f"Day {d+1}", shift_names[s]))
    
    if shift_data:
        df = pd.DataFrame(shift_data, columns=["Nurse", "Day", "Shift"])
        table = pd.crosstab(df["Nurse"], [df["Day"], df["Shift"]])
        sns.heatmap(table, cmap="Blues", cbar=False, annot=True, fmt="d")
        plt.title("Shift Requests")
    else:
        plt.text(0.5, 0.5, "No shift requests", ha="center", va="center")
        plt.title("Shift Requests (None)")
    
    plt.subplot(1, 2, 2)
    day_off_df = pd.DataFrame(day_off_requests, 
                             index=[f"Nurse {n}" for n in all_nurses],
                             columns=[f"Day {d+1}" for d in all_days])
    sns.heatmap(day_off_df, cmap="Reds", cbar=False, annot=True, fmt=".0f")
    plt.title("Day Off Requests")
    
    plt.tight_layout()
    plt.show()

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

if (day_off_requests is not None) and (shift_requests is not None):
    visualize_requests()

if (shift_requests is not None) and (day_off_requests is not None):
    # Create the model with preferences
    model_with_preferences, shifts_with_preferences = create_model_with_preferences()
    print("Model with preferences created.")

def create_advanced_model():
    """Create an advanced model with additional constraints."""
    
    if (shift_requests is not None) and (day_off_requests is not None): 
        # Start with the basic model with preferences
        model, shifts = create_model_with_preferences()
    else:
        # Start with the basic model
        model, shifts = create_basic_model()
    
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

# Create the advanced model
advanced_model, advanced_shifts = create_advanced_model()
print("Advanced model created with additional constraints.")

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


if (day_off_requests is not None) and (shift_requests is not None):
    # Solve the advanced model with preferences
    solve_model(advanced_model, advanced_shifts, "Advanced Model with Preferences", with_preferences=True)
else:
    # Solve the advanced model without preferences
    solve_model(advanced_model, advanced_shifts, "Advanced Model without Preferences")