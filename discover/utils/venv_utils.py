"""Utility functions to create virtual environments and execute commands in them

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    06.09.2023

"""
import os
import json
import platform
import tempfile
from pathlib import Path
from discover.utils import env
from importlib.machinery import SourceFileLoader


def _args_run_cmd(args: list = None, kwargs: dict = None) -> list:
    """
    Generate a command argument list from positional and keyword arguments.

    Args:
        args (list, optional): List of arguments.
        kwargs (dict, optional): Dictionary of keyword arguments.

    Returns:
        list: Combined argument list.

    Example:
        >>> _args_run_cmd(['arg1', 'arg2'], {'--flag': 'value'})
        ['arg1', 'arg2', '--flag', 'value']
    """
    tmp = []
    if args is not None:
        tmp += args
    if kwargs is not None:
        for k, v in kwargs.items():
            tmp.append(k)
            if v is not None and v != "":
                tmp.append(str(v))

    return tmp


def _get_venv_python(env_path: Path) -> Path:
    """
    Get the path to the Python executable within a virtual environment.

    Args:
        env_path (Path): Path to the virtual environment.

    Returns:
        Path: Path to the Python executable.

    Example:
        >>> _get_venv_python(Path('/path/to/venv'))
        Path('/path/to/venv/bin/python')
    """
    if platform.system() == "Windows":
        return env_path / "Scripts" / "python.exe"
    else:
        return env_path / "bin" / "python"


def _src_activate_cmd(env_path: Path):
    """
    Generate the source command to activate a virtual environmend. Generated output is platform dependend.

    Args:
        env_path (Path): Path to the virtual environment.

    Returns:
        str: Source activation command.

    Example:
        >>> _src_activate_cmd(Path('/path/to/venv'))
        'source /path/to/venv/bin/activate'
    """
    if platform.system() == "Windows":
        return f"{env_path/'Scripts'/'activate'}"
    else:
        return f". {env_path/'bin'/'activate'}"


def get_module_run_cmd(
    env_path: Path, module: str, args: list = None, kwargs: dict = None
):
    """
    Generate a command to run a Python module within a virtual environment.

    Args:
        env_path (Path): Path to the virtual environment.
        module (str): Python module name.
        args (list, optional): List of arguments to pass to the module.
        kwargs (dict, optional): Dictionary of keyword arguments to pass to the module.

    Returns:
        list: Command argument list.

    Example:
        >>> get_module_run_cmd(Path('/path/to/venv'), 'mymodule', ['arg1', 'arg2'], {'--flag': 'value'})
        ['/path/to/venv/bin/python', '-m', 'mymodule', 'arg1', 'arg2', '--flag', 'value']
    """
    python_exe = _get_venv_python(env_path)
    cmd = [str(python_exe), "-m", module]
    cmd.extend(_args_run_cmd(args, kwargs))
    return cmd


def get_python_script_run_cmd(
    env_path: Path, script: Path, args: list = None, kwargs: dict = None
):
    """
    Generate a command to run a Python script within a virtual environment.

    Args:
        env_path (Path): Path to the virtual environment.
        script (Path): Path to the Python script.
        args (list, optional): List of arguments to pass to the script.
        kwargs (dict, optional): Dictionary of keyword arguments to pass to the script.

    Returns:
        list: Command argument list.

    Example:
        >>> get_python_script_run_cmd(Path('/path/to/venv'), Path('/path/to/script.py'), ['arg1', 'arg2'], {'--flag': 'value'})
        ['/path/to/venv/bin/python', '/path/to/script.py', 'arg1', 'arg2', '--flag', 'value']
    """
    python_exe = _get_venv_python(env_path)
    cmd = [str(python_exe), str(script.resolve())]
    cmd.extend(_args_run_cmd(args, kwargs))
    return cmd

