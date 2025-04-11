from z3 import *
import itertools
from typing import Tuple

from sims.utils import Tile
from sims.options import Opt, get
from sims.constraints import constraint_enabled, get_required_number_of_houses, get_required_number_of_hospitals, get_number_of_houses_required_near_hospital, get_required_number_of_harbours, get_required_number_of_supermarkets, get_required_number_of_factories

import sims.generator as generator    

z3.set_param("timeout", 5000)

def get_neighbors_pos(x, y, w, h):              
    neigh = []
    for (x0, y0) in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
        if x0 >= 0 and x0 < w and y0 >= 0 and y0 < h:
            neigh.append((x0,y0))
    return neigh

def get_neighbors_tiles(grid: list[list[int]], x, y, w, h):
    return [grid[y0][x0] for (x0, y0) in get_neighbors_pos(x, y, w, h)]

def has_neighboring_tile(grid: list[list[int]], x, y, tile : Tile, w, h):
    return tile in get_neighbors_tiles(grid, x, y, w, h) 

def get_positions_of_type(grid : list[list[int]], w, h, of_type : list[Tile]):
    pos = []
    for y, x in itertools.product(range(h), range(w)):
        if grid[y][x] in of_type:
            pos.append((x, y))
    return pos

def get_positions_not_type(grid : list[list[int]], w, h, not_type : list[Tile]):
    pos = []
    for y, x in itertools.product(range(h), range(w)):
        if not grid[y][x] in not_type:
            pos.append((x, y))
    return pos

def get_non_fixed_positions(grid : list[list[int]], w, h, fixed_tiles : list[Tile]):
    return get_positions_not_type(grid, w, h, fixed_tiles)

def get_positions_next_to_road_in_pos(grid : list[list[int]], w, h, pos):
    next_to_road = []
    for x, y in pos:
        if has_neighboring_tile(grid, x, y, Tile.ROAD, w, h): next_to_road.append((x, y))
    return next_to_road

def get_non_fixed_positions_next_to_roads(grid : list[list[int]], w, h, non_fixed):
    return get_positions_next_to_road_in_pos(grid, w, h, non_fixed)

def get_water_positions(grid : list[list[int]], w, h):
    return get_positions_of_type(grid, w, h, [Tile.WATER])

def get_water_positions_next_to_road(grid : list[list[int]], w, h, water_pos):
    return get_positions_next_to_road_in_pos(grid, w, h, water_pos)

