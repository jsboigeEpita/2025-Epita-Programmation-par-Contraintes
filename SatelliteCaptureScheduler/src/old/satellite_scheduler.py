import math
import numpy as np
import ortools
from ortools.sat.python import cp_model

class Satellite:
    def __init__(self, memory_capacity_gb, image_size_per_km2_gb, image_duration_per_km2_sec, max_photo_duration_s, recalibration_time_s,  speed_kms_per_s):
        self.memory_capacity_gb = memory_capacity_gb
        self.image_size_per_km2_gb = image_size_per_km2_gb
        self.image_duration_per_km2_sec = image_duration_per_km2_sec
        self.max_photo_duration_s = max_photo_duration_s
        self.recalibration_time_s = recalibration_time_s
        self.speed_kms_per_s = speed_kms_per_s
    
    def calculate_distance(self, coord1, coord2):
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371
        return int(c * r / self.speed_kms_per_s)
        
    def calculate_travel_time(self, coord1, coord2):
        distance = self.calculate_distance(coord1, coord2)
        return distance / self.speed_kms_per_s

    def calculate_memory_usage(self, area_size_km2):
        return area_size_km2 * self.image_size_per_km2_gb
    
    def calculate_capture_duration(self, area_size_km2):
        duration = min(area_size_km2 * self.image_duration_per_km2_sec, self.max_photo_duration_s)
        return int(duration)


class Request:
    def __init__ (self, location, coordinates, priority, area_size_km2, time_window_sec):
        self.location = location
        self.coordinates = coordinates
        self.priority = priority
        self.area_size_km2 = area_size_km2
        self.time_window_sec = time_window_sec


