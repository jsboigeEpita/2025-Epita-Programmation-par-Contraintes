import random
from colorama import Fore, Style
class Rack:
    def __init__(self, x, y):
        self.current_position = (x, y)
        self.boxes = []
        self.max_boxes = 5
        self.id = None

    def add_box(self, box):
        if len(self.boxes) < self.max_boxes:
            self.boxes.append(box)
        else:
            print("Rack is full.")

    def remove_box(self, box):
        if box in self.boxes:
            self.boxes.remove(box)
        else:
            print("Box not found in rack.")

class Box:
    id_counter = 0
    def __init__(self, x, y):
        self.current_position = (x, y)
        self.id = Box.id_counter
        self.contents = []
        self.max_contents = 5
        Box.id_counter += 1

class Robot:
    id_counter = 0
    def __init__(self, x, y):
        self.current_position = (x, y)
        self.energy = 100
        self.inventory = []
        self.id = Robot.id_counter
        self.max_inventory = 5
        self.task = None
    
    def set_task(self, task):
        self.task = task

    def complete_task(self):
        if self.task is not None:
            self.task_complete = True
            self.task = None
        else:
            print("No task to complete.")

    def move(self, x, y):
        if self.energy > 0:
            self.current_position = (x, y)
            self.energy -= 1
        else:
            print("Not enough energy to move.")

    def pick_up(self, item):
        if len(self.inventory) < self.max_inventory:
            self.inventory.append(item)
        else:
            print("Inventory full.")
    
    def drop(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
        else:
            print("Item not in inventory.")

class Task:
    def __init__(self, name, time):
        self.name = name
        self.time = time
        self.completed = False

    def complete(self):
        self.completed = True

class Grid:
    def __init__(self, width,height,pattern = 'PV'):
        # Make the dimensions odd
        if width % 2 == 0:
            width += 1

        if height % 2 == 0:
            height += 1
        
        self.width = width
        self.height = height
        print(f"Grid size: {self.width} x {self.height}")

        self.grid = [[' ' for _ in range(width)] for _ in range(height)]

        if pattern == 'PV':
            # Place racks in a parallel vertical pattern
            for i in range(1,height - 1):
                for j in range(1, width - 1, 2):
                    self.grid[i][j] = 'R'
        elif pattern == 'PH':
            # Place racks in a parallel horizontal pattern
            for i in range(1, height - 1, 2):
                for j in range(1, width - 1):
                    self.grid[i][j] = 'R'
            
        elif pattern == 'FBV':
            # Place racks in a Fishbone pattern vertically
            for i in range(1, height - 1, 4):  # Step every 4 rows for horizontal racks
                for j in range(1, width - 1):
                    self.grid[i][j] = 'R'  # Horizontal racks

            for i in range(3, height - 1, 4):  # Step every 4 rows for diagonal racks
                for j in range(1, width - 1, 2):  # Diagonal racks alternate
                    if j + (i % 4) < width - 1:
                        self.grid[i][j + (i % 4)] = 'R'
        elif pattern == 'FBH':
            # Place racks in a Fishbone pattern horizontally
            for i in range(1, height - 1):
                for j in range(1, width - 1, 4):
                    self.grid[i][j] = 'R'
            for i in range(1, height - 1, 2):
                for j in range(3, width - 1, 4):
                    if i + (j % 4) < height - 1:
                        self.grid[i + (j % 4)][j] = 'R'
            
        elif pattern == 'R':
            # Place racks in a random pattern
            for i in range(width):
                for j in range(height):
                    if random.random() < 0.5:
                        self.grid[i][j] = 'R'
        else :
            raise ValueError("Invalid pattern. Use 'PV', 'PH', 'S', 'FB', or 'R'.")
    
    def place_robot(self, x,y, robot):
        if self.grid[x][y] == ' ':
            self.grid[x][y] = '🤖'
            robot.current_position = (x, y)
        else:
            print("Cell is occupied.")

    def print_grid(self):
        for row in self.grid:
            print(' '.join(row))

    def place_charging_station(self, x, y):
        if self.grid[x][y] == ' ':
            self.grid[x][y] = 'C'
        else:
            print("Cell is occupied.")



