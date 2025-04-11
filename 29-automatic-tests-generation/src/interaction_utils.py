import itertools
import io_utils
import testsuite
from collections import defaultdict
from coverage_utils import compute_coverage


def build_locating_array_matrix(test_array, param_values, display=False):
    """
    From a test array and parameter values, builds a locating array matrix:
    mapping each 2-way pair to the list of test case indices that cover it.

    Args:
        test_array (list[dict]): List of test cases as dicts {param: value}.
        param_values (dict): Dictionary of parameter: list of possible values.

    Returns:
        dict: Mapping from ((p1, v1), (p2, v2)) to list of test indices.
    """
    params = list(param_values.keys())
    param_pairs = list(itertools.combinations(params, 2))

    # Store where each pair appears
    locating_array = defaultdict(list)

    for idx, test in enumerate(test_array):
        for p1, p2 in param_pairs:
            v1, v2 = test[p1], test[p2]
            key = ((p1, v1), (p2, v2))
            locating_array[key].append(idx)

    if display:
        print(f"{'Pair':<50} | Covered in Test Indices")
        print("-" * 85)
        for pair, indices in sorted(locating_array.items()):
            pair_str = f"({pair[0][0]}={pair[0][1]}, {pair[1][0]}={pair[1][1]})"
            print(f"{pair_str:<50} | {indices}")

    return locating_array


def get_pair_coverages(
    filename, func_name, locating_array, test_array, param_values, display=False
):
    """
    Builds and prints a 2-way pair coverage matrix based on actual test coverage data.

    Args:
        locating_array (dict): Mapping from ((p1, v1), (p2, v2)) to list of test indices.
        test_array (list[dict]): The test suite, each test is a dict of parameter: value.
        param_values (dict): Dictionary of parameter: list of possible values.
        display (bool): Whether to print the matrix.

    Returns:
        dict: Mapping from ((p1, v1), (p2, v2)) to number of intersected coverage lines.
    """
    # Precompute coverage for all tests
    test_coverages = []
    for test in test_array:
        cov = compute_coverage(
            testsuite.generate_test_suite(
                io_utils.load_function_from_file(filename, func_name), [test]
            ),
            filename,
            get_lines=True,
        )
        test_coverages.append(cov)

    # For each pair, compute the number of intersected lines
    pair_coverage_matrix = {}
    for pair, test_indices in locating_array.items():
        coverages = [test_coverages[i] for i in test_indices]
        total_coverage = set()
        for cov in coverages:
            for line in cov:
                total_coverage.add(line)
        pair_coverage_matrix[pair] = len(total_coverage)

    if display:
        print(f"\n{'Pair':<50} | Test Indices       | #Intersected Lines")
        print("-" * 100)
        for pair, test_indices in locating_array.items():
            count = pair_coverage_matrix[pair]
            pair_str = f"({pair[0][0]}={pair[0][1]}, {pair[1][0]}={pair[1][1]})"
            indices_str = ", ".join(str(i) for i in test_indices)
            print(f"{pair_str:<50} | [{indices_str:<15}] | {count}")

    return pair_coverage_matrix


def get_pair_impact(pair_coverage_matrix, display=False):
    """
    Calculate the difference between the maximum and minimum coverage for each parameter pair
    from the given pair coverage matrix.

    Args:
        pair_coverage_matrix (dict): Mapping from pairs ((param1, value1), (param2, value2)) to intersection size.

    Returns:
        dict: Mapping from parameter pairs ((param1, param2)) to the coverage difference (max - min) across the pairs.
    """
    # Initialize a dictionary to store coverage values for each parameter pair
    param_pair_coverage_map = {}

    # Collect coverage values for each parameter pair across all pairs it appears in
    for pair, coverage in pair_coverage_matrix.items():
        param_pair = (pair[0][0], pair[1][0])  # Extract parameter pair (param1, param2)
        if param_pair not in param_pair_coverage_map:
            param_pair_coverage_map[param_pair] = []
        param_pair_coverage_map[param_pair].append(coverage)

    if display:
        # Print collected coverage values for each parameter pair
        print("\nCollected coverage values for each parameter pair:")
        for param_pair, coverages in param_pair_coverage_map.items():
            print(f"{param_pair}: {coverages}")

    # Calculate the difference between max and min coverage for each parameter pair
    param_pair_coverage_diff_map = {}
    for param_pair, coverages in param_pair_coverage_map.items():
        max_coverage = max(coverages)
        min_coverage = min(coverages)
        param_pair_coverage_diff_map[param_pair] = max_coverage - min_coverage

    if display:
        print("\nCoverage differences for each parameter pair (max - min):")
        for param_pair, diff in param_pair_coverage_diff_map.items():
            print(f"{param_pair}: {diff}")

    return param_pair_coverage_diff_map


