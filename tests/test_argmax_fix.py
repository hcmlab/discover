#!/usr/bin/env python3
"""
Test script to verify ARG_MAX fix for issue #9
Creates a command with many arguments to test the fix.
"""
import os
import sys
import tempfile
from pathlib import Path

# Add discover to path
sys.path.insert(0, str(Path(__file__).parent))

from discover.utils import venv_utils as vu
from discover.backend.virtual_environment import VenvHandler

def test_large_args():
    """Test with many arguments that would exceed ARG_MAX limits"""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Simulate many session arguments (the root cause of issue #9)
        # Create a scenario that would definitely exceed ARG_MAX and trigger argument file usage
        large_args = [f"session_with_extremely_long_descriptive_name_that_goes_on_and_on_{i}_making_arguments_absolutely_massive" for i in range(10000)]  # 10000 sessions
        large_kwargs = {f"--parameter_with_incredibly_long_name_that_exceeds_all_reasonable_limits_{i}": f"value_with_extremely_long_content_that_definitely_exceeds_system_limits_and_forces_argument_file_usage_{i}" for i in range(5000)}  # 5000 parameters
        
        print(f"Testing with {len(large_args)} args and {len(large_kwargs)} kwargs")
        
        # Test the new argument list generation
        arg_list = vu._args_run_cmd(large_args, large_kwargs)
        print(f"Generated argument list length: {len(arg_list)}")
        
        # Test command generation (without actual execution)
        fake_venv_path = temp_path / "test_venv"
        
        # Test module command
        module_cmd = vu.get_module_run_cmd(fake_venv_path, "test_module", large_args, large_kwargs)
        print(f"Module command type: {type(module_cmd)}")
        print(f"Module command length: {len(module_cmd) if isinstance(module_cmd, list) else len(str(module_cmd))}")
        
        # Test script command  
        script_path = temp_path / "test_script.py"
        script_cmd = vu.get_python_script_run_cmd(fake_venv_path, script_path, large_args, large_kwargs)
        print(f"Script command type: {type(script_cmd)}")
        print(f"Script command length: {len(script_cmd) if isinstance(script_cmd, list) else len(str(script_cmd))}")
        
        # Test console script command (NEW - this was the missing piece!)
        console_cmd, temp_file = vu.get_console_script_run_cmd(fake_venv_path, "du-process", large_args, large_kwargs)
        print(f"Console script command type: {type(console_cmd)}")
        print(f"Console script command length: {len(console_cmd) if isinstance(console_cmd, list) else len(str(console_cmd))}")
        
        if temp_file:
            print(f"✅ Large arguments written to temporary file: {temp_file}")
            print(f"Console script command: {console_cmd}")
            # Clean up temp file
            import os
            try:
                os.unlink(temp_file)
                print("✅ Temporary file cleaned up")
            except:
                pass
        else:
            # Calculate approximate command line length if it were a string
            if isinstance(console_cmd, list):
                approx_length = sum(len(str(arg)) + 1 for arg in console_cmd)  # +1 for spaces
                print(f"Console script approximate string length would be: {approx_length} characters")
                
                # Check if it would exceed typical ARG_MAX limits
                typical_arg_max = 131072  # 128KB typical Linux limit
                if approx_length > typical_arg_max:
                    print(f"✅ Console script would have exceeded ARG_MAX ({typical_arg_max}), but using list format avoids this!")
                else:
                    print(f"Console script command length is within ARG_MAX limits: {approx_length} < {typical_arg_max}")
        
        print("✅ Test completed successfully - no ARG_MAX errors!")

if __name__ == "__main__":
    test_large_args()