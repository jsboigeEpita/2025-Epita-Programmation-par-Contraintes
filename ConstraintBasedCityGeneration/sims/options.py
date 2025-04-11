import eel
import sims.generator as generator

from sims.utils import StringEnum

OPTIONS = {}

class Option():
    def __init__(self, id, name, category, type, default, depends_on):
        self.id, self.name, self.category, self.type, self.value, self.default, self.depends_on = id, name, category, type, None, default, depends_on

    def serialize(self):
        return { 'id': self.id, 'name': self.name, 'category': self.category, 'type': self.type, 'default': self.default, 'depends_on': self.depends_on }

class RangeOption(Option):
    def __init__(self, id, name, category, default, depends_on, min_range, max_range, step):
        super().__init__(id, name, category, 'range', default, depends_on)
        self.min_range, self.max_range, self.step = min_range, max_range, step

    def serialize(self):
        return super().serialize() | { 'min_range': self.min_range, 'max_range': self.max_range, 'step': self.step }

class SelectOption(Option):
    def __init__(self, id, name, category, default, depends_on, options : list[str]):
        super().__init__(id, name, category, 'select', default, depends_on)
        self.options = options

    def serialize(self):
        return super().serialize() | { 'options': self.options }

class CheckboxOption(Option):
    def __init__(self, id, name, category, default, depends_on):
        super().__init__(id, name, category, 'checkbox', default, depends_on)

@eel.expose
def option_update(id, value):
    OPTIONS[id].value = value
    print(f'Updated option {id} to ({type(value)}) {value}.')

def register_option(option : Option):
    if option.id in OPTIONS:
        raise Exception(f'Option already exists: {option.id}.')
    
    OPTIONS[option.id] = option
    
class Opt(StringEnum):
    GRID_WIDTH = 'grid_width'
    GRID_HEIGHT = 'grid_height'

    # World Generation
    ROAD_GENERATION_ALGORITHM = 'road_generation_algorithm'
    GENERATE_RIVERS = 'generate_rivers'

    # City parameters
    POPULATION = 'population'
    HOUSE_CAPACITY = 'house_capacity'
    HOSPITAL_CAPACITY = 'hospital_capacity'
    NUMBER_OF_HARBOURS = 'harbours_number'


    # Solver and Constraints
    SOLVER = 'solver'

    BUILDINGS_NEXT_TO_AT_LEAST_A_ROAD = 'buildings_next_to_at_least_a_road'
    HOSPITALS_ENABLED = 'hospitals_enabled'
    HOSPITALS_NEAR_PATIENTS = 'hospitals_near_patients'
    HARBOURS_ENABLED = 'harbours_enabled'
    SUPERMARKETS_ENABLED = 'supermarkets_enabled'
    SUPERMARKETS_ALIGNED_WITH_CLIENTS = 'supermarkets_aligned_with_clients'

    FACTORIES_ENABLED = 'factories_enabled'
    NUMBER_OF_FACTORIES = 'factories_number'
    DISTANCE_HOUSE_FACTORY = 'distance_house_factory'
    FIRE_STATIONS_ENABLED = 'fire_stations_enabled'
    FIRE_STATION_CAPACITY = 'fire_stations_capacity'
    FIRE_STATION_RADIUS = 'fire_stations_radius'
    TOWN_HALL_ENABLED = 'town_hall_enabled'

class OptCat(StringEnum):
    GRID = 'GRID',
    WORLD_GENERATION = 'WORLD GENERATION'
    SOLVER_AND_CONSTRAINTS = 'SOLVER AND CONSTRAINTS'
    CITY_PARAMETERS = 'CITY PARAMETERS'

def register_options():
    opts = [
        # Grid
        RangeOption(Opt.GRID_WIDTH, 'Grid Width', OptCat.GRID, 25, [], 5, 25, 5),
        RangeOption(Opt.GRID_HEIGHT, 'Grid Height', OptCat.GRID, 25, [], 5, 25, 5),

        # World Generation
        SelectOption(Opt.ROAD_GENERATION_ALGORITHM, 'Road Generation Algorithm', OptCat.WORLD_GENERATION, None, [],
                     list(generator.ROAD_GENERATION_ALGORITHMS.keys())),
        CheckboxOption(Opt.GENERATE_RIVERS, 'Generate Rivers', OptCat.WORLD_GENERATION, None, []),

        # City Parameters
        RangeOption(Opt.POPULATION, 'Population', OptCat.CITY_PARAMETERS, 500, [], 10, 1000, 10),
        RangeOption(Opt.HOUSE_CAPACITY, 'House Capacity', OptCat.CITY_PARAMETERS, 10, [], 1, 10, 1),
        RangeOption(Opt.HOSPITAL_CAPACITY, 'Hospital Capacity', OptCat.CITY_PARAMETERS, 50, [(Opt.HOSPITALS_ENABLED, True)], 10, 100, 5),
        RangeOption(Opt.NUMBER_OF_HARBOURS, 'Number of harbours', OptCat.CITY_PARAMETERS, 2, [(Opt.HARBOURS_ENABLED, True)], 1, 5, 1),
        RangeOption(Opt.NUMBER_OF_FACTORIES, 'Number of factories', OptCat.CITY_PARAMETERS, 2, [(Opt.FACTORIES_ENABLED, True)], 1, 10, 1),

        #OR-TOOLS
        RangeOption(Opt.DISTANCE_HOUSE_FACTORY, 'Distance house-factory', OptCat.CITY_PARAMETERS, 7, [(Opt.SOLVER, "OR-TOOLS"), (Opt.FACTORIES_ENABLED, True)], 1, 10, 1),
        RangeOption(Opt.FIRE_STATION_CAPACITY, 'Fire station capacity', OptCat.CITY_PARAMETERS, 2, [(Opt.SOLVER, "OR-TOOLS"), (Opt.FIRE_STATIONS_ENABLED, True)], 1, 15, 1),
        RangeOption(Opt.FIRE_STATION_RADIUS, 'Fire station radius', OptCat.CITY_PARAMETERS, 3, [(Opt.SOLVER, "OR-TOOLS"), (Opt.FIRE_STATIONS_ENABLED, True)], 1, 10, 1),

        # Solver and Constraints
        SelectOption(Opt.SOLVER, 'Solver', OptCat.SOLVER_AND_CONSTRAINTS, None, [], ['NONE'] + list(generator.SOLVER_ALGORITHMS.keys())),
    ]

    for o in opts: register_option(o)

def send_options_to_front():
    eel.registerOptions([o.serialize() for o in OPTIONS.values()])

def get(opt : Opt):
    return OPTIONS[opt].value