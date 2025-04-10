import io
from contextlib import redirect_stdout
import unittest
import itertools


def generate_all_possible_test_cases(values):
    """
    Generate all possible test cases from the given function and values.
    """
    test_cases = []
    for combination in itertools.product(*values.values()):
        test_cases.append(dict(zip(values.keys(), combination)))
    return test_cases


def generate_test_suite(func, test_cases):
    """
    Dynamically generates a unittest.TestCase subclass with test methods
    for each test case in the list. The expected output is computed by
    running the function with the given parameters.
    """

    class DynamicTestCase(unittest.TestCase):
        pass

    num_digits = len(str(len(test_cases)))

    for i, case in enumerate(test_cases):
        # Compute expected result (suppressing print from func)
        with io.StringIO() as buf, redirect_stdout(buf):
            expected = func(**case)

        def make_test(case, expected):
            def test(self):
                # Show test case parameters
                formatted_params = ", ".join(f"{k}={v!r}" for k, v in case.items())
                print(f"\n▶️  Running test with: {formatted_params}")

                # Suppress print from func during actual call
                with io.StringIO() as buf, redirect_stdout(buf):
                    result = func(**case)

                self.assertEqual(result, expected)
                print()

            return test

        test_method = make_test(case, expected)
        test_method_name = f"test_case_{str(i+1).zfill(num_digits)}"
        setattr(DynamicTestCase, test_method_name, test_method)

    return unittest.defaultTestLoader.loadTestsFromTestCase(DynamicTestCase)
