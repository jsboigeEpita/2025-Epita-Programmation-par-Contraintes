import numpy as np
import ortools
from ortools.sat.python import cp_model
from enum import Enum



class Satellite:
    def __init__(self, name, memory_capacity, battery_level):
        self.name = name
        self.memory_capacity = memory_capacity
        self.memory_used = 0
        self.battery_level = battery_level
        self.tasks_queue = []
        self.current_task = None

    def can_perform_task(self, task):

        if self.battery_level >= task.battery_required and self.memory_used + task.memory_required <= self.memory_capacity:
            return True
        
        return False
    
    def add_task(self, task):
        if self.memory_used + task.memory_required <= self.memory_capacity:
            self.tasks_queue.append(task)


class TaskType(Enum):
    IMAGE_CAPTURE = "Image Capture"
    DATA_TRANSMISSION = "Data Transmission"
    MAINTENANCE = "Maintenance"
    LENS_CALIBRATION = "Lens Calibration"
    

class Task:
    def __init__(self, task_id, task_type: TaskType, duration, priority, location=None, memory_required=0, battery_required=0):
        self.task_id = task_id
        self.task_type = task_type
        self.duration = duration
        self.priority = priority
        self.location = location
        self.memory_required = memory_required
        self.battery_required = battery_required

    
class Track:
    def __init__(self, satellite, start_time, duration, zones):
        self.satellite = satellite
        self.start_time = start_time
        self.duration = duration
        self.zones = zones  # List of zones the satellite will pass over

    def get_zone_by_name(self, name):
        for zone in self.zones:
            if zone.name == name:
                return zone
        return None
    
    
class Zone:
    def __init__(self, name, coordinates, visibility_window, priority, has_ground_station=False):
        self.name = name 
        self.coordinates = coordinates  # GPS coordinates (latitude, longitude)e
        self.visibility_window = visibility_window  # Time window when the zone is visible
        self.priority = priority 
        self.has_ground_station  = has_ground_station  # True if the zone has a ground station for data transmission

    def is_visible(self, current_time):
        start, end = self.visibility_window
        return start <= current_time <= end
    

class SatelliteScheduler:
    def __init__(self, tasks, zones, memory_capacity, battery_capacity, time_horizon):
        self.tasks = tasks
        self.zones = zones
        self.memory_capacity = memory_capacity
        self.battery_capacity = battery_capacity
        self.time_horizon = time_horizon
        self.model = cp_model.CpModel()
        self.task_starts = {}
        self.task_done = {}
        self.solver = cp_model.CpSolver()

    def define_variables(self):
        for task in self.tasks:
            self.task_starts[task.task_id] = self.model.NewIntVar(0, self.time_horizon, f"start_{task.task_id}")
            self.task_done[task.task_id] = self.model.NewBoolVar(f"done_{task.task_id}")

    def add_constraints(self):
        memory_used = [self.model.NewIntVar(0, self.memory_capacity, f"memory_{t}") for t in range(self.time_horizon)]
        battery_used = [self.model.NewIntVar(0, self.battery_capacity, f"battery_{t}") for t in range(self.time_horizon)]

        for t in range(1, self.time_horizon):
            self.model.Add(memory_used[t] == memory_used[t-1])
            self.model.Add(battery_used[t] == battery_used[t-1])

        for task in self.tasks:
            start_var = self.task_starts[task.task_id]
            done_var = self.task_done[task.task_id]

            zone = next((z for z in self.zones if z.name == task.location), None)
            if zone:
                self.model.Add(start_var >= zone.visibility_window[0]).OnlyEnforceIf(done_var)
                self.model.Add(start_var + task.duration <= zone.visibility_window[1]).OnlyEnforceIf(done_var)

            if task.task_type == TaskType.IMAGE_CAPTURE:
                self.model.Add(memory_used[start_var] + task.memory_required <= self.memory_capacity).OnlyEnforceIf(done_var)
                self.model.Add(battery_used[start_var] + task.battery_required <= self.battery_capacity).OnlyEnforceIf(done_var)

                # Calibration obligatoire avant la capture
                has_calibration = any(t.task_type == TaskType.LENS_CALIBRATION for t in self.tasks if t.task_id < task.task_id)
                if has_calibration:
                    calibration_task = next(t for t in self.tasks if t.task_type == TaskType.LENS_CALIBRATION and t.task_id < task.task_id)
                    self.model.Add(start_var >= self.task_starts[calibration_task.task_id] + calibration_task.duration).OnlyEnforceIf(done_var)

            if task.task_type == TaskType.DATA_TRANSMISSION:
                self.model.Add(memory_used[start_var] == 0).OnlyEnforceIf(done_var)
                self.model.Add(battery_used[start_var] + task.battery_required <= self.battery_capacity).OnlyEnforceIf(done_var)

    def set_objective(self):
        self.model.Maximize(sum(task.priority * self.task_done[task.task_id] for task in self.tasks))

    def solve(self):
        self.define_variables()
        self.add_constraints()
        self.set_objective()
        status = self.solver.Solve(self.model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("Solution trouvée !")
            for task in self.tasks:
                if self.solver.Value(self.task_done[task.task_id]):
                    print(f"Tâche {task.task_id} ({task.task_type.value}) exécutée à {self.solver.Value(self.task_starts[task.task_id])}")
        else:
            print("Pas de solution trouvée.")

# === Définition des tâches et zones ===

zones = [
    Zone("Paris", (48.8566, 2.3522), visibility_window=(10, 20), priority=10),
    Zone("Tokyo", (35.682839, 139.759455), visibility_window=(25, 35), priority=15, has_ground_station=True),
]

tasks = [
    Task(0, TaskType.LENS_CALIBRATION, duration=2, priority=0),
    Task(1, TaskType.IMAGE_CAPTURE, duration=5, priority=10, location="Paris", memory_required=5, battery_required=10),
    Task(2, TaskType.IMAGE_CAPTURE, duration=4, priority=12, location="Tokyo", memory_required=6, battery_required=8),
    Task(3, TaskType.DATA_TRANSMISSION, duration=3, priority=0, location="Tokyo", battery_required=5),
]

scheduler = SatelliteScheduler(tasks, zones, memory_capacity=10, battery_capacity=50, time_horizon=40)
scheduler.solve()
