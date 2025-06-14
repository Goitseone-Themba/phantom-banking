"""
Run all component tests
"""
import subprocess
import sys
from pathlib import Path

def run_test_file(test_file):
    """Run a single test file"""
    print(f"\n{'='*60}")
    print(f"Running {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Failed to run {test_file}: {e}")
        return False

def main():
    """Run all component tests"""
    print("🏦 Phantom Banking - All Component Tests")
    print("=" * 60)
    
    test_files = [
        'test_merchants.py',
        'test_customers.py',
        'test_wallets.py',
        'test_transactions.py',
        'test_mock_systems.py'
    ]
    
    passed = 0
    for test_file in test_files:
        if run_test_file(test_file):
            passed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Overall Results: {passed}/{len(test_files)} test files passed")
    
    if passed == len(test_files):
        print("🎉 All component tests passed!")
        return True
    else:
        print(f"❌ {len(test_files) - passed} test files failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)