def solve(grid : list[list[int]]) -> Tuple[bool, list[list[int]]]:
    w, h = len(grid[0]), len(grid)

    # constrained version of the grid
    s_grid = [[BitVec(f"cell_{y}_{x}", 3) for x in range(w)] for y in range(h)]
    s = Solver()

    fixed_tiles = [ Tile.ROAD, Tile.WATER ]
    buildings_tiles = [ Tile.HOUSE ]
    if constraint_enabled(Opt.HOSPITALS_ENABLED): buildings_tiles += [Tile.HOSPITAL]
    if constraint_enabled(Opt.SUPERMARKETS_ENABLED): buildings_tiles += [Tile.SUPERMARKET]
    if constraint_enabled(Opt.FACTORIES_ENABLED): buildings_tiles += [Tile.FACTORY]
    water_buildings_tiles = [ Tile.HARBOUR ] if constraint_enabled(Opt.HARBOURS_ENABLED) else []
    possible_earth_tiles = [ Tile.NONE ] + buildings_tiles
    possible_water_tiles = [Tile.WATER] + water_buildings_tiles

    non_fixed = get_non_fixed_positions(grid, w, h, fixed_tiles)
    next_to_road = get_non_fixed_positions_next_to_roads(grid, w, h, non_fixed)
    water = get_water_positions(grid, w, h)
    water_next_to_road = get_water_positions_next_to_road(grid, w, h, water)

    def get_possible_pos():
        if constraint_enabled(Opt.BUILDINGS_NEXT_TO_AT_LEAST_A_ROAD): return next_to_road
        else: return non_fixed
        
    def get_possible_water_pos():
        if constraint_enabled(Opt.BUILDINGS_NEXT_TO_AT_LEAST_A_ROAD): return water_next_to_road
        else: return water

    print(get_possible_pos())

    # this basically says which tile can be what in the grid
    for y, x in itertools.product(range(h), range(w)):
        if (x,y) in get_possible_pos():
            s.add(Or([s_grid[y][x] == BitVecVal(dt, 3) for dt in possible_earth_tiles]))
        elif (x,y) in get_possible_water_pos():
            s.add(Or([s_grid[y][x] == BitVecVal(dt, 3) for dt in possible_water_tiles]))
        else:
            s.add(s_grid[y][x] == BitVecVal(grid[y][x], 3))

    nb_buildings = [
        (True, Tile.HOUSE, get_required_number_of_houses()),
        (constraint_enabled(Opt.HOSPITALS_ENABLED), Tile.HOSPITAL, get_required_number_of_hospitals()),
        (constraint_enabled(Opt.HARBOURS_ENABLED), Tile.HARBOUR, get_required_number_of_harbours()),
        (constraint_enabled(Opt.SUPERMARKETS_ENABLED), Tile.SUPERMARKET, get_required_number_of_supermarkets()),
        (constraint_enabled(Opt.FACTORIES_ENABLED), Tile.FACTORY, get_required_number_of_factories()),
    ]

    for b, t, n in nb_buildings:
        if not b: continue
        print(f'There must be {n} {t.name} on the grid.')
        s.add(Sum([If(s_grid[y][x] == BitVecVal(t, 3), 1, 0) for y in range(h) for x in range(w)]) == n)

    def cond_tiles_of_type_in_square_radius(t : BitVecVal, x0, y0, rad, nb):
        result = []
        for dy, dx in itertools.product(range(-rad, rad + 1), range(-rad, rad + 1)):
            if abs(dx) + abs(dy) <= rad:
                x, y = x0 + dx, y0 + dy
                if x >= 0 and x < w and y >= 0 and y < h:
                    result.append((s_grid[y][x] == t, 1))
        return PbGe(result, nb)
    
    def cond_tiles_of_type_in_line(t: BitVecVal, x0, y0, rad, nb):
        result = []
        for x in range(x0 - rad, x0 + rad + 1):
            if x >= 0 and x < w:
                result.append((s_grid[y0][x] == t, 1))
        return PbGe(result, nb)
    
    def cond_tiles_of_type_in_column(t: BitVecVal, x0, y0, rad, nb):
        result = []
        for y in range(y0 - rad, y0 + rad + 1):
            if y >= 0 and y < h:
                result.append((s_grid[y][x0] == t, 1))
        return PbGe(result, nb)

    # tile of type 'source' must have at least n tiles of type 'in_radius' in a radius of 'rad'
    def constraint_n_select_in_square_radius(source : Tile, n : int, rad : int, in_radius : Tile, possible_pos):
        for x, y in possible_pos:
            c = cond_tiles_of_type_in_square_radius(BitVecVal(in_radius, 3), x, y, rad, n)
            s.add(Implies(s_grid[y][x] == BitVecVal(source, 3), c))
            # print(Implies(s_grid[y][x] == BitVecVal(source, 3), c))

    # tile of type 'source' must have at least n tiles of type 'in_radius' in its axis
    def constraint_n_select_in_axis(source : Tile, n : int, rad : int, in_axis : Tile, possible_pos):
        for x, y in possible_pos:
            c_c = cond_tiles_of_type_in_column(BitVecVal(in_axis, 3), x, y, rad, n)
            l_c = cond_tiles_of_type_in_line(BitVecVal(in_axis, 3), x, y, rad, n)
            s.add(Implies(s_grid[y][x] == BitVecVal(source, 3), Or(c_c, l_c)))

    if constraint_enabled(Opt.HOSPITALS_ENABLED) and constraint_enabled(Opt.HOSPITALS_NEAR_PATIENTS):
        n = get_number_of_houses_required_near_hospital()
        print(f'Hospitals must have {n} houses around them in a radius of 3.')
        constraint_n_select_in_square_radius(Tile.HOSPITAL, n, 3, Tile.HOUSE, get_possible_pos())
    
    if constraint_enabled(Opt.HARBOURS_ENABLED):
        constraint_n_select_in_square_radius(Tile.HARBOUR, 1, 1, Tile.WATER, get_possible_water_pos())

    if constraint_enabled(Opt.SUPERMARKETS_ENABLED) and constraint_enabled(Opt.SUPERMARKETS_ALIGNED_WITH_CLIENTS):
        constraint_n_select_in_axis(Tile.SUPERMARKET, 3, 2, Tile.HOUSE, get_possible_pos())

    if constraint_enabled(Opt.FACTORIES_ENABLED):
        constraint_n_select_in_square_radius(Tile.FACTORY, 8, 2, Tile.NONE, get_possible_pos())

    print('Checking satisfiability (solving constraints)...')
    if s.check() == sat:
        print('Solved.', flush=True)
        return True, [[s.model().evaluate(s_grid[y][x]).as_long() for x in range(w)] for y in range(h)]
    else:
        print('Z3 could not find a solution.')
        return False, None
    
generator.register_solver_func('Z3', solve)