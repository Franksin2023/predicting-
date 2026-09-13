#!/usr/bin/env python3
"""
Test execution report generator.
Runs tests and generates detailed HTML and text reports.
"""

import sys
import os
import subprocess
import json
from datetime import datetime

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def generate_test_report():
    """Generate comprehensive test report."""
    
    print("\n" + "="*80)
    print(" "*20 + "CHARTACE TEST EXECUTION & REPORT GENERATION")
    print("="*80 + "\n")
    
    # Step 1: Check dependencies
    print("[STEP 1] Checking Python dependencies...")
    dependencies = [
        'pandas',
        'numpy',
        'unittest'
    ]
    
    missing_deps = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} (MISSING)")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n⚠ Warning: Missing dependencies: {', '.join(missing_deps)}")
        print("  Install with: pip install " + " ".join(missing_deps))
    
    # Step 2: Run tests
    print("\n[STEP 2] Running test suite...")
    print("-" * 80)
    
    try:
        # Try to run tests
        result = subprocess.run(
            [sys.executable, 'run_tests.py'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=False,
            text=True
        )
        test_exit_code = result.returncode
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        test_exit_code = 1
    
    # Step 3: Generate summary
    print("\n[STEP 3] Generating test summary...")
    summary = {
        "timestamp": datetime.now().isoformat(),
        "test_framework": "unittest",
        "exit_code": test_exit_code,
        "status": "PASSED" if test_exit_code == 0 else "FAILED"
    }
    
    # Save summary
    summary_path = "test_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"  ✓ Summary saved to {summary_path}")
    
    # Step 4: Print final status
    print("\n" + "="*80)
    if test_exit_code == 0:
        print(" "*25 + "✓ TEST SUITE PASSED!")
    else:
        print(" "*25 + "✗ TEST SUITE FAILED")
    print("="*80 + "\n")
    
    return test_exit_code


if __name__ == "__main__":
    exit_code = generate_test_report()
    sys.exit(exit_code)