class SatelliteScheduler:
    def __init__(self, satellite: Satellite, requests: list[Request]):
        self.satellite = satellite
        self.requests = requests
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.capture_durations = []
        self.mem_usages = []
        self.execution_log = []

    def solver(self):

        n = len(self.requests)

        for req in self.requests:
            # Image capture duration
            duration = self.satellite.calculate_capture_duration(req.area_size_km2)
            self.capture_durations.append(int(duration))

            # Total memory usage
            memory = self.satellite.calculate_memory_usage(req.area_size_km2)
            self.mem_usages.append(memory)

        # Decision variables (if the satellite is chosen and its start time)
        is_selected = [self.model.NewBoolVar(f"select_{i}") for i in range(n)]
        start_times = [self.model.NewIntVar(req.time_window_sec[0], req.time_window_sec[1], f"start_{i}")
                          for i, req in enumerate(self.requests)]
        
        # Travel time of each pair of points
        travel_times = {}
        for i in range(n):
            for j in range(n):
                if i != j:
                    travel_times[i, j] = self.satellite.calculate_travel_time(
                        self.requests[i].coordinates,
                        self.requests[j].coordinates
                    )

        # Calculate the latest ending time from all time windows (with recalibration)
        horizon = max(req.time_window_sec[1] for req in self.requests) + self.satellite.recalibration_time_s

        # Calculate the end times for each task
        end_times = []
        horizon = max(req.time_window_sec[1] for req in self.requests) + self.satellite.recalibration_time_s
        for i in range(n):
            end_time = self.model.NewIntVar(0, horizon, f"end_{i}")
            self.model.Add(end_time == start_times[i] + self.capture_durations[i]).OnlyEnforceIf(is_selected[i])

            # If not selected, sets a default value
            self.model.Add(end_time == 0).OnlyEnforceIf(is_selected[i].Not())
            end_times.append(end_time)

        # Sequence of selected location, checks if i is visited before j or j before i
        sequence = {}
        for i in range(n):
            for j in range(i+1, n):
                sequence[i, j] = self.model.NewBoolVar(f"sequence_{i}_{j}")

        # Multiple selected requests
        for i in range(n):
            for j in range(i+1, n):
                # i before j
                self.model.Add(start_times[j] >= self.capture_durations[i] + self.satellite.recalibration_time_s + travel_times[i, j]).OnlyEnforceIf([is_selected[i], is_selected[j], sequence[i, j]])

                # j before i
                self.model.Add(start_times[i] >= self.capture_durations[j] + self.satellite.recalibration_time_s + travel_times[j, i]).OnlyEnforceIf([is_selected[i], is_selected[j], sequence[i, j].Not()])

    
        # Ensure time windows
        for i, req in enumerate(self.requests):
            self.model.Add(start_times[i] + self.capture_durations[i] <= req.time_window_sec[1]).OnlyEnforceIf(is_selected[i])

        # Memory constraint
        # Memory limit of the satellite
        # Scaling the float to an int
        scale = 1000 
        memory_capacity = int(self.satellite.memory_capacity_gb * scale)
        memory_usage = [int(mem * scale) for mem in self.mem_usages]
        self.model.Add(sum(memory_usage[i] * is_selected[i] for i in range(n)) <= memory_capacity)

        # Objective function: maximize the number of selected requests
        priority_score = sum(req.priority * is_selected[i] for i, req in enumerate(self.requests))
        self.model.Maximize(priority_score)

        # Solve the model
        status = self.solver.Solve(self.model)

        results = []
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            
            selected_indices = [i for i in range(n) if self.solver.Value(is_selected[i]) == 1]
            selected_indices.sort(key=lambda i: self.solver.Value(start_times[i]))

            total_memory = 0

            # Selected locations
            for idx, i in enumerate(selected_indices):
                start = self.solver.Value(start_times[i])
                duration = self.capture_durations[i]
                memory = self.mem_usages[i]
                total_memory += memory

                travel_time = 0
                if idx > 0:
                    prev_idx = selected_indices[idx - 1]
                    travel_time = self.satellite.calculate_distance(
                        self.requests[prev_idx].coordinates,
                        self.requests[i].coordinates,
                    )

                    result = {
                        "location": self.requests[i].location,
                        "priority": self.requests[i].priority,
                        "start_time": start,
                        "duration": duration,
                        "end_time": start + duration + travel_time,
                        "memory_used": memory,
                        "travel_time": travel_time,
                        "selected": True,
                        "time_window": self.requests[i].time_window_sec,
                    }
                    results.append(result)

            # Unselected locations
            for i in range(n):
                if i not in selected_indices:
                    result = {
                        "location": self.requests[i].location,
                        "priority": self.requests[i].priority,
                        "selected": False,
                    }
                    results.append(result)
        else:
            # No solution found
            for i in range(n):
                result = {
                    "location": self.requests[i].location,
                    "priority": self.requests[i].priority,
                    "selected": False,
                }
                results.append(result)
    
        return status, results
    
    def print_solution(self, status, results):
        if status == cp_model.OPTIMAL:
            print("Found optimal solution!")
        elif status == cp_model.FEASIBLE:
            print("Found a feasible solution.")
        else:
            print("No solution found.")

        selected_results = [r for r in results if r.get("selected", True)]
        print(f"\nScheduled {len(selected_results)} out of {len(self.requests)} image captures:")

        total_memory = 0
        total_priority = 0
        prev_end_time = 0

        for idx, r in enumerate(selected_results):
            if r["selected"]:
                print(f"{r['location']} (Priority {r['priority']}): Start at {r['start_time']}s, Duration: {r['duration']}s, Time window: {r['time_window']}")
                print(f"  Memory used: {r['memory_used']:.2f} GB, Travel time from previous: {r['travel_time']}s")
                if idx == len(selected_results) - 1:
                    effective_end = r['start_time'] + r['duration']
                    
                    print(f"  No recalibration.")
                else:
                    effective_end = r['start_time'] + r['duration'] + self.satellite.recalibration_time_s
                    
                    print(f"  Recalibration time: {self.satellite.recalibration_time_s}s")
                print(f"  End task at: {effective_end}s")
                
                if idx > 0:
                    print(f"  Time since previous task: {r['start_time'] - prev_end_time}s")
                
                prev_end_time = effective_end
                
                print()
                
                total_memory += r['memory_used']
                total_priority += r['priority']
                
        print(f"Total memory used: {total_memory:.2f} GB out of {self.satellite.memory_capacity_gb} GB")
        print(f"Total priority score: {total_priority}")

        unscheduled = [r for r in results if not r.get("selected", True)]
        if unscheduled:
            print("\nUnscheduled locations:")
            for r in unscheduled:
                print(f"{r['location']} (Priority {r['priority']})")

                
if __name__ == "__main__":
    # Example usage
    satellite = Satellite(
        memory_capacity_gb=100,
        image_size_per_km2_gb=0.1,
        image_duration_per_km2_sec=5,
        max_photo_duration_s=300,
        recalibration_time_s=60,
        speed_kms_per_s=10
    )

    requests = [
        Request("New-York", (40.730610, -73.935242), 3, 6, (500, 1200)),
        Request("Los-Angeles", (34.052235, -118.243683), 5, 8, (600, 1300)),
        Request("Chicago", (41.878113, -87.629799), 2, 4, (700, 1400)),
        Request("San-Francisco", (37.774929, -122.419416), 4, 5, (800, 1500)),
        Request("Miami", (25.761680, -80.191790), 3, 7, (400, 1100)),
        Request("Seattle", (47.608013, -122.335167), 4, 6, (900, 1600)),
        Request("Houston", (29.760427, -95.369803), 2, 5, (600, 1300)),
        Request("Boston", (42.360081, -71.058880), 3, 4, (450, 1150))
    ]

    scheduler = SatelliteScheduler(satellite, requests)
    status, results = scheduler.solver()
    scheduler.print_solution(status, results)
    

        