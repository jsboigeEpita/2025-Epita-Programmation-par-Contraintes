from noise import pnoise2
from sims.utils import Tile
from sims.options import Opt, get
import random

TRESH = 0.95

def generate_river(grid : list[list[int]]) -> list[list[int]]:
    grid_width, grid_height = get(Opt.GRID_WIDTH), get(Opt.GRID_HEIGHT)
    
    seed = random.randint(0, 1000)
    x = random.randint(0, 1000)
    y = random.randint(0, 1000)

    SCALE = random.randint(25, 50)

    # Génération du bruit Perlin et transformation en ridge noise
    for i in range(grid_height):
        for j in range(grid_width):
            # Génération du bruit Perlin
            noise_value = pnoise2(x + i / SCALE, y + j / SCALE, octaves=2, persistence=0.5, lacunarity=2.0, base=seed)
            # Application du ridge noise (inverser la valeur absolue)
            ridge = 1 - abs(noise_value)

            if ridge > TRESH and grid[i][j] == Tile.NONE:
                grid[i][j] = Tile.WATER
    
    return grid
