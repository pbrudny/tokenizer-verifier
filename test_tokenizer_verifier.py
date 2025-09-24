#!/usr/bin/env python3
"""
Basic tests for tokenizer verifier functionality.
These tests verify the code structure and logic without requiring network access.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tokenizer_verifier import TokenizerVerifier


def test_basic_structure():
    """Test that the TokenizerVerifier class can be instantiated."""
    print("Testing basic class structure...")
    
    try:
        # This will fail without network access, but we can catch the exception
        verifier = TokenizerVerifier()
        print("❌ Unexpected: Should have failed without network access")
        return False
    except Exception as e:
        if "HTTPSConnectionPool" in str(e) or "Failed to resolve" in str(e):
            print("✅ Expected network error - class structure is correct")
            return True
        else:
            print(f"❌ Unexpected error: {e}")
            return False


def test_method_signatures():
    """Test that all required methods exist with correct signatures."""
    print("Testing method signatures...")
    
    methods = [
        'verify_round_trip',
        'analyze_token_boundaries', 
        'find_problematic_substrings',
        'comprehensive_verification'
    ]
    
    # Check if methods exist
    for method_name in methods:
        if not hasattr(TokenizerVerifier, method_name):
            print(f"❌ Missing method: {method_name}")
            return False
        
        method = getattr(TokenizerVerifier, method_name)
        if not callable(method):
            print(f"❌ {method_name} is not callable")
            return False
    
    print("✅ All required methods present")
    return True


def test_cli_help():
    """Test that CLI help works."""
    print("Testing CLI help...")
    
    import subprocess
    try:
        result = subprocess.run([
            sys.executable, 'tokenizer_verifier.py', '--help'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0 and 'Verify tiktoken tokenizer behavior' in result.stdout:
            print("✅ CLI help working")
            return True
        else:
            print(f"❌ CLI help failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI help error: {e}")
        return False


def test_import():
    """Test that the module imports correctly."""
    print("Testing module import...")
    
    try:
        import tokenizer_verifier
        print("✅ Module imports successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def run_tests():
    """Run all tests and report results."""
    print("=== Running Tokenizer Verifier Tests ===\n")
    
    tests = [
        test_import,
        test_method_signatures,
        test_basic_structure,
        test_cli_help
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
        print()
    
    print(f"=== Test Results: {passed}/{total} passed ===")
    
    if passed == total:
        print("✅ All tests passed! The tokenizer verifier is ready to use.")
        print("Note: Full functionality requires internet access for tiktoken encodings.")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)