import chat
import twise
import io_utils
import testsuite
import coverage_utils

import unittest
import logging
import random

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def generate_and_run_testsuite(filename, function_name):

    # 1. Extract parameters and domains from function
    logging.info(
        f"Extracting parameters and domains from function '{function_name}' in file '{filename}'..."
    )
    values = chat.parse_llm_response(
        chat.extract_parameters_and_domains(
            io_utils.get_function_code_from_file(filename, function_name)
        )
    )
    logging.debug(f"Extracted values: {values}")
    logging.info(f"Total number of parameters: {len(values)}")
    io_utils.pretty_print_values(values)

    # 2. Generate all possible test cases
    logging.info("Generating all possible test cases...")
    all_test_cases = testsuite.generate_all_possible_test_cases(values)
    logging.info(f"Total test cases generated: {len(all_test_cases)}")

    # 2.5. Select randomly initial test set
    initial_test_set = random.sample(all_test_cases, 10)
    logging.info(
        f"Selecting {len(initial_test_set)} random test cases from {len(all_test_cases)} possible test cases..."
    )

    # 6. Evaluation
    print()
    logging.info("Starting evaluation...")
    strategies = {
        "all_combinations": all_test_cases,
        "pairwise": initial_test_set,
    }
    for strategy in strategies.keys():
        print(
            "\n======================================================================\n"
        )
        logging.info(f'"{strategy}" strategy')
        test_suite = testsuite.generate_test_suite(
            io_utils.load_function_from_file(filename, function_name),
            strategies[strategy],
        )
        coverage_utils.compute_coverage(test_suite, strategy)

    return


# generate_and_run_testsuite("./tests/test_twise.py", "configure_volume")
generate_and_run_testsuite("./tests/test_discout.py", "calculate_discount")
