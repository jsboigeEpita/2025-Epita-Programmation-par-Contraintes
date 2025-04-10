import chat
import twise
import io_utils
import testsuite

import unittest
import logging
import coverage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def generate_and_run_testsuite(filename, function_name):
    logging.info(
        f"Extracting parameters and domains from function '{function_name}' in file '{filename}'..."
    )

    values = chat.parse_llm_response(
        chat.extract_parameters_and_domains(
            io_utils.get_function_code_from_file(filename, function_name)
        )
    )
    logging.debug(f"Extracted values: {values}")

    logging.info("Generating test inputs using t-wise testing...")
    result = twise.t_wise_testing(values, [], t=2)
    logging.debug(f"Generated combinations: {result}")
    logging.info(f"Total test cases generated: {len(result)}")

    logging.info("Generating test suite...")
    suite = testsuite.generate_test_suite(
        io_utils.load_function_from_file(filename, function_name),
        result,
    )

    cov = coverage.Coverage()
    cov.start()

    logging.info("Running the test suite...\n")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

    cov.stop()
    cov.save()

    logging.info("\nCoverage Report:")
    cov.report()
    cov.html_report(directory="htmlcov")
    logging.info("HTML coverage report generated in 'htmlcov' directory.")


generate_and_run_testsuite("test_twise.py", "configure_volume")
