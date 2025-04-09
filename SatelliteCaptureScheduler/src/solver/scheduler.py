from ortools.sat.python import cp_model

from core.satellite import Satellite
from core.request import Request


class SatelliteScheduler:

    def __init__(self, satellite: Satellite, requests: list[Request]) -> None:

        self.__satellite = satellite
        self.__requests = requests
        self.__model = cp_model.CpModel()
        self.__solver = cp_model.CpSolver()

    def solve(self) -> tuple[int, list[dict]]:

        n = len(self.__requests)
        capture_durations = []
        mem_usages = []

        for req in self.__requests:
            # Image capture duration
            duration = self.__satellite.calculate_capture_duration(req.area_size_km2)
            capture_durations.append(int(duration))

            # Total memory usage
            memory = self.__satellite.calculate_memory_usage(req.area_size_km2)
            mem_usages.append(memory)

        # Decision variables (if the satellite is chosen and its start time)
        is_selected = [self.__model.NewBoolVar(f"select_{i}") for i in range(n)]
        start_times = [
            self.__model.NewIntVar(
                req.time_window_sec[0], req.time_window_sec[1], f"start_{i}"
            )
            for i, req in enumerate(self.__requests)
        ]

        # Travel time of each pair of points
        travel_times = {}
        for i in range(n):
            for j in range(n):
                if i != j:
                    travel_times[i, j] = self.__satellite.calculate_distance(
                        self.__requests[i].coordinates, self.__requests[j].coordinates
                    )

        # Calculate the latest ending time from all time windows (with recalibration)
        horizon = (
            max(req.time_window_sec[1] for req in self.__requests)
            + self.__satellite.recalibration_time_s
        )

        # Calculate the end times for each task
        end_times = []
        for i in range(n):
            end_time = self.__model.NewIntVar(0, horizon, f"end_{i}")
            self.__model.Add(
                end_time == start_times[i] + capture_durations[i]
            ).OnlyEnforceIf(is_selected[i])

            # If not selected, sets a default value
            self.__model.Add(end_time == 0).OnlyEnforceIf(is_selected[i].Not())
            end_times.append(end_time)

        # Sequence of selected location, checks if i is visited before j or j before i
        sequence = {}
        for i in range(n):
            for j in range(i + 1, n):
                sequence[i, j] = self.__model.NewBoolVar(f"sequence_{i}_{j}")

        # Multiple selected requests
        for i in range(n):
            for j in range(i + 1, n):
                # i before j
                self.__model.Add(
                    start_times[j]
                    >= start_times[i]
                    + capture_durations[i]
                    + self.__satellite.recalibration_time_s
                    + travel_times[i, j]
                ).OnlyEnforceIf([is_selected[i], is_selected[j], sequence[i, j]])

                # j before i
                self.__model.Add(
                    start_times[i]
                    >= start_times[j]
                    + capture_durations[j]
                    + self.__satellite.recalibration_time_s
                    + travel_times[j, i]
                ).OnlyEnforceIf([is_selected[i], is_selected[j], sequence[i, j].Not()])

        # Ensure time windows
        for i, req in enumerate(self.__requests):
            self.__model.Add(
                start_times[i] + capture_durations[i] <= req.time_window_sec[1]
            ).OnlyEnforceIf(is_selected[i])

        # Memory constraint
        # Memory limit of the satellite
        # Scaling the float to an int
        scale = 1000
        memory_capacity_scaled = int(self.__satellite.memory_capacity_gb * scale)
        memory_usages_scaled = [int(mem * scale) for mem in mem_usages]

        self.__model.Add(
            sum(memory_usages_scaled[i] * is_selected[i] for i in range(n))
            <= memory_capacity_scaled
        )

        # Objective function: maximize the number of selected requests
        priority_score = sum(
            self.__requests[i].priority * is_selected[i] for i in range(n)
        )
        self.__model.Maximize(priority_score)

        # Solve the model
        status = self.__solver.Solve(self.__model)

        results = []
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:

            selected_indices = [
                i for i in range(n) if self.__solver.Value(is_selected[i])
            ]
            selected_indices.sort(key=lambda i: self.__solver.Value(start_times[i]))
            total_memory = 0

            # Selected locations
            for idx, i in enumerate(selected_indices):
                start = self.__solver.Value(start_times[i])
                duration = capture_durations[i]
                memory = mem_usages[i]
                total_memory += memory

                travel_time = 0
                if idx > 0:
                    prev_idx = selected_indices[idx - 1]
                    travel_time = self.__satellite.calculate_distance(
                        self.__requests[prev_idx].coordinates,
                        self.__requests[i].coordinates,
                    )

                result = {
                    "location": self.__requests[i].location,
                    "priority": self.__requests[i].priority,
                    "start_time": start,
                    "duration": duration,
                    "end_time": start + duration + travel_time,
                    "memory_used": memory,
                    "travel_time": travel_time,
                    "selected": True,
                    "time_window": self.__requests[i].time_window_sec,
                }
                results.append(result)

            # Unselected locations
            for i in range(n):
                if i not in selected_indices:
                    result = {
                        "location": self.__requests[i].location,
                        "priority": self.__requests[i].priority,
                        "selected": False,
                    }
                    results.append(result)
        else:
            # No solution found
            for i in range(n):
                result = {
                    "location": self.__requests[i].location,
                    "priority": self.__requests[i].priority,
                    "selected": False,
                }
                results.append(result)

        return status, results

    def print_solution(self, status: int, results: tuple[int, list[dict]]) -> None:
        if status == cp_model.OPTIMAL:
            print("Found optimal solution!")
        elif status == cp_model.FEASIBLE:
            print("Found a feasible solution.")
        else:
            print("No solution found.")

        selected_results = [r for r in results if r.get("selected", True)]
        print(
            f"\nScheduled {len(selected_results)} out of {len(self.__requests)} image captures:"
        )

        total_memory = 0
        total_priority = 0
        prev_end_time = 0

        for idx, r in enumerate(selected_results):
            if r["selected"]:
                print(
                    f"{r['location']} (Priority {r['priority']}): Start at {r['start_time']}s, Duration: {r['duration']}s, Time window: {r['time_window']}"
                )
                print(
                    f"  Memory used: {r['memory_used']:.2f} GB, Travel time from previous: {r['travel_time']}s"
                )
                if idx == len(selected_results) - 1:
                    effective_end = r["start_time"] + r["duration"]

                    print("  No recalibration.")
                else:
                    effective_end = (
                        r["start_time"]
                        + r["duration"]
                        + self.__satellite.recalibration_time_s
                    )

                    print(
                        f"  Recalibration time: {self.__satellite.recalibration_time_s}s"
                    )
                print(f"  End task at: {effective_end}s")

                if idx > 0:
                    print(
                        f"  Time since previous task: {r['start_time'] - prev_end_time}s"
                    )

                prev_end_time = effective_end

                print()

                total_memory += r["memory_used"]
                total_priority += r["priority"]

        print(
            f"Total memory used: {total_memory:.2f} GB out of {self.__satellite.memory_capacity_gb} GB"
        )
        print(f"Total priority score: {total_priority}")

        unscheduled = [r for r in results if not r.get("selected", True)]
        if unscheduled:
            print("\nUnscheduled locations:")
            for r in unscheduled:
                print(f"{r['location']} (Priority {r['priority']})")
