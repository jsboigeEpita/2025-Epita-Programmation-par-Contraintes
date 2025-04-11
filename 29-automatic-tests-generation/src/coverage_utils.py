from io import StringIO
import contextlib
import coverage
import sys
import unittest


def compute_coverage(test_suite, strategy_name, get_lines=False):
    # Create a string buffer to capture output
    captured_output = StringIO()

    # Redirect stdout to our buffer
    original_stdout = sys.stdout
    sys.stdout = captured_output

    if not get_lines:
        runner = unittest.TextTestRunner(verbosity=0)
    else:
        with (
            contextlib.redirect_stdout(captured_output),
            contextlib.redirect_stderr(captured_output),
        ):
            runner = unittest.TextTestRunner(verbosity=0)

    cov = coverage.Coverage(
        # Exclude testsuite.py and other test files
        omit=["testsuite.py", "*/__init__.py"],
    )
    cov.start()
    try:
        runner.run(test_suite)
    finally:
        # Restore stdout
        sys.stdout = original_stdout
        cov.stop()
        cov.save()

    if not get_lines:
        cov.report()
        cov.html_report(directory=f"htmlcov/{strategy_name}")
        return

    data = cov.get_data()
    lines = []
    for file_name in data.measured_files():
        for line in data.lines(file_name):
            lines.append(line)

    return sorted(lines)
