from ortools.sat.python import cp_model
import math

def calculate_distance(coord1, coord2, satellite_speed):
    """Calculate the great-circle distance between two points on Earth using the Haversine formula."""
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    # Convert to seconds (assuming satellite moves at X km/s)
    # satellite_speed = 100  # km/s (example value)
    return int(c * r / satellite_speed)  # Return travel time in seconds

def solve_satellite_scheduling(satellite, requests):
    model = cp_model.CpModel()
    
    num_requests = len(requests)
    
    # Calculate capture durations and memory usage
    capture_durations = []
    mem_usages = []
    
    for req in requests:
        # Calculate capture duration (in seconds)
        duration = min(req["area_size_km2"] * satellite["image_duration_per_km2_sec"], 
                       satellite["max_photo_duration_s"])
        # print(duration)
        capture_durations.append(int(duration))  # Convert to integer
        
        # Calculate memory usage (in GB)
        memory = req["area_size_km2"] * satellite["image_size_per_km2_gb"]
        
        mem_usages.append(memory)
    
    # Decision variables
    is_selected = [model.NewBoolVar(f"select_{i}") for i in range(num_requests)]
    start_times = [model.NewIntVar(req["time_window_sec"][0], req["time_window_sec"][1], f"start_{i}") 
                   for i, req in enumerate(requests)]
    
    # Calculate the latest ending time from all time windows
    # horizon = max(req["time_window_sec"][1] for req in requests)
    horizon = max(req["time_window_sec"][1] for req in requests) + satellite["recalibration_time_s"]
    
    # Calculate end times for each task
    end_times = []
    for i in range(num_requests):
        end_time = model.NewIntVar(0, horizon, f"end_{i}")
        model.Add(end_time == start_times[i] + capture_durations[i]).OnlyEnforceIf(is_selected[i])
        # If not selected, just set a default value (doesn't matter which)
        model.Add(end_time == 0).OnlyEnforceIf(is_selected[i].Not())
        end_times.append(end_time)
    
    # Variables to track the sequence of selected locations
    # For each pair i,j we have a variable that is 1 if i is performed before j
    sequence = {}
    for i in range(num_requests):
        for j in range(i+1, num_requests):
            sequence[i, j] = model.NewBoolVar(f"sequence_{i}_{j}")
    
    # Non-overlapping constraints
    for i in range(num_requests):
        for j in range(i+1, num_requests):
            # If both tasks are selected, they cannot overlap
            i_end = model.NewIntVar(0, horizon, f"end_{i}")
            model.Add(i_end == start_times[i] + capture_durations[i] + satellite["recalibration_time_s"])
            
            # Either i before j or j before i
            # If i before j
            model.Add(i_end <= start_times[j]).OnlyEnforceIf([is_selected[i], is_selected[j], sequence[i, j]])
            
            # If j before i
            j_end = model.NewIntVar(0, horizon, f"end_{j}")
            model.Add(j_end == start_times[j] + capture_durations[j] + satellite["recalibration_time_s"])
            model.Add(j_end <= start_times[i]).OnlyEnforceIf([is_selected[i], is_selected[j], sequence[i, j].Not()])

    # Time window constraints
    for i, req in enumerate(requests):
        # If task is selected, it must finish within its time window
        model.Add(start_times[i] + capture_durations[i] <= req["time_window_sec"][1]).OnlyEnforceIf(is_selected[i])
    
    # Memory capacity constraint
    # Convert floating point calculations to a scaled integer constraint
    scale = 1000  # Scaling factor
    memory_capacity_scaled = int(satellite["memory_capacity_gb"] * scale)
    mem_usages_scaled = [int(mem * scale) for mem in mem_usages]
    
    model.Add(sum(mem_usages_scaled[i] * is_selected[i] for i in range(num_requests)) <= memory_capacity_scaled)
    
    
    # Maximize priority objective
    priority_score = sum(requests[i]["priority"] * is_selected[i] for i in range(num_requests))
    model.Maximize(priority_score)
    
    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    # Process results
    results = []
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Get selected locations
        selected_indices = [i for i in range(num_requests) if solver.Value(is_selected[i])]
        
        # Sort them based on start time
        selected_indices.sort(key=lambda i: solver.Value(start_times[i]))
        
        total_memory = 0
        for idx, i in enumerate(selected_indices):
            start = solver.Value(start_times[i])
            duration = capture_durations[i]
            memory = mem_usages[i]
            total_memory += memory
            
            # Calculate travel time from previous location if applicable
            travel_time = 0
            if idx > 0:
                prev_idx = selected_indices[idx-1]
                travel_time = calculate_distance(requests[prev_idx]["coordinates"], requests[i]["coordinates"], satellite['speed_kms_per_s'])
            
            result = {
                "location": requests[i]["location"],
                "priority": requests[i]["priority"],
                "start_time": start,
                "duration": duration,
                "end_time": start + duration,
                "memory_used": memory,
                "travel_time": travel_time,
                "selected": True,
                "time_window": requests[i]["time_window_sec"]
            }
            results.append(result)
        
        # Add unselected locations
        for i in range(num_requests):
            if i not in selected_indices:
                results.append({
                    "location": requests[i]["location"],
                    "priority": requests[i]["priority"],
                    "selected": False
                })
    else:
        # No solution found
        for i in range(num_requests):
            results.append({
                "location": requests[i]["location"],
                "priority": requests[i]["priority"],
                "selected": False
            })
    
    return status, results

