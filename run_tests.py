#!/usr/bin/env python3
"""
Test runner script for Mezmur Bot
"""
import sys
import subprocess
import os
from pathlib import Path


def run_tests(test_type="all", verbose=True):
    """
    Run tests for the Mezmur Bot
    
    Args:
        test_type: Type of tests to run ('all', 'unit', 'integration', 'specific')
        verbose: Whether to run in verbose mode
    """
    # Get the project root directory
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    # Add test directory
    cmd.append(str(tests_dir))
    
    # Add specific test types
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "specific":
        # Run specific test files
        specific_tests = [
            "test_bot.py",
            "test_api_client.py",
            "test_search_handler.py",
            "test_lyrics_handler.py",
            "test_albums_handler.py"
        ]
        for test_file in specific_tests:
            test_path = tests_dir / test_file
            if test_path.exists():
                cmd.append(str(test_path))
    
    # Add coverage if available
    try:
        import pytest_cov
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    except ImportError:
        print("pytest-cov not available, skipping coverage report")
    
    print(f"Running tests: {' '.join(cmd)}")
    print("=" * 50)
    
    # Run the tests
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest pytest-asyncio")
        return False


def main():
    """Main function"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "all"
    
    print(f"🧪 Running {test_type} tests for Mezmur Bot")
    print("=" * 50)
    
    success = run_tests(test_type)
    
    if success:
        print("\n🎉 Test run completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test run failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
