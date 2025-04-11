import math

from sims.utils import StringEnum
import sims.options as o

CONSTRAINTS = {}

class Constraint():
    def __init__(self, opt : o.Opt, title : str, depends_on):
        self.opt = opt
        self.option = o.CheckboxOption(opt, title, o.OptCat.SOLVER_AND_CONSTRAINTS, None, depends_on)

        o.register_option(self.option)

    def enabled(self):
        return o.get(self.opt)

def constraint_enabled(opt : o.Opt):
    if not opt in CONSTRAINTS:
        raise Exception('Invalid constraint given to is_constraint_enabled.')
    
    return CONSTRAINTS[opt].enabled()

def register_constraint(constraint : Constraint):
    CONSTRAINTS[constraint.option.id] = constraint

def register_constraints():
    consts = [
        Constraint(o.Opt.BUILDINGS_NEXT_TO_AT_LEAST_A_ROAD, 'Buildings next to a road', []),
        Constraint(o.Opt.HARBOURS_ENABLED, 'City has harbours', [(o.Opt.GENERATE_RIVERS, True)]),
        Constraint(o.Opt.HOSPITALS_ENABLED, 'City has hospitals', []),
        Constraint(o.Opt.SUPERMARKETS_ENABLED, 'City has supermarkets', []),
        Constraint(o.Opt.HOSPITALS_NEAR_PATIENTS, 'Hospitals near patients', [(o.Opt.SOLVER, "Z3")]),
        Constraint(o.Opt.SUPERMARKETS_ALIGNED_WITH_CLIENTS, 'Supermarkets aligned with clients', []),

        Constraint(o.Opt.FACTORIES_ENABLED, 'City has factories', []),
        Constraint(o.Opt.FIRE_STATIONS_ENABLED, 'City has fire stations', [(o.Opt.SOLVER, "OR-TOOLS")]),
        Constraint(o.Opt.TOWN_HALL_ENABLED, 'City has town hall', [(o.Opt.SOLVER, "OR-TOOLS")]),
    ]

    for c in consts: register_constraint(c)

# Utils functions related to parameters

def get_required_number_of_houses():
    return math.ceil(o.get(o.Opt.POPULATION) / o.get(o.Opt.HOUSE_CAPACITY))

def get_required_number_of_hospitals():
    return math.ceil(o.get(o.Opt.POPULATION) / o.get(o.Opt.HOSPITAL_CAPACITY))

def get_number_of_houses_required_near_hospital():
    return math.floor(o.get(o.Opt.HOSPITAL_CAPACITY) / o.get(o.Opt.HOUSE_CAPACITY))

def get_required_number_of_supermarkets():
    return math.ceil(o.get(o.Opt.POPULATION) / 100)

def get_required_number_of_harbours():
    return o.get(o.Opt.NUMBER_OF_HARBOURS)

def get_required_number_of_factories():
    return o.get(o.Opt.NUMBER_OF_FACTORIES)

def get_required_number_of_fire_station():
    return math.ceil(o.get(o.Opt.NUMBER_OF_FACTORIES) / o.get(o.Opt.FIRE_STATION_CAPACITY))
