#!/usr/bin/env python3
"""
Comprehensive test runner for Chartace framework.
Executes all unit tests and generates detailed diagnostics.
"""

import sys
import unittest
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("TestRunner")

def run_all_tests():
    """Run all tests and return results."""
    logger.info("=" * 70)
    logger.info("CHARTACE TEST SUITE RUNNER")
    logger.info("=" * 70)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    logger.info(f"Failures:  {len(result.failures)}")
    logger.info(f"Errors:    {len(result.errors)}")
    logger.info(f"End time:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    if result.failures:
        logger.info("\nFAILED TESTS:")
        for test, traceback in result.failures:
            logger.error(f"  ✗ {test}")
            logger.error(f"    {traceback}")
    
    if result.errors:
        logger.info("\nERROR TESTS:")
        for test, traceback in result.errors:
            logger.error(f"  ✗ {test}")
            logger.error(f"    {traceback}")
    
    if result.wasSuccessful():
        logger.info("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        logger.error("\n✗ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
