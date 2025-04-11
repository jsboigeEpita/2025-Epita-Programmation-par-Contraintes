import itertools
import random
from z3 import Solver, Int, sat


def define_new_combinations(slices):
    """
    Unwraps pairs to recompose n uples

    Args:
        slices (list of lists): List of slices each containing a group of pairs and representing a strength class

    Returns:
        list of lists: lists of n uples respective to the strengths
    """
    new_combinations = []
    t = 2

    for s in slices:
        values = [x for pair in s for x in pair]
        t_uples = set(
            tuple(sorted(comb))
            for comb in itertools.combinations(values, t)
            if len(set(comb)) == t
        )
        new_combinations.append(list(t_uples))
        t += 1

    return new_combinations


def extend_test_suite(test_suite, param_values, constraints, interaction_combos):
    """
    Extend the test suite to cover interactions of different strengths (2-way, 3-way, etc.).

    Args:
        test_suite (list): Current test suite (list of dicts mapping parameter names to values).
        param_values (dict): Dictionary of parameter names and their possible values.
        constraints (list): List of constraint functions taking Z3 variables.
        interaction_combos (list of lists): A list where each element is a list of parameter combinations
                                            for each interaction strength (e.g., pairs, triplets, etc.).

    Returns:
        list: Extended test suite with additional test cases.
    """

    def create_base_solver():
        z3_vars = {p: Int(p) for p in param_values}
        s = Solver()
        for p in param_values:
            s.add(z3_vars[p] >= 0, z3_vars[p] < len(param_values[p]))
        for c in constraints:
            s.add(c(z3_vars))
        return s, z3_vars

    # Iterate through interaction strengths (e.g., pairs, triplets, etc.)
    for strength, param_combos_list in enumerate(interaction_combos, start=2):
        # Track uncovered value combinations for each parameter combo
        uncovered = {
            combo: set(itertools.product(*(param_values[p] for p in combo)))
            for combo in param_combos_list
        }

        while any(uncovered[combo] for combo in param_combos_list):
            # Select the parameter combo with the most uncovered value combinations
            best_combo = max(
                uncovered.items(), key=lambda x: len(x[1]) if x[1] else -1
            )[0]
            value_combos = list(uncovered[best_combo])
            random.shuffle(value_combos)

            found = False
            for val_combo in value_combos:
                s, z3_vars = create_base_solver()
                for p, v in zip(best_combo, val_combo):
                    s.add(z3_vars[p] == param_values[p].index(v))
                if s.check() == sat:
                    found = True
                    break
                else:
                    uncovered[best_combo].remove(val_combo)

            if not found:
                continue

            # Build the test case from the chosen value combination
            test_case = {p: v for p, v in zip(best_combo, val_combo)}
            assigned = set(test_case.keys())

            s, z3_vars = create_base_solver()
            for p, v in test_case.items():
                s.add(z3_vars[p] == param_values[p].index(v))

            # Assign remaining parameters to cover more combinations
            for p in param_values:
                if p in assigned:
                    continue
                candidates = []
                for v in param_values[p]:
                    s.push()
                    s.add(z3_vars[p] == param_values[p].index(v))
                    if s.check() == sat:
                        # Score based on new combinations it covers
                        score = 0
                        for combo in param_combos_list:
                            if p not in combo:
                                continue
                            if all(param in test_case for param in combo if param != p):
                                full_combo = tuple(
                                    test_case[param] if param != p else v
                                    for param in combo
                                )
                                if full_combo in uncovered[combo]:
                                    score += 1
                        candidates.append((v, score))
                    s.pop()
                if not candidates:
                    raise Exception(
                        f"No valid value for parameter {p} under constraints."
                    )
                max_score = max(c[1] for c in candidates)
                best_vals = [v for v, s in candidates if s == max_score]
                chosen_val = random.choice(best_vals)
                test_case[p] = chosen_val
                s.add(z3_vars[p] == param_values[p].index(chosen_val))

            # Add the test case to the suite if it's not already present
            sorted_test_case = {k: test_case[k] for k in sorted(test_case.keys())}
            if sorted_test_case not in [dict(sorted(tc.items())) for tc in test_suite]:
                test_suite.append(sorted_test_case)

            # Update uncovered combinations
            for combo in param_combos_list:
                if all(p in test_case for p in combo):
                    val_combo = tuple(test_case[p] for p in combo)
                    uncovered[combo].discard(val_combo)

    return test_suite
