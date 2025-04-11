import time

from sims.constraints import get_required_number_of_houses, constraint_enabled, get_required_number_of_fire_station
from sims.options import Opt, get
from sims.constraints import constraint_enabled, get_required_number_of_houses, get_required_number_of_hospitals, get_number_of_houses_required_near_hospital, get_required_number_of_harbours, get_required_number_of_supermarkets, get_required_number_of_factories
from sims.utils import Tile
import sims.generator as generator
from ortools.sat.python import cp_model
import random
from typing import List, Tuple

# VARIABLES DE GENERATION

BUILD_NEXT_ROAD = None
BUILD_HOSPITALS = None
BUILD_FACTORIES = None
BUILD_FIRE_STATIONS = None
BUILD_HARBOUR = None
BUILD_TOWN_HALL = None
BUILD_SUPERMARKETS = None

NB_HOUSE = None
CAPACITY_HOUSE = None

NB_HOSPITAL = None
RADIUS_HOSPITAL = 3
CAPACITY_HOSPITAL = None

NB_FACTORY = None
DISTANCE_HOUSE_FACTORY = None

NB_FIRE_STATION = None
CAPACITY_FIRE_STATION = None
RADIUS_FIRE_STATION = None

NB_HARBOUR = None

NB_SUPERMARKET = None
SUPERMARKETS_ALIGNED = None
MAX_SHOP_DISTANCE = 1

NB_TOWN_HALL = 1
RADIUS_TOWN_HALL = 1
REQUIRED_NB_TILE_TOWN_HALL = 1

CROSS_CONSTRAINT_RADIUS = 1
CROSS_CONSTRAINT = 1
#AROUND_CONSTRAINT_RADIUS = 1
#AROUND_CONSTRAINT = 3

HOSPITAL_SHAPES = [
    [(0, 0), (0, 1), (1, 0)],
    [(0, 0), (1, 0), (1, -1)],
    [(0, 0), (0, -1), (1, 0)],
    [(0, 0), (-1, 0), (0, 1)]
]

PORT_SHAPES = [
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(0, 0), (1, 0), (2, 0), (3, 0)]
]

def count_neighbors(grid: List[List[int]], x: int, y: int, radius: int, tile:Tile, cross_only: bool = False) -> int:
    rows, cols = len(grid), len(grid[0])
    count = 0
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if dx == 0 and dy == 0:
                continue
            if cross_only and abs(dx) + abs(dy) != 1:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == tile:
                count += 1
    return count

def has_water_contact(grid: List[List[int]], cells: List[Tuple[int, int]]) -> bool:
    for x, y in cells:
        if count_neighbors(grid, x, y, 1, Tile.WATER, cross_only=True) >= 1:
            return True
    return False

def has_road_contact(grid: List[List[int]], cells: List[Tuple[int, int]]) -> bool:
    for x, y in cells:
        if count_neighbors(grid, x, y, 1, Tile.ROAD, cross_only=True) >= 1:
            return True
    return False

def cross_constraint(model: cp_model.CpModel, grid: List[List[int]], var: cp_model.IntVar, x: int, y: int, tile: Tile, required: int, radius: int = 1) -> None:
    if count_neighbors(grid, x, y, radius, tile, cross_only=True) < required:
        model.Add(var == 0)

def around_constraint(model: cp_model.CpModel, grid: List[List[int]], var: cp_model.IntVar, x: int, y: int, tile: Tile, required: int, radius: int = 1) -> None:
    if count_neighbors(grid, x, y, radius, tile, cross_only=False) < required:
        model.Add(var == 0)

def factory_isolation_constraint(model: cp_model.CpModel, houses: List[Tuple[cp_model.IntVar, int, int]],
                                 var: cp_model.IntVar, fx: int, fy: int, min_distance: int):
    for hvar, hx, hy in houses:
        if abs((fx - hx) + (fy - hy)) < min_distance:
            model.AddImplication(var, hvar.Not())

def register_occupation(cells, var, occupied):
    for x, y in cells:
        occupied.setdefault((x, y), []).append(var)

def is_valid_cell(x, y, rows, cols):
    return 0 <= x < rows and 0 <= y < cols

def create_single_tile_building(model, grid, rows, cols, name, collection, occupied, constraint_fn=None):
    for x in range(rows):
        for y in range(cols):
            if grid[x][y] != Tile.NONE:
                continue
            var = model.NewBoolVar(f"{name}_{x}_{y}")
            collection.append((var, x, y))
            register_occupation([(x, y)], var, occupied)
            if constraint_fn:
                constraint_fn(var, x, y)