def get_console_script_run_cmd(
        env_path: Path, script: str, args: list = None, kwargs: dict = None
):
    """
    Generate a command to run a console script within a virtual environment using direct execution.
    Uses argument files for large argument lists to avoid system limits.

    Args:
        env_path (Path): Path to the virtual environment.
        script (str): Name of the console script to run.
        args (list, optional): List of arguments to pass to the script.
        kwargs (dict, optional): Dictionary of keyword arguments to pass to the script.

    Returns:
        tuple: (command_list, temp_file_path) where temp_file_path is None if no file was used

    Example:
        >>> get_console_script_run_cmd(Path('/path/to/venv'), 'my_script', ['arg1', 'arg2'], {'--flag': 'value'})
        (['/path/to/venv/bin/my_script', 'arg1', 'arg2', '--flag', 'value'], None)
    """
    if platform.system() == "Windows":
        script_path = env_path / "Scripts" / f"{script}.exe"
        if not script_path.exists():
            script_path = env_path / "Scripts" / script
    else:
        script_path = env_path / "bin" / script
    
    cmd = [str(script_path)]
    arg_list = _args_run_cmd(args, kwargs)
    
    # Check if arguments would be too large for command line
    # Use a very conservative estimate: 100KB limit to definitely trigger for large batches
    estimated_size = sum(len(str(arg)) + 1 for arg in arg_list)  # +1 for spaces
    max_safe_size = 100 * 1024  # 100KB - much more conservative
    
    temp_file = None
    if estimated_size > max_safe_size:
        # Create temporary argument file
        temp_fd, temp_file = tempfile.mkstemp(suffix='.args', prefix='discover_args_')
        try:
            with os.fdopen(temp_fd, 'w') as f:
                for arg in arg_list:
                    f.write(f"{arg}\n")
            # Use @ prefix to indicate argument file (argparse fromfile_prefix_chars)
            cmd.append(f"@{temp_file}")
        except:
            # If file creation fails, fall back to direct arguments
            os.unlink(temp_file)
            temp_file = None
            cmd.extend(arg_list)
    else:
        cmd.extend(arg_list)
    
    return cmd, temp_file


def get_shell_script_run_cmd(
        env_path: Path, script: str, args: list = None, kwargs: dict = None
):
    """
    Generate a command to run a shell script within a virtual environment. The path to the script musst be set in the path environment variable of the console session.

    Args:
        env_path (Path): Path to the virtual environment.
        script (Path): Path to the Python script.
        args (list, optional): List of arguments to pass to the script.
        kwargs (dict, optional): Dictionary of keyword arguments to pass to the script.

    Returns:
        str: Run command (shell-based for script execution).

    Example:
        >>> get_shell_script_run_cmd(Path('/path/to/venv'), 'my_script', ['arg1', 'arg2'], {'--flag': 'value'})
        'source /path/to/venv/bin/activate && my_script arg1 arg2 --flag value'
    """
    # Convert args back to string for shell commands (shell scripts typically don't have massive args)
    args_str = ""
    if args or kwargs:
        arg_list = _args_run_cmd(args, kwargs)
        args_str = " ".join(str(arg) for arg in arg_list)
        if args_str:
            args_str = " " + args_str
    
    return f"{_src_activate_cmd(env_path)} && {script}{args_str}"


def _venv_name_from_mod(module_dir: Path) -> str:
    """
    Generate a virtual environment name from a DISCOVER module directory.
    The name equals the root folder name of the model. If a version.py file is present at the top level od the module
    directory the returned name will be equal to <root_folder_name>@<major_version>.<minor_version>.<patch_version>
    Args:
        module_dir (Path): Path to the module directory.

    Returns:
        str: Virtual environment name.
    """
    venv_name = module_dir.name
    version_file = module_dir / "version.py"
    if version_file.is_file():
        v = SourceFileLoader("version", str(version_file.resolve())).load_module()
        venv_name += f"@{v.__version__}"

    return venv_name


def venv_dir_from_mod(module_dir: Path) -> Path:
    """
    Returns the path to a virtual environment directory matchin a provided module directory.

    Args:
        module_dir (Path): Path to the module directory.

    Returns:
        Path: Virtual environment directory.

    Raises:
        ValueError: If the NOVA_CACHE_DIR environment variable is not set.

    Example:
        >>> venv_dir_from_mod(Path('/path/to/my_module'))
        Path('/path/to/venvs/my_module')
    """
    parent_dir = os.getenv(env.DISCOVER_CACHE_DIR)

    if parent_dir is None:
        raise ValueError("DISCOVER_CACHER_DIR environment variable has not been set")

    parent_dir = Path(parent_dir) / "venvs"
    venv_dir = parent_dir / _venv_name_from_mod(module_dir)
    return venv_dir