def get_param_impact(pair_coverage_matrix, display=False):
    """
    Calculate the difference between the maximum and minimum coverage for each parameter
    (across all its value-pairs) from the given pair coverage matrix.

    Args:
        pair_coverage_matrix (dict): Mapping from pairs ((param1, value1), (param2, value2)) to intersection size.

    Returns:
        dict: Mapping from parameter to the coverage difference (max - min) across its values.
    """
    # Initialize a dictionary to store coverage values for each parameter
    param_coverage_map = {}

    # Collect coverage values for each parameter across all pairs it appears in
    for pair, coverage in pair_coverage_matrix.items():
        for param, value in pair:
            if param not in param_coverage_map:
                param_coverage_map[param] = []
            param_coverage_map[param].append(coverage)

    if display:
        # Print collected coverage values for each parameter
        print("\nCollected coverage values for each parameter:")
        for param, coverages in param_coverage_map.items():
            print(f"{param}: {coverages}")

    # Calculate the difference between max and min coverage for each parameter
    param_coverage_diff_map = {}
    for param, coverages in param_coverage_map.items():
        max_coverage = max(coverages)
        min_coverage = min(coverages)
        param_coverage_diff_map[param] = max_coverage - min_coverage

    if display:
        # Print coverage differences for each parameter
        print("\nCoverage differences for each parameter (max - min):")
        for param, diff in param_coverage_diff_map.items():
            print(f"{param}: {diff}")

    return param_coverage_diff_map


def get_pair_correlation_matrix(param_impact, pair_impact, display=False):
    """
    Calculate the correlation matrix for parameter pairs based on their impact values.

    Args:
        param_impact (dict): Mapping from parameters to their coverage differences (impacts).
        pair_impact (dict): Mapping from parameter pairs to their coverage differences (pair impacts).

    Returns:
        list: A matrix (list of lists) containing correlations between parameter pairs.
    """
    # Get the list of parameters in the same order to build a matrix
    parameters = list(param_impact.keys())

    # Initialize a square matrix of size len(parameters) x len(parameters)
    matrix_size = len(parameters)
    correlation_matrix = [
        [None for _ in range(matrix_size)] for _ in range(matrix_size)
    ]

    # Create a mapping from parameters to indices for the matrix
    param_index = {param: idx for idx, param in enumerate(parameters)}

    # Iterate over all parameter pairs to calculate the correlation
    for param_pair, pair_impact_value in pair_impact.items():
        p1, p2 = param_pair
        p1_impact = param_impact.get(p1, 0)
        p2_impact = param_impact.get(p2, 0)

        # Calculate the correlation if neither impact is zero
        if p1_impact != 0 and p2_impact != 0:
            correlation = pair_impact_value / (p1_impact * p2_impact)
        else:
            correlation = None  # If the denominator is zero, correlation is set to None

        # Update the matrix with the calculated correlation
        i = param_index[p1]
        j = param_index[p2]

        correlation_matrix[i][j] = correlation
        correlation_matrix[j][
            i
        ] = correlation  # Since the correlation matrix is symmetric

    if display:
        # Print the correlation matrix
        print("\nCorrelation matrix for parameter pairs:")
        print(f"{'Param 1':<15} | {'Param 2':<15} | {'Correlation'}")
        print("-" * 50)
        for i, row in enumerate(correlation_matrix):
            for j, correlation in enumerate(row):
                print(
                    f"{parameters[i]:<15} | {parameters[j]:<15} | {correlation if correlation is not None else 'null'}"
                )

    return correlation_matrix


def strength_calculation(params, correlation_matrix, display=False):
    """
    using the correlation matrix of the parameters
    return the set of parameters associated to each strength

    Args:
        params (list): List of parameter names.
        correlation_matrix (list of lists): matrix of corralation

    Returns:
        t way classes (list of lists): List of categories of parameters organised by strength
    """

    def calc_variation(correlation_matrix):
        mean = sum(correlation_matrix) / len(correlation_matrix)
        variance = sum((x - mean) ** 2 for x in correlation_matrix) / len(
            correlation_matrix
        )
        return variance

    def calc_slices(variation, max_t):
        if max_t < 2:
            return 1
        return int(max(variation * (max_t - 1), 2))

    params_num = len(params)
    flattened_correlation_matrix = values = [
        val for row in correlation_matrix for val in row
    ]
    flattened_correlation_matrix = [
        value for value in flattened_correlation_matrix if value is not None
    ]

    variation = calc_variation(flattened_correlation_matrix)
    slices_num = calc_slices(variation, params_num)

    min_correlation = min(flattened_correlation_matrix)
    max_correlation = max(flattened_correlation_matrix)
    step = (max_correlation - min_correlation) / slices_num

    slices = []
    for i in range(slices_num):
        category = set()
        # the order of the params are first param in rows second in columns
        for p1 in range(params_num):
            for p2 in range(params_num):
                if p1 == p2:
                    continue
                if (
                    i * step <= correlation_matrix[p1][p2]
                    and correlation_matrix[p1][p2] < (i + 1) * step
                ):
                    category.add(
                        (min(params[p1], params[p2]), max(params[p1], params[p2]))
                    )
        slices.append(category)

        if display:
            # Print the parameters that fall into the current slice
            print(f"Slice {i + 1} (correlation range: {i * step} - {(i + 1) * step}):")
            print(f"Parameters: {category}")

    return slices
