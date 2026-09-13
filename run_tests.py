#!/usr/bin/env python3
"""
Enhanced test runner with comprehensive diagnostics and detailed output.
Runs all Chartace tests and generates a full report.
"""

import sys
import os
import unittest
import logging
import traceback
from datetime import datetime
from io import StringIO

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ChartaceTestRunner")


class DetailedTestResult(unittest.TestResult):
    """Custom test result class with enhanced reporting."""
    
    def __init__(self, stream=None, descriptions=None, verbosity=None):
        super().__init__(stream, descriptions, verbosity)
        self.test_details = []
        self.test_times = {}

    def startTest(self, test):
        super().startTest(test)
        self.start_time = datetime.now()

    def addSuccess(self, test):
        super().addSuccess(test)
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.test_times[str(test)] = elapsed
        self.test_details.append({
            'test': str(test),
            'status': 'PASS',
            'time': elapsed,
            'message': None
        })

    def addError(self, test, err):
        super().addError(test, err)
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.test_times[str(test)] = elapsed
        exc_type, exc_value, exc_tb = err
        self.test_details.append({
            'test': str(test),
            'status': 'ERROR',
            'time': elapsed,
            'message': f"{exc_type.__name__}: {exc_value}"
        })

    def addFailure(self, test, err):
        super().addFailure(test, err)
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.test_times[str(test)] = elapsed
        exc_type, exc_value, exc_tb = err
        self.test_details.append({
            'test': str(test),
            'status': 'FAIL',
            'time': elapsed,
            'message': f"{exc_type.__name__}: {exc_value}"
        })


def print_header():
    """Print test run header."""
    print("\n" + "=" * 80)
    print(" " * 20 + "CHARTACE FRAMEWORK - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Working Directory: {os.getcwd()}")
    print("=" * 80 + "\n")


def print_test_results(result):
    """Print detailed test results."""
    print("\n" + "=" * 80)
    print(" " * 30 + "TEST RESULTS SUMMARY")
    print("=" * 80)
    
    total_tests = result.testsRun
    passed = total_tests - len(result.failures) - len(result.errors)
    
    print(f"\nTests Run:     {total_tests}")
    print(f"✓ Passed:      {passed} ({100*passed/total_tests if total_tests > 0 else 0:.1f}%)")
    print(f"✗ Failed:      {len(result.failures)}")
    print(f"✗ Errors:      {len(result.errors)}")
    
    if result.test_details:
        print("\n" + "-" * 80)
        print("Detailed Test Results:")
        print("-" * 80)
        
        for detail in result.test_details:
            status_symbol = "✓" if detail['status'] == 'PASS' else "✗"
            print(f"{status_symbol} {detail['test']}")
            print(f"   Status: {detail['status']} | Time: {detail['time']:.3f}s")
            if detail['message']:
                print(f"   Message: {detail['message']}")
    
    if result.failures:
        print("\n" + "-" * 80)
        print("FAILURES:")
        print("-" * 80)
        for test, tb in result.failures:
            print(f"\n✗ {test}")
            print(tb)
    
    if result.errors:
        print("\n" + "-" * 80)
        print("ERRORS:")
        print("-" * 80)
        for test, tb in result.errors:
            print(f"\n✗ {test}")
            print(tb)
    
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print(" " * 25 + "✓ ALL TESTS PASSED SUCCESSFULLY!")
    else:
        print(" " * 20 + f"✗ SOME TESTS FAILED ({len(result.failures) + len(result.errors)} issues)")
    print("=" * 80)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")


def run_tests():
    """Discover and run all tests."""
    print_header()
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    # Run with custom result class
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    runner.resultclass = DetailedTestResult
    result = runner.run(suite)
    
    # Print detailed results
    print_test_results(result)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    try:
        exit_code = run_tests()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error during test execution: {e}")
        logger.error(traceback.format_exc())
        sys.exit(2)