# Satellite parameters
satellite = {
    "memory_capacity_gb": 5,
    "image_size_per_km2_gb": 0.15,
    "image_duration_per_km2_sec": 3.5,
    "max_photo_duration_s": 120,
    "simultaneous_tasks": False,
    "recalibration_time_s": 30,
    "speed_kms_per_s": 100
}

# Image capture requests
requests = [
    {"location": "Tokyo", "coordinates": (35.6895, 139.6917), "priority": 3, "area_size_km2": 10, "time_window_sec": (0, 100)},
    {"location": "Paris", "coordinates": (48.8566, 2.3522), "priority": 1, "area_size_km2": 8, "time_window_sec": (100, 150)},
    {"location": "Montréal", "coordinates": (45.5017, -73.5673), "priority": 2, "area_size_km2": 8, "time_window_sec": (50, 120)},
    {"location": "New-York", "coordinates": (40.730610, -73.935242), "priority": 3, "area_size_km2": 6, "time_window_sec": (50, 120)}
]


# Solve the problem
status, results = solve_satellite_scheduling(satellite, requests)

# Print results
if status == cp_model.OPTIMAL:
    print("Found optimal solution!")
elif status == cp_model.FEASIBLE:
    print("Found a feasible solution.")
else:
    print("No solution found.")

selected_results = [r for r in results if r.get("selected", True)]
print(f"\nScheduled {len(selected_results)} out of {len(requests)} image captures:")

total_memory = 0
total_priority = 0
prev_end_time = 0

for idx, r in enumerate(selected_results):
    if r["selected"]:  # This is a selected location
        print(f"{r['location']} (Priority {r['priority']}): Start at {r['start_time']}s, Duration: {r['duration']}s, Time window: {r['time_window']}")
        print(f"  Memory used: {r['memory_used']:.2f} GB, Travel time from previous: {r['travel_time']}s")
        if idx == len(selected_results) - 1:
            print(f"  No recalibration.")
        else:
            print(f"  Recalibration time: {satellite['recalibration_time_s']}s")
        end_time = r['start_time'] + r['duration'] + satellite['recalibration_time_s'] * (idx != len(selected_results) - 1)
        print(f"  End task at: {end_time}s")
        
        if prev_end_time > 0:
            print(f"  Time since previous task: {r['start_time'] - prev_end_time}s")
        
        prev_end_time = end_time
        print()
        
        total_memory += r['memory_used']
        total_priority += r['priority']

print(f"Total memory used: {total_memory:.2f} GB out of {satellite['memory_capacity_gb']} GB")
print(f"Total priority score: {total_priority}")

# List unscheduled locations
unscheduled = [r for r in results if not r.get("selected", True)]
if unscheduled:
    print("\nUnscheduled locations:")
    for r in unscheduled:
        print(f"{r['location']} (Priority {r['priority']})")