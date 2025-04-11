from twise import *
from mixed_t_way import *
from interaction_utils import *


def weighted_cit_testing(filename, func_name, values, constraints, display=False):
    params = list(values.keys())

    # initial pair wise test suite
    test_suite = t_wise_testing(values, constraints, t=2)

    # weighting parameter impact
    locating_array = build_locating_array_matrix(test_suite, values)
    pair_coverages = get_pair_coverages(
        filename, func_name, locating_array, test_suite, values, display=False
    )
    pair_impacts = get_pair_impact(pair_coverages, display=False)
    param_impacts = get_param_impact(pair_coverages, display=False)
    correlation_matrix = get_pair_correlation_matrix(
        param_impacts, pair_impacts, display=False
    )
    strength_classes = strength_calculation(params, correlation_matrix, display=False)

    # updating the tests according to impact weights
    unrolled_strength_classes = define_new_combinations(strength_classes)
    extended_test_suite = extend_test_suite(
        test_suite, values, constraints, unrolled_strength_classes
    )

    if display:
        # Print the extended test suite
        for idx, test_case in enumerate(extended_test_suite):
            print(f"Test {idx + 1}: {test_case}")

    return extended_test_suite
