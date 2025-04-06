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
    LENS_CALIBRATION = "Lens Calibration"
    

class Task:
    def __init__(self, task_id, task_type: TaskType, duration, priority=0, location=None, memory_required=0, battery_required=0):
        self.task_id = task_id
        self.task_type = task_type
        self.duration = duration
        self.priority = priority
        self.location = location
        self.memory_required = memory_required
        self.battery_required = battery_required

    
class Track:
    def __init__(self, start_time, duration, zones):
        self.start_time = start_time
        self.duration = duration
        self.zones = zones  # List of zones the satellite will pass over

    def get_zone_by_name(self, name):
        for zone in self.zones:
            if zone.name == name:
                return zone
        return None
    
    
class Zone:
    def __init__(self, name, coordinates, visibility_window, has_ground_station=False):
        self.name = name 
        self.coordinates = coordinates  # GPS coordinates (latitude, longitude)e
        self.visibility_window = visibility_window  # Time window when the zone is visible (start_time, end_time)
        self.has_ground_station  = has_ground_station  # True if the zone has a ground station for data transmission

    def is_visible(self, current_time):
        start, end = self.visibility_window
        return start <= current_time <= end
    
class SatelliteScheduler:
    def __init__(self, satellite, images_to_capture, track):
        self.satellite = satellite
        self.images_to_capture = images_to_capture  # Liste des images à capturer
        self.track = track  # Liste des zones à survoler
        self.model = cp_model.CpModel()
        self.task_starts = {}
        self.task_done = {}
        self.tasks = []
        self.solver = cp_model.CpSolver()
        self.execution_log = []  # Journal des tâches effectuées

    def solve(self):
        # Create variables for task start times and completion
        for task_id, task in self.images_to_capture.items():
            start_var = self.model.NewIntVar(0, self.track.duration, f'start_{task_id}')
            done_var = self.model.NewBoolVar(f'done_{task_id}')
            self.task_starts[task_id] = start_var
            self.task_done[task_id] = done_var
            self.tasks.append((task, start_var, done_var))

        # Add constraints for visibility windows
        for task_id, task in self.images_to_capture.items():
            zone = self.track.get_zone_by_name(task.location)
            if zone:
                start, end = zone.visibility_window
                self.model.Add(self.task_starts[task_id] >= start).OnlyEnforceIf(self.task_done[task_id])
                self.model.Add(self.task_starts[task_id] + task.duration <= end).OnlyEnforceIf(self.task_done[task_id])

        # Add constraints for satellite memory and battery
        for task, start_var, done_var in self.tasks:
            self.model.Add(self.satellite.memory_used + task.memory_required <= self.satellite.memory_capacity).OnlyEnforceIf(done_var)
            self.model.Add(self.satellite.battery_level >= task.battery_required).OnlyEnforceIf(done_var)

        # Add precedence constraints (tasks must not overlap)
        for i, (task1, start_var1, done_var1) in enumerate(self.tasks):
            for j, (task2, start_var2, done_var2) in enumerate(self.tasks):
                if i != j:
                    self.model.Add(start_var1 + task1.duration <= start_var2).OnlyEnforceIf([done_var1, done_var2])
                    self.model.Add(start_var2 + task2.duration <= start_var1).OnlyEnforceIf([done_var2, done_var1])

        # Objective: Maximize priority of completed tasks
        self.model.Maximize(
            sum(task.priority * done_var for task, _, done_var in self.tasks)
        )

        # Solve the model
        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("Solution found!")
            for task, start_var, done_var in self.tasks:
                if self.solver.Value(done_var):
                    start_time = self.solver.Value(start_var)
                    self.execution_log.append({
                        "task_id": task.task_id,
                        "type": task.task_type.value,
                        "location": task.location,
                        "start_time": start_time
                    })
                    print(f"Task {task.task_id} starts at {start_time}")
        else:
            print("No solution found.")

    def print_execution_log(self):
        print("\n **Journal des tâches exécutées :**")
        for log in self.execution_log:
            print(f"[{log['start_time']}s] {log['type']} à {log['location']} (ID: {log['task_id']})")


# Satellite :
satellite = Satellite(name="Sat-1", memory_capacity=100, battery_level=100)

# Images à capturer :
images_to_capture = {
    "image1": Task(task_id="image1", task_type=TaskType.IMAGE_CAPTURE, duration=5, priority=10, location="Zone A", memory_required=10, battery_required=5),
    "image2": Task(task_id="image2", task_type=TaskType.IMAGE_CAPTURE, duration=5, priority=20, location="Zone B", memory_required=10, battery_required=5),
    "image3": Task(task_id="image3", task_type=TaskType.IMAGE_CAPTURE, duration=5, priority=15, location="Zone C", memory_required=10, battery_required=5),
    "image4": Task(task_id="image4", task_type=TaskType.IMAGE_CAPTURE, duration=5, priority=5, location="Zone D", memory_required=10, battery_required=5),
    "image5": Task(task_id="image5", task_type=TaskType.IMAGE_CAPTURE, duration=5, priority=25, location="Zone E", memory_required=10, battery_required=5),
}

# Zones :
zones = [
    Zone(name="Zone A", coordinates=(10, 20), visibility_window=(0, 30), has_ground_station=True),
    Zone(name="Zone B", coordinates=(15, 25), visibility_window=(5, 35), has_ground_station=False),
    Zone(name="Zone C", coordinates=(20, 30), visibility_window=(10, 40), has_ground_station=True),
    Zone(name="Zone D", coordinates=(25, 35), visibility_window=(15, 45), has_ground_station=False),
    Zone(name="Zone E", coordinates=(30, 40), visibility_window=(20, 50), has_ground_station=True),
]

# Track :
track = Track(start_time=0, duration=60, zones=zones)

scheduler = SatelliteScheduler(satellite, images_to_capture, track)
scheduler.solve()
scheduler.print_execution_log()

