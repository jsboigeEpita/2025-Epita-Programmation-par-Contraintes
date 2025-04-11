import random
import numpy as np

from sims.utils import Tile
import sims.generator as generator
from sims.options import Opt, get

DIRS = [(0, 2), (2, 0), (0, -2), (-2, 0)]
DIRS1 = [(0, 1), (1, 0), (0, -1), (-1, 0)]

def flood_fill(grid, flooded, x_start, y_start, i):
    grid_width, grid_height = get(Opt.GRID_WIDTH), get(Opt.GRID_HEIGHT)
    toVisit = [(x_start,y_start)]
    while toVisit:
        x,y = toVisit.pop()

        if flooded[y][x] == i or grid[y][x] == Tile.WATER:
            continue

        flooded[y][x] = i

        for dx, dy in DIRS1:
            xx = x + dx
            yy = y + dy

            if xx < 0 or yy < 0 or xx >= grid_width or yy >= grid_height:
                continue

            toVisit.append((xx,yy))

def is_near_water(grid, x, y):
    grid_width, grid_height = get(Opt.GRID_WIDTH), get(Opt.GRID_HEIGHT)
    for dx, dy in DIRS:
        xx = x + dx
        yy = y + dy

        if xx < 0 or yy < 0 or xx >= grid_width or yy >= grid_height:
            continue

        if grid[yy][xx] == Tile.WATER:
            return True

    return False

def _generate_road(grid, start_x, start_y): 
    grid_width, grid_height = get(Opt.GRID_WIDTH), get(Opt.GRID_HEIGHT)

    grid[start_y][start_x] = Tile.ROAD
    walls = [(start_x + dx, start_y + dy) for dx, dy in DIRS]
    near_water = set()
    
    while walls:
        wx, wy = random.choice(walls)
        walls.remove((wx, wy))

        if 0 < wx < grid_width-1 and 0 < wy < grid_height-1 and grid[wy][wx] == Tile.NONE:
            neighbors = []
            if wx >= 2 and grid[wy][wx - 2] == Tile.ROAD:
                neighbors.append((wx - 2, wy))
            if wx < grid_width - 2 and grid[wy][wx + 2] == Tile.ROAD:
                neighbors.append((wx + 2, wy))
            if wy >= 2 and grid[wy - 2][wx] == Tile.ROAD:
                neighbors.append((wx, wy - 2))
            if wy < grid_height - 2 and grid[wy + 2][wx] == Tile.ROAD:
                neighbors.append((wx, wy + 2))

            if len(neighbors) == 1:
                nx, ny = neighbors[0]
                if grid[ny][nx] == Tile.WATER:
                    continue
                midY = (wy + ny)//2
                midX = (wx + nx)//2

                if grid[midY][midX] != Tile.NONE:
                    continue

                grid[wy][wx] = Tile.ROAD
                grid[midY][midX] = Tile.ROAD

                near_water.add((wx, wy))
                near_water.add((midX, midY))

                for dx, dy in DIRS:
                    new_wx, new_wy = wx + dx, wy + dy
                    if 0 <= new_wx < grid_width and 0 <= new_wy < grid_height:
                        if grid[new_wy][new_wx] == Tile.NONE:
                            walls.append((new_wx, new_wy))

    return grid, near_water

def generate_labyrinth_roads(grid) -> list[list[int]]:
    grid_width, grid_height = get(Opt.GRID_WIDTH), get(Opt.GRID_HEIGHT)
    flooded = np.zeros_like(grid)
    roads = set()
    set_i = 1
    prev_road = []

    for x in range(1, grid_width):
        for y in range(1, grid_height):
            if grid[y][x] == Tile.WATER:
                continue

            if flooded[y][x] > 0:
                continue

            if is_near_water(grid, x, y):
                continue

            grid, near_water = _generate_road(grid, x, y)

            flood_fill(grid, flooded, x, y, set_i)
            set_i += 1

            prev_road.append(np.array(list(near_water)))
                             
    for i in range(1, len(prev_road)):
        A, B = prev_road[i - 1], prev_road[i]

        dists = np.linalg.norm(A[:, None] - B[None, :], axis=2)
        i, j = np.unravel_index(np.argmin(dists), dists.shape)
        
        sx, sy = A[i]
        ex, ey = B[j]
        
        # Convert to integers (after swapping if needed)        
        sx, sy, ex, ey = map(int, (sx, sy, ex, ey))

        dx = 1 if sx < ex else -1
        dy = 1 if sy < ey else -1

        while sx != ex:
            roads.add((sx, sy))
            grid[sy][sx] = Tile.ROAD
            sx += dx

        while sy != ey:
            roads.add((sx, sy))
            grid[sy][sx] = Tile.ROAD
            sy += dy

    return grid, roads

generator.register_road_generation_func('LABYRINTH', generate_labyrinth_roads)
