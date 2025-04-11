from sims.utils import Tile
import sims.generator as generator
from sims.options import Opt, get
import random
from sims.utils import Direction


class LSystem:
    def __init__(self, axiom, rules, angle=90):
        self.axiom = axiom
        self.rules = rules
        self.angle = angle
        self.current_state = axiom

    def iterate(self, iterations) -> str:
        for _ in range(iterations):
            new_state = ""
            for char in self.current_state:
                if char in self.rules:
                    rule = self.rules[char]

                    # Handle rules
                    if isinstance(rule, list):
                        choices, weights = zip(*rule)
                        new_state += random.choices(choices, weights=weights, k=1)[0]
                    else:
                        new_state += rule
                else:
                    new_state += char
            self.current_state = new_state
        return self.current_state

    def __str__(self):
        rules_str = "\n".join([f"{key} -> {value}" for key, value in self.rules.items()])
        return f"L-System:\nAxiom: {self.axiom}\nRules:\n{rules_str}\nCurrent state length: {len(self.current_state)}"

    def render_ascii(self, width=50, height=50, step_size=4, full_char=1, empty_char=0, debug=False) -> list[list[int]]:
        grid = [[empty_char for _ in range(width)] for _ in range(height)]

        x, y = width // 2, height // 2
        stack = []
        direction = Direction.RIGHT
        grid[y][x] = full_char

        if debug:
            print(f"Starting at: width={width}, height={height}, x={x}, y={y}")

        for char in self.current_state:
            if debug:
                print(f"Processing '{char}' at x={x}, y={y}, direction={direction}")
            if char in "ABCDEFG":
                x, y, grid = self._move(x, y, direction, step_size, width, height, grid, full_char)
            elif char == '+':
                direction = (direction + 1) % 4
            elif char == '-':
                direction = (direction - 1) % 4
            elif char == '[':
                stack.append((x, y, direction))
            elif char == ']':
                x, y, direction = stack.pop()

        return grid

    def _move(self, x, y, direction, step_size, width, height, grid, full_char):

        dx, dy = 0, 0

        # Determine movement direction
        if direction == Direction.RIGHT:
            dx = 1
        elif direction == Direction.DOWN:
            dy = 1
        elif direction == Direction.LEFT:
            dx = -1
        elif direction == Direction.UP:
            dy = -1

        for _ in range(step_size):
            x += dx
            y += dy

            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = full_char
            else:
                x -= dx
                y -= dy
                break

        return x, y, grid

def random_pattern():
    choices = "ABCDEFG+-"

    return "".join([random.choice(choices) for i in range(random.randint(3, 5))])

def generate_l_system_roads(grid) -> list[list[int]]:
    grid_width, grid_height = get(Opt.GRID_WIDTH), get(Opt.GRID_HEIGHT)
    system = LSystem(
        axiom=random_pattern(),
        rules={"F": random_pattern(), "G": random_pattern(), "A": random_pattern(), "B": random_pattern(),
        "C": random_pattern(), "D": random_pattern(), "E": random_pattern()}
    )

    system.iterate(5)
    return system.render_ascii(width=grid_width, height=grid_height), set()

# generator.register_road_generation_func('LSYSTEM', generate_l_system_roads)