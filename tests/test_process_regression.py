#!/usr/bin/env python3
"""
Test script to verify that process execution works correctly with shell=False
and that return codes and exceptions are handled properly.
"""
import sys
import tempfile
import os
from pathlib import Path

# Add discover to path
sys.path.insert(0, str(Path(__file__).parent))

from discover.backend.virtual_environment import VenvHandler
from discover.utils import log_utils

def test_process_completion():
    """Test that processes complete properly and return correct codes"""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a simple test script that exits with code 1
        test_script = temp_path / "test_script.py"
        test_script.write_text("""
import sys
print("Test script starting...")
print("Test script output line 1")
print("Test script output line 2")
print("Test script writing to stderr", file=sys.stderr)
print("Test script exiting with code 1")
sys.exit(1)
""")
        
        # Test with a fake venv (using system python)
        fake_venv = temp_path / "fake_venv"
        fake_venv.mkdir()
        (fake_venv / "bin").mkdir()
        
        # Create symlink to system python 
        import shutil
        python_path = shutil.which("python")
        os.symlink(python_path, fake_venv / "bin" / "python")
        
        print("Testing VenvHandler with script that exits with code 1...")
        
        try:
            handler = VenvHandler(log_verbose=True, logger=None)
            handler.venv_dir = fake_venv
            
            print("Running script that should fail...")
            print("Expected output: Test script starting/output/stderr/exiting messages")
            handler.run_python_script_from_file(test_script)
            print("❌ ERROR: Script should have raised CalledProcessError!")
            
        except Exception as e:
            print(f"✅ SUCCESS: Got expected exception: {type(e).__name__}: {e}")
            
            # Check if it's the right type of exception
            if "CalledProcessError" in str(type(e)):
                print("✅ SUCCESS: Correct exception type (CalledProcessError)")
            else:
                print(f"❌ ERROR: Wrong exception type: {type(e)}")
                
        print("\nTesting console script execution...")
        
        # Test console script execution (this should also handle return codes properly)
        try:
            # Create fake console script
            fake_script = fake_venv / "bin" / "test-console-script"
            fake_script.write_text(f"""#!/usr/bin/env python
{test_script.read_text()}
""")
            fake_script.chmod(0o755)
            
            handler.run_console_script("test-console-script")
            print("❌ ERROR: Console script should have raised CalledProcessError!")
            
        except Exception as e:
            print(f"✅ SUCCESS: Console script got expected exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_process_completion()