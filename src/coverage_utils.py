import coverage
import unittest
import sys
from io import StringIO


def compute_coverage(test_suite, strategy_name):
    # Create a string buffer to capture output
    captured_output = StringIO()
    
    # Redirect stdout to our buffer
    original_stdout = sys.stdout
    sys.stdout = captured_output
    
    runner = unittest.TextTestRunner(verbosity=0)
    cov = coverage.Coverage(
        # Exclude testsuite.py and other test files
        omit=['testsuite.py', '*/__init__.py'],
    )
    cov.start()
    try:
        runner.run(test_suite)
    finally:
        # Restore stdout
        sys.stdout = original_stdout
        cov.stop()
        cov.save()
    cov.report()
    cov.html_report(directory=f"htmlcov/{strategy_name}")