def create_shape_buildings(model, grid, rows, cols, name, shapes, collection, capacity_dict, capacity_value, occupied):
    for x in range(rows):
        for y in range(cols):
            for shape_id, shape in enumerate(shapes):
                cells = [(x + dx, y + dy) for dx, dy in shape]
                if all(is_valid_cell(nx, ny, rows, cols) and grid[nx][ny] == Tile.NONE for nx, ny in cells):
                    var = model.NewBoolVar(f"{name}_{x}_{y}_shape{shape_id}")
                    collection.append((var, x, y, shape_id))
                    capacity_dict[(x, y, shape_id)] = capacity_value
                    register_occupation(cells, var, occupied)

                    if BUILD_NEXT_ROAD:
                        x, y = cells[0]
                        cross_constraint(model, grid, var, x, y, Tile.ROAD, required=1, radius=1)


def add_houses(model, grid, rows, cols, houses, house_capacities, occupied):
    def constraint(var, x, y):
        if BUILD_NEXT_ROAD:
            cross_constraint(model, grid, var, x, y, Tile.ROAD, CROSS_CONSTRAINT, CROSS_CONSTRAINT_RADIUS)
        house_capacities[(x, y)] = CAPACITY_HOUSE
    create_single_tile_building(model, grid, rows, cols, "house", houses, occupied, constraint)

def add_supermarkets(model, grid, rows, cols, supermarkets, houses, occupied):
    def is_close_to_aligned_house(x, y):
        for _, hx, hy in houses:
            if (hx == x and abs(hy - y) <= MAX_SHOP_DISTANCE) or (hy == y and abs(hx - x) <= MAX_SHOP_DISTANCE):
                return True
        return False

    for x in range(rows):
        for y in range(cols):
            if grid[x][y] != Tile.NONE:
                continue
            if SUPERMARKETS_ALIGNED and not is_close_to_aligned_house(x, y):
                continue

            var = model.NewBoolVar(f"supermarket_{x}_{y}")
            supermarkets.append((var, x, y))
            register_occupation([(x, y)], var, occupied)
            if BUILD_NEXT_ROAD:
                cross_constraint(model, grid, var, x, y, Tile.ROAD, required=1, radius=1)

def add_factories(model, grid, rows, cols, factories, houses, occupied):
    def constraint(var, x, y):
        factory_isolation_constraint(model, houses, var, x, y, DISTANCE_HOUSE_FACTORY)
        if BUILD_NEXT_ROAD:
            cross_constraint(model, grid, var, x, y, Tile.ROAD, CROSS_CONSTRAINT, CROSS_CONSTRAINT_RADIUS)
    create_single_tile_building(model, grid, rows, cols, "factory", factories, occupied, constraint)

def add_fire_stations(model, grid, rows, cols, fire_stations, occupied):
    def constraint(var, x, y):
        if BUILD_NEXT_ROAD:
            cross_constraint(model, grid, var, x, y, Tile.ROAD, CROSS_CONSTRAINT, CROSS_CONSTRAINT_RADIUS)
    create_single_tile_building(model, grid, rows, cols, "firestation", fire_stations, occupied, constraint)

def add_town_hall(model, grid, rows, cols, town_hall, occupied):
    def constraint(var, x, y):
        # Exige au moins 1 route en contact direct (comme une maison)
        if BUILD_NEXT_ROAD:
            cross_constraint(model, grid, var, x, y, Tile.ROAD, REQUIRED_NB_TILE_TOWN_HALL, RADIUS_TOWN_HALL)
    create_single_tile_building(model, grid, rows, cols, "mayor", town_hall, occupied, constraint)

def add_hospitals(model, grid, rows, cols, hospitals, hospital_capacities, occupied):
    create_shape_buildings(model, grid, rows, cols, "hospital", HOSPITAL_SHAPES, hospitals, hospital_capacities, CAPACITY_HOSPITAL, occupied)

def add_harbours(model, grid, rows, cols, ports, occupied):
    for x in range(rows):
        for y in range(cols):
            for shape in PORT_SHAPES:
                cells = [(x + dx, y + dy) for dx, dy in shape]
                if all(is_valid_cell(nx, ny, rows, cols) and grid[nx][ny] == Tile.WATER for nx, ny in cells):
                    if has_road_contact(grid, cells):
                        var = model.NewBoolVar(f"port_{x}_{y}")
                        ports.append((var, cells))
                        register_occupation(cells, var, occupied)

