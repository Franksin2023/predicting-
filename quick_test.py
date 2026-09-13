#!/usr/bin/env python3
"""
Chartace Test Suite - Quick Test Runner
Executes all tests and displays pass/fail summary.
"""

import sys
import os
import unittest
from datetime import datetime

# Ensure repo root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("\n" + "="*80)
    print(" "*15 + "CHARTACE ALGORITHMIC TRADING FRAMEWORK - TEST SUITE")
    print("="*80)
    print(f"\nStart Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}\n")
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Run:  {result.testsRun}")
    print(f"Passed:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed:     {len(result.failures)}")
    print(f"Errors:     {len(result.errors)}")
    print("="*80)
    
    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
