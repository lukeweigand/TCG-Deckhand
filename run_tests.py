"""
TCG Deckhand - Automated Test Runner

This script runs all tests with various configurations and generates reports.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ {description} - FAILED")
        return False
    else:
        print(f"\n✅ {description} - PASSED")
        return True


def main():
    """Run all test suites."""
    print("\n" + "="*70)
    print("  TCG DECKHAND - AUTOMATED TEST SUITE")
    print("="*70)
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    results = []
    
    # 1. Run all unit tests
    results.append(run_command(
        "pytest tests/ -m unit -v",
        "Unit Tests (Individual Components)"
    ))
    
    # 2. Run integration tests
    results.append(run_command(
        "pytest tests/ -m integration -v",
        "Integration Tests (Complete Workflows)"
    ))
    
    # 3. Run database tests
    results.append(run_command(
        "pytest tests/ -m db -v",
        "Database Tests"
    ))
    
    # 4. Run AI tests
    results.append(run_command(
        "pytest tests/ -m ai -v",
        "AI Tests"
    ))
    
    # 5. Run all tests with coverage
    results.append(run_command(
        "pytest tests/ --cov=src --cov-report=html --cov-report=term",
        "All Tests with Coverage Report"
    ))
    
    # Print summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    test_names = [
        "Unit Tests",
        "Integration Tests",
        "Database Tests",
        "AI Tests",
        "Coverage Report"
    ]
    
    for name, passed in zip(test_names, results):
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name:<30} {status}")
    
    print("="*70)
    
    # Check if all passed
    if all(results):
        print("\n🎉 ALL TESTS PASSED! 🎉\n")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED ⚠️\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
