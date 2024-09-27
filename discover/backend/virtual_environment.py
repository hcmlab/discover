"""Backend for using virtual environments as a backend for discover

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    18.8.2023

"""
import shutil
import string
import tempfile

import sys
from threading import Thread
from subprocess import Popen, PIPE
from pathlib import Path
from discover.utils import venv_utils as vu
from dotenv import load_dotenv
from logging import Logger
import psutil
import subprocess
import os


class VenvHandler:
    """
    Handles the creation and management of a virtual environment and running scripts within it.

    Args:
        module_dir (Path, optional): The path to the discover  module directory for the environtment.
        logger (Logger, optional): The logger instance for logging.
        log_verbose (bool, optional): If True, log verbose output.

    Attributes:
        venv_dir (Path): The path to the virtual environment.
        log_verbose (bool): If True, log verbose output.
        module_dir (Path): The path to the module directory.
        logger (Logger): The logger instance.

    Example:
        >>> import logging
        >>> load_dotenv("../.env")
        >>> log_dir = Path(os.getenv('NOVA_LOG_DIR', '.'))
        >>> log_file = log_dir / 'test.log'
        >>> logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG)
        >>> logger = logging.getLogger('test_logger')
        >>> module_path = Path(os.getenv("NOVA_CML_DIR")) / "test"
        >>> venv_handler = VenvHandler(module_path, logger=logger, log_verbose=True)
        >>> venv_handler.run_python_script_from_file(
        ...     module_path / "test.py",
        ...     script_args=["pos_1", "pos_2"],
        ...     script_kwargs={"-k1": "k1", "--keyword_three": "k3"},
        ... )
    """

    def _reader(self, stream, context=None):
        """
        Reads and logs output from a stream.

        Args:
            stream: The stream to read.
            context (str, optional): The context of the stream (stdout or stderr).
        """
        while True:
            try:
                s = stream.readline()
                printable = set(string.printable)
                s = "".join(filter(lambda x: x in printable, s))
                if not s or s == "":
                    break
                if self.logger is None:
                    if not self.log_verbose:
                        sys.stderr.write(".")
                    else:
                        sys.stderr.write(s.strip("\n"))
                else:
                    # if context == "stderr":
                    #    self.logger.error(s.strip('\n'))
                    # else:
                    self.logger.info(s.strip("\n"))
                sys.stderr.flush()
            except Exception as e:
                continue
            # self.logger.error(e)
        stream.close()

    def _run_cmd(self, cmd: str, wait: bool = True) -> int:
        """
        Executes a command in a subprocess and logs the output.

        Args:
           cmd (str): The command to execute.
           wait (bool, optional): If True, wait for the command to complete.

        Returns:
            int: Return code of the executed command
        """
        # TODO check if CREATE_NEW_PROCESS_GROUP works in unix
        self.current_process = Popen(
            cmd, stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True
        )
        t1 = Thread(target=self._reader, args=(self.current_process.stdout, "stdout"))
        t1.start()
        t2 = Thread(target=self._reader, args=(self.current_process.stderr, "stderr"))
        t2.start()
        if wait:
            self.current_process.wait()
            t1.join()
            t2.join()
        return self.current_process.returncode

    def _get_or_create_venv(self):
        """
        Gets or creates a virtual environment and returns its path.

        Returns:
            Path: The path to the virtual environment.
        """
        venv_dir = vu.venv_dir_from_mod(self.module_dir)
        existed = True
        if not venv_dir.is_dir():
            existed = False
            try:
                run_cmd = f"{sys.executable} -m venv {venv_dir}"
                self._run_cmd(run_cmd)
            except Exception as e:
                shutil.rmtree(venv_dir)
                raise e
        return venv_dir, existed

    def _upgrade_pip(self):
        """
        Upgrades the `pip` package within the virtual environment.
        """

        args = ["install"]
        if not self.log_verbose:
            args.append("-q")

        run_cmd = vu.get_module_run_cmd(
            self.venv_dir, "pip", args=args, kwargs={"--upgrade": "pip"}
        )
        self._run_cmd(run_cmd)

    def _install_requirements(self):
        """
        Installs requirements from a `requirements.txt` file within the virtual environment.
        """
        # pip
        self._upgrade_pip()

        # requirements.txt
        req_txt = self.module_dir / "requirements.txt"
        if not req_txt.is_file():
            self._install_discover_utils()
            return
        else:

            # Create tmp copy of requirement file
            tmp_req_txt = (
                Path(tempfile.tempdir) / f"_{self.module_dir.name}_requirements.txt"
            )
            with open(tmp_req_txt, mode="wt") as tmp:
                requirements = open(req_txt).readlines()
                if self.extra_index_urls is not None:
                    tmp.writelines(
                        [f"--extra-index-url {x}\n" for x in self.extra_index_urls]
                    )
                tmp.writelines(requirements)

            self._install_discover_utils(requirements_file=str(tmp_req_txt))
            args = ["install", "--upgrade", "--force-reinstall"]
            if not self.log_verbose:
                args.append("-q")
            run_cmd = vu.get_module_run_cmd(
                self.venv_dir,
                "pip",
                args=args,
                kwargs={"-r": str(tmp_req_txt)},
            )
            self._run_cmd(run_cmd)
            tmp_req_txt.unlink()

    def _install_discover_utils(self, requirements_file=None):
        args = ["install", "--upgrade", "--force-reinstall"]
        package = "hcai-discover-utils"
        if not self.log_verbose:
            args.append("-q")
        try:
            # check if discover-utils version is specified in requirements
            if requirements_file is not None:
                with open(requirements_file, "r") as fd:
                    for req in fd.readlines():
                        if "hcai-discover-utils" in req:
                            package = req

            # else install same version as discover has
            else:
                import toml

                toml_file = Path(__file__) / ".." / ".." / ".." / "pyproject.toml"

                with open(toml_file.resolve(), "r") as f:
                    config = toml.load(f)
                    dependencies = config["project"]["dependencies"]
                    nu_dependency = list(
                        filter(lambda x: x.startswith("hcai-discover-utils"), dependencies)
                    )
                    if len(nu_dependency) == 1:

                        package = nu_dependency[0]
                    else:
                        raise ValueError(
                            f"Could not find unique version for hcai-discover-utils in {dependencies}"
                        )
        # in case of exception log error and install latest release
        except Exception as e:
            self.logger.exception(e)
            args.append("hcai-discover-utils")
        finally:
            args.append(f'"{package}"')
            run_cmd = vu.get_module_run_cmd(self.venv_dir, "pip", args=args)
            self._run_cmd(run_cmd)

    def __init__(
        self,
        module_dir: Path = None,
        logger: Logger = None,
        log_verbose: bool = False,
        extra_index_urls: list = None,
        force_requirements: bool = False,
    ):
        """
        Initializes the VenvHandler instance.

        Args:
            module_dir (Path, optional): The path to the module directory.
            logger (Logger, optional): The logger instance for logging.
            log_verbose (bool, optional): If True, log verbose output.
            force_requirements(bool, optional): If True, requirement.txt will always be installed. If false skipping requirements installation if venv already exist.
        """
        self.venv_dir = None
        self.current_process = None
        self.log_verbose = log_verbose
        self.module_dir = module_dir
        self.logger = logger if logger is not None else Logger(__name__)
        self.force_requirements = force_requirements
        self.extra_index_urls = extra_index_urls
        if module_dir is not None:
            self.init_venv()

    def init_venv(self):
        """
        Initializes the virtual environment and installs requirements.
        """
        self.logger.info(f"Initializing venv")
        venv_dir, existed = self._get_or_create_venv()
        self.venv_dir = venv_dir
        if not existed or self.force_requirements:
            self._install_requirements()
        self.logger.info(f"Venv {self.venv_dir} initialized")

    def run_python_script_from_file(
        self, script_fp: Path, script_args: list = None, script_kwargs: dict = None
    ):
        """
        Runs a Python script within the virtual environment.

        Args:
            script_fp (Path): The path to the script to run.
            script_args (list, optional): List of positional arguments to pass to the script.
            script_kwargs (dict, optional): Dictionary of keyword arguments to pass to the script.

        Raises:
            ValueError: If the virtual environment has not been initialized. Call `init_venv()` first.
            subprocess.CalledProcessError: If the executed command exits with a return value other than 0
        """
        if self.venv_dir is None:
            raise ValueError(
                "Virtual environment has not been initialized. Call <init_venv()> first."
            )
        run_cmd = vu.get_python_script_run_cmd(
            self.venv_dir, script_fp, script_args, script_kwargs
        )
        return_code = self._run_cmd(run_cmd)
        if not return_code == 0:
            raise subprocess.CalledProcessError(returncode=return_code, cmd=run_cmd)

    def run_shell_script(
        self, script: str, script_args: list = None, script_kwargs: dict = None
    ):
        """
        Runs a command in the respective os shell with an activated virtual environment


        Args:
            script (Path): The path to the script to run.
            script_args (list, optional): List of positional arguments to pass to the script.
            script_kwargs (dict, optional): Dictionary of keyword arguments to pass to the script.

        Raises:
            ValueError: If the virtual environment has not been initialized. Call `init_venv()` first.
            subprocess.CalledProcessError: If the executed command exits with a return value other than 0
        """
        if self.venv_dir is None:
            raise ValueError(
                "Virtual environment has not been initialized. Call <init_venv()> first."
            )
        run_cmd = vu.get_shell_script_run_cmd(
            self.venv_dir, script, script_args, script_kwargs
        )
        return_code = self._run_cmd(run_cmd)
        if not return_code == 0:
            raise subprocess.CalledProcessError(returncode=return_code, cmd=run_cmd)

    def kill(self):
        """Kills parent and children processess"""
        parent = psutil.Process(self.current_process.pid)
        # kill all the child processes
        for child in parent.children(recursive=True):
            try:
                self.logger.info(f"Killing process {child}")
                child.kill()
                # kill the parent process
                self.logger.info(f"Killing process {parent}")
                parent.kill()
            except psutil.NoSuchProcess:
                continue


if __name__ == "__main__":
    import logging
    load_dotenv()

    log_dir = Path(os.getenv("DISCOVER_LOG_DIR", "."))
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "test.log"
    logging.basicConfig(filename=log_file, encoding="utf-8", level=logging.DEBUG)
    logger = logging.getLogger("test_logger")

    module_path = Path(os.getenv("DISCOVER_CML_DIR")) / "test"
    venv_handler = VenvHandler(module_path, logger=logger, log_verbose=True)
    venv_handler.run_python_script_from_file(
        module_path / "test.py",
        script_args=["pos_1", "pos_2"],
        script_kwargs={"-k1": "k1", "--keyword_three": "k3"},
    )
