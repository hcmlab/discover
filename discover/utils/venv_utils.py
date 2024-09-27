"""Utility functions to create virtual environments and execute commands in them

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    06.09.2023

"""
import os
import json
import platform
from pathlib import Path
from discover.utils import env
from importlib.machinery import SourceFileLoader


def _args_run_cmd(args: list = None, kwargs: dict = None) -> str:
    """
    Generate a command string from a list of arguments and keyword arguments.

    Args:
        args (list, optional): List of arguments.
        kwargs (dict, optional): Dictionary of keyword arguments.

    Returns:
        str: Combined command string.

    Example:
        >>> _args_run_cmd(['arg1', 'arg2'], {'--flag': 'value'})
        'arg1 arg2 --flag value'
    """
    tmp = []
    if args is not None:
        tmp += args
    if kwargs is not None:
        tmp += [f"{k} {json.dumps(v)}" for k, v in kwargs.items()]
    args_run_cmd = " ".join(tmp)

    return args_run_cmd


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
        str: Run command.

    Example:
        >>> get_module_run_cmd(Path('/path/to/venv'), 'mymodule', ['arg1', 'arg2'], {'--flag': 'value'})
        'source /path/to/venv/bin/activate && python -m mymodule arg1 arg2 --flag value'
    """
    return f"{_src_activate_cmd(env_path)} && python -m {module} {_args_run_cmd(args, kwargs)}"


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
        str: Run command.

    Example:
        >>> get_python_script_run_cmd(Path('/path/to/venv'), Path('/path/to/script.py'), ['arg1', 'arg2'], {'--flag': 'value'})
        'source /path/to/venv/bin/activate && python /path/to/script.py arg1 arg2 --flag value'
    """
    return f"{_src_activate_cmd(env_path)} && python {script.resolve()} {_args_run_cmd(args, kwargs)}"

def get_shell_script_run_cmd(
        env_path: Path, script: str, args: list = None, kwargs: dict = None
):
    """
    Generate a command to run a console script within a virtual environment. The path to the script musst be set in the path environment variable of the console session.

    Args:
        env_path (Path): Path to the virtual environment.
        script (Path): Path to the Python script.
        args (list, optional): List of arguments to pass to the script.
        kwargs (dict, optional): Dictionary of keyword arguments to pass to the script.

    Returns:
        str: Run command.

    Example:
        >>> get_python_script_run_cmd(Path('/path/to/venv'), Path('/path/to/script.py'), ['arg1', 'arg2'], {'--flag': 'value'})
        'source /path/to/venv/bin/activate && python /path/to/script.py arg1 arg2 --flag value'
    """
    return f"{_src_activate_cmd(env_path)} && {script} {_args_run_cmd(args, kwargs)}"


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