def add_constraints(model, rows, cols, houses, hospitals, factories, fire_stations, ports, town_hall, supermarkets, house_capacities, hospital_capacities, occupied):

    for vars_in_cell in occupied.values():
        model.Add(sum(vars_in_cell) <= 1)

    model.Add(sum(var for var, _, _ in houses) == NB_HOUSE)

    if BUILD_HOSPITALS:
        model.Add(sum(var for var, _, _, _ in hospitals) == NB_HOSPITAL)

    if BUILD_FACTORIES:
        model.Add(sum(var for var, _, _ in factories) == NB_FACTORY)

    if BUILD_FIRE_STATIONS:
        model.Add(sum(var for var, _, _ in fire_stations) == NB_FIRE_STATION)

    if BUILD_HARBOUR:
        model.Add(sum(var for var, _ in ports) == NB_HARBOUR)

    if BUILD_TOWN_HALL:
        model.Add(sum(var for var, _, _ in town_hall) == NB_TOWN_HALL)

    if BUILD_SUPERMARKETS:
        model.Add(sum(var for var, _, _ in supermarkets) == NB_SUPERMARKET)

    if BUILD_SUPERMARKETS and SUPERMARKETS_ALIGNED:
        for svar, sx, sy in supermarkets:
            aligned_nearby_houses = [
                hvar for hvar, hx, hy in houses
                if (hx == sx and abs(hy - sy) <= MAX_SHOP_DISTANCE)
                or (hy == sy and abs(hx - sx) <= MAX_SHOP_DISTANCE)
            ]
            if aligned_nearby_houses:
                model.AddBoolOr(aligned_nearby_houses).OnlyEnforceIf(svar)

    if BUILD_HOSPITALS:
        for var, hx, hy in houses:
            in_range = []
            for hvar, x, y, shape_id in hospitals:
                for dx, dy in HOSPITAL_SHAPES[shape_id]:
                    if abs(hx - (x + dx)) + abs(hy - (y + dy)) <= RADIUS_HOSPITAL:
                        in_range.append(hvar)
                        break
            if in_range:
                model.AddBoolOr(in_range).OnlyEnforceIf(var)

    if BUILD_FACTORIES:
        for fvar, fx, fy in factories:
            covered_by = [cvar for cvar, cx, cy in fire_stations if abs(fx - cx) + abs(fy - cy) <= RADIUS_FIRE_STATION]
            if covered_by:
                model.AddBoolOr(covered_by).OnlyEnforceIf(fvar)

    if BUILD_FIRE_STATIONS:
        for cvar, cx, cy in fire_stations:
            nearby_factories = [
                fvar for fvar, fx, fy in factories
                if abs(fx - cx) + abs(fy - cy) <= RADIUS_FIRE_STATION
            ]
            model.Add(sum(nearby_factories) <= CAPACITY_FIRE_STATION)

    if BUILD_HOSPITALS:
        population_terms = [var * house_capacities[(x, y)] for var, x, y in houses]
        hospital_capacity_terms = [hvar * hospital_capacities[(x, y, shape_id)] for hvar, x, y, shape_id in hospitals]
        model.Add(sum(hospital_capacity_terms) >= sum(population_terms))

    weights = {(x, y): 1.0 / (1 + abs(x - rows // 2) + abs(y - cols // 2)) for _, x, y in houses}
    model.Maximize(sum(weights[(x, y)] * var for var, x, y in houses))

    if BUILD_SUPERMARKETS:
        total_supermarkets = sum(var for var, _, _ in supermarkets)
        model.Add(total_supermarkets * 100 >= NB_HOUSE * CAPACITY_HOUSE)


def create_model(grid: List[List[int]]) -> Tuple:
    model = cp_model.CpModel()
    rows, cols = len(grid), len(grid[0])

    houses, hospitals, factories, fire_stations, ports, town_hall, supermarkets = [], [], [], [], [], [], []
    house_capacities, hospital_capacities, occupied = {}, {}, {}

    add_houses(model, grid, rows, cols, houses, house_capacities, occupied)

    if BUILD_HOSPITALS:
        add_hospitals(model, grid, rows, cols, hospitals, hospital_capacities, occupied)

    if BUILD_FACTORIES:
        add_factories(model, grid, rows, cols, factories, houses, occupied)

    if BUILD_FIRE_STATIONS:
        add_fire_stations(model, grid, rows, cols, fire_stations, occupied)

    if BUILD_HARBOUR:
        add_harbours(model, grid, rows, cols, ports, occupied)

    if BUILD_TOWN_HALL:
        add_town_hall(model, grid, rows, cols, town_hall, occupied)

    if BUILD_SUPERMARKETS:
        add_supermarkets(model, grid, rows, cols, supermarkets, houses, occupied)

    add_constraints(model, rows, cols, houses, hospitals, factories, fire_stations, ports, town_hall, supermarkets, house_capacities, hospital_capacities, occupied)

    return model, houses, hospitals, factories, fire_stations, ports, town_hall, supermarkets


def solve_model(model: cp_model.CpModel, houses, hospitals, factories, fire_stations, ports, town_hall, supermarkets, grid):
    solver = cp_model.CpSolver()
    solver.parameters.random_seed = random.randint(0, 100000)
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for var, x, y in houses:
            if solver.Value(var):
                grid[x][y] = Tile.HOUSE
        for var, x, y, shape_id in hospitals:
            if solver.Value(var):
                for dx, dy in HOSPITAL_SHAPES[shape_id]:
                    nx, ny = x + dx, y + dy
                    grid[nx][ny] = Tile.HOSPITAL
        for var, x, y in factories:
            if solver.Value(var):
                grid[x][y] = Tile.FACTORY
        for var, x, y in fire_stations:
            if solver.Value(var):
                grid[x][y] = Tile.FIRE_STATION
        for var, cells in ports:
            if solver.Value(var):
                for x, y in cells:
                    grid[x][y] = Tile.HARBOUR
        for var, x, y in town_hall:
            if solver.Value(var):
                grid[x][y] = Tile.TOWN_HALL
        for var, x, y in supermarkets:
            if solver.Value(var):
                grid[x][y] = Tile.SUPERMARKET
    else:
        return False, None
    return True, grid

def set_parameters():
    global BUILD_NEXT_ROAD, BUILD_HOSPITALS, BUILD_FACTORIES, BUILD_FIRE_STATIONS
    global BUILD_HARBOUR, BUILD_TOWN_HALL, BUILD_SUPERMARKETS
    global NB_HOUSE, CAPACITY_HOUSE, NB_HOSPITAL, CAPACITY_HOSPITAL
    global NB_FACTORY, DISTANCE_HOUSE_FACTORY
    global NB_FIRE_STATION, CAPACITY_FIRE_STATION, RADIUS_FIRE_STATION
    global NB_HARBOUR, NB_SUPERMARKET, SUPERMARKETS_ALIGNED

    BUILD_NEXT_ROAD = constraint_enabled(Opt.BUILDINGS_NEXT_TO_AT_LEAST_A_ROAD)
    BUILD_HOSPITALS = constraint_enabled(Opt.HOSPITALS_ENABLED)
    BUILD_FACTORIES = constraint_enabled(Opt.FACTORIES_ENABLED)
    BUILD_FIRE_STATIONS = constraint_enabled(Opt.FIRE_STATIONS_ENABLED)
    BUILD_HARBOUR = constraint_enabled(Opt.HARBOURS_ENABLED)
    BUILD_TOWN_HALL = constraint_enabled(Opt.TOWN_HALL_ENABLED)
    BUILD_SUPERMARKETS = constraint_enabled(Opt.SUPERMARKETS_ENABLED)

    NB_HOUSE = get_required_number_of_houses()
    CAPACITY_HOUSE = get(Opt.HOUSE_CAPACITY)

    NB_HOSPITAL = get_required_number_of_hospitals()
    CAPACITY_HOSPITAL = get(Opt.HOSPITAL_CAPACITY)

    NB_FACTORY = get_required_number_of_factories()
    DISTANCE_HOUSE_FACTORY = get(Opt.DISTANCE_HOUSE_FACTORY)

    NB_FIRE_STATION = get_required_number_of_fire_station()
    CAPACITY_FIRE_STATION = get(Opt.FIRE_STATION_CAPACITY)
    RADIUS_FIRE_STATION = get(Opt.FIRE_STATION_RADIUS)

    NB_HARBOUR = get_required_number_of_harbours()

    NB_SUPERMARKET = get_required_number_of_supermarkets()
    SUPERMARKETS_ALIGNED = constraint_enabled(Opt.SUPERMARKETS_ALIGNED_WITH_CLIENTS)


def ortools_solveur(grid : list[list[int]]) -> Tuple[bool, list[list[int]]]:
    set_parameters()
    start = time.time()
    print("Model creation")
    model, houses, hospitals, factories, fire_stations, ports, town_hall, supermarkets = create_model(grid)
    duration = time.time() - start
    print(f"Model creation time : {duration:.3f} s")
    start = time.time()
    print("Model resolution")
    res = solve_model(model, houses, hospitals, factories, fire_stations, ports, town_hall, supermarkets, grid)

    duration = time.time() - start
    print(f"Model resolution time : {duration:.3f} s")

    if res[0]:
        print("Solved", flush=True)
    else:
        print('OR-Tools could not find a solution.')
    return res

generator.register_solver_func("OR-TOOLS", ortools_solveur)
