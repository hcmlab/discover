#!/usr/bin/env python3
"""
Test script to verify that progress output and flushing works correctly
"""
import sys
import tempfile
import os
from pathlib import Path

# Add discover to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from discover.backend.virtual_environment import VenvHandler

def test_progress_output():
    """Test that progress output appears in real-time"""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a simple test script that prints progress with delays
        test_script = temp_path / "progress_test.py"
        test_script.write_text("""
import sys
import time

print("Starting progress test...")
sys.stdout.flush()

for i in range(5):
    print(f"Processing item ({i+1}/5)...")
    sys.stdout.flush()
    time.sleep(1)  # Simulate work
    print(f"Completed item ({i+1}/5)")
    sys.stdout.flush()

print("All items completed!")
sys.stdout.flush()
""")
        
        # Test with a fake venv (using system python)
        fake_venv = temp_path / "fake_venv"
        fake_venv.mkdir()
        (fake_venv / "bin").mkdir()
        
        # Create symlink to system python 
        import shutil
        python_path = shutil.which("python")
        os.symlink(python_path, fake_venv / "bin" / "python")
        
        print("Testing real-time progress output (should see output as it happens)...")
        print("=" * 60)
        
        try:
            handler = VenvHandler(log_verbose=True, logger=None)
            handler.venv_dir = fake_venv
            
            # This should show real-time output
            handler.run_python_script_from_file(test_script)
            print("=" * 60)
            print("✅ SUCCESS: Script completed")
            
        except Exception as e:
            print(f"❌ ERROR: Got exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_progress_output()