#!/usr/bin/env python3
"""
Test script to verify password sanitization in stderr and traceback output.
"""

import sys
import os

# Add the parent directory to the path so we can import discover
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_stderr_sanitization():
    """Test that passwords are sanitized in stderr output"""
    from discover.backend.virtual_environment import VenvHandler
    import io
    import contextlib
    
    # Create a VenvHandler instance
    handler = VenvHandler()
    
    # Test various password formats
    test_cases = [
        'Error connecting with password: secretpass123',
        'dbPassword="mypassword"',
        'db_password: supersecret',
        'Failed: --password mysecretpwd',
        'AUTH_ERROR: PASSWORD=admin123',
        'Connection failed with password=test123',
    ]
    
    print("Testing stderr sanitization:")
    for test_input in test_cases:
        sanitized = handler._sanitize_stderr_output(test_input)
        print(f"Input:  {test_input}")
        print(f"Output: {sanitized}")
        
        # Verify that actual passwords are masked
        if "secretpass123" in test_input:
            assert "****" in sanitized and "secretpass123" not in sanitized
        if "mypassword" in test_input:
            assert "****" in sanitized and "mypassword" not in sanitized
        if "supersecret" in test_input:
            assert "****" in sanitized and "supersecret" not in sanitized
        if "mysecretpwd" in test_input:
            assert "****" in sanitized and "mysecretpwd" not in sanitized
        if "admin123" in test_input:
            assert "****" in sanitized and "admin123" not in sanitized
        if "test123" in test_input:
            assert "****" in sanitized and "test123" not in sanitized
            
        print("✅ PASS")
        print()

def test_traceback_sanitization():
    """Test that passwords are sanitized in traceback output"""
    from discover.app import _sanitize_traceback_line
    
    test_cases = [
        'File "/path/script.py", line 42, in connect\n    raise Exception("Auth failed with password=secret123")',
        'DatabaseError: Connection failed with dbPassword="mysecretpwd"',
        'ValueError: Invalid password: supersecret at line 15',
    ]
    
    print("Testing traceback sanitization:")
    for test_input in test_cases:
        sanitized = _sanitize_traceback_line(test_input)
        print(f"Input:  {test_input}")
        print(f"Output: {sanitized}")
        
        # Verify that actual passwords are masked
        if "secret123" in test_input:
            assert "****" in sanitized and "secret123" not in sanitized
        if "mysecretpwd" in test_input:
            assert "****" in sanitized and "mysecretpwd" not in sanitized
        if "supersecret" in test_input:
            assert "****" in sanitized and "supersecret" not in sanitized
            
        print("✅ PASS")
        print()

def test_command_sanitization():
    """Test that passwords are sanitized in command arguments for exceptions"""
    from discover.backend.virtual_environment import VenvHandler
    
    handler = VenvHandler()
    
    # Test command sanitization for both string and list commands
    test_commands = [
        ["python", "script.py", "--db_password", "secret123", "--host", "localhost"],
        "python script.py --password=mysecret --user admin",
        ["du-process", "--db_password", "secret", "--db_host", "nova.hcai.eu"]
    ]
    
    print("Testing command sanitization:")
    for cmd in test_commands:
        sanitized = handler._sanitize_command_for_exception(cmd)
        print(f"Input:  {cmd}")
        print(f"Output: {sanitized}")
        
        # Convert to string for testing
        sanitized_str = str(sanitized)
        
        # Verify passwords are masked
        if "secret123" in str(cmd):
            assert "****" in sanitized_str and "secret123" not in sanitized_str
        if "mysecret" in str(cmd):
            assert "****" in sanitized_str and "mysecret" not in sanitized_str
        if "secret" in str(cmd) and "secret123" not in str(cmd):  # Only check the exact "secret"
            assert "****" in sanitized_str and "secret" not in sanitized_str
            
        print("✅ PASS")
        print()

if __name__ == "__main__":
    print("=" * 60)
    print("DISCOVER Password Sanitization Test")
    print("=" * 60)
    
    try:
        test_stderr_sanitization()
        test_traceback_sanitization()
        test_command_sanitization()
        print("🎉 All tests passed! Password sanitization is working correctly.")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise