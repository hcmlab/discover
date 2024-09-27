""" Class definition for th execution handler. The execution handler combines uses data from the request form to execute
the correct command using the specified backends.

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    06.09.2023
"""
import importlib
import os
import re
from logging import Logger
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from pathlib import PureWindowsPath
from discover.utils import env
from discover_utils.utils.string_utils import string_to_bool


class Action(Enum):
    PROCESS = "du-process"
    TRAIN = "du-train"


class Backend(Enum):
    DEBUG = "debug"
    VENV = "venv"


class ExecutionHandler(ABC):
    @property
    def script_arguments(self):
        return self._script_arguments

    @script_arguments.setter
    def script_arguments(self, value):
        # convert dictionary keys from camelCase to snake_case
        self._script_arguments = {
            "--" + re.sub(r"(?<!^)(?=[A-Z])(?<![A-Z])", "_", k).lower(): v
            for k, v in value.items()
        }

    def __init__(
        self, request_form: dict, backend: str = "venv", logger: Logger = None
    ):
        self.backend = Backend(backend)
        self.script_arguments = request_form
        self.logger = logger
        self.backend_handler = None

    def _nova_server_env_to_arg(self):
        arg_vars = {}
        prefix = "DISCOVER_"

        # Select data folder, where dataset exists if multiple folders are passed
        dd = os.getenv(env.DISCOVER_DATA_DIR)
        ds = self.script_arguments.get("--dataset")
        if ds is not None:
            if ";" in dd:
                for dir in dd.split(";"):
                    dataset_dir = Path(dir) / ds
                    if dataset_dir.is_dir():
                        os.environ[env.DISCOVER_DATA_DIR] = str(dataset_dir.parent)
                        break

        # set other vars
        env_vars = [
            env.DISCOVER_CML_DIR,
            env.DISCOVER_DATA_DIR,
            env.DISCOVER_LOG_DIR,
            env.DISCOVER_CACHE_DIR,
            env.NOVA_SERVER_TMP_DIR,
            env.DISCOVER_VIDEO_BACKEND,
        ]

        for var in env_vars:
            k = "--" + var[len(prefix) :].lower()
            v = os.getenv(var)
            arg_vars[k] = v
        return arg_vars

    def run(self):

        # Run with selected backend
        if self.backend == Backend.DEBUG:
            from importlib.machinery import SourceFileLoader
            import discover_utils as nu
            from importlib.metadata import entry_points

            ep = [
                x
                for x in entry_points().get("console_scripts")
                if x.name == self.run_script
            ][0]
            run_module = importlib.import_module(ep.module)
            main = getattr(run_module, "main")

            # Add dotenv variables to arguments for script
            self._script_arguments |= self._nova_server_env_to_arg()
            self._script_arguments.setdefault(
                "--shared_dir", os.getenv(env.NOVA_SERVER_TMP_DIR)
            )

            args = []
            for k, v in self._script_arguments.items():
                args.append(k)
                args.append(v)

            main(args)

        elif self.backend == Backend.VENV:
            from discover.backend import virtual_environment as backend

            # Setup virtual environment
            cml_dir = os.getenv(env.DISCOVER_CML_DIR)
            if cml_dir is None:
                raise ValueError(f"NOVA_CML_DIR not set")

            module_dir = Path(cml_dir) / self.module_name
            if not module_dir.is_dir():
                raise NotADirectoryError(
                    f"NOVA_CML_DIR {module_dir} is not a valid directory"
                )

            extra_index_urls = os.getenv(env.VENV_EXTRA_INDEX_URLS, None)
            if extra_index_urls is not None:
                extra_index_urls = extra_index_urls.split(";")

            self.backend_handler = backend.VenvHandler(
                module_dir,
                logger=self.logger,
                log_verbose=string_to_bool(os.getenv(env.VENV_LOG_VERBOSE, "True")),
                force_requirements=string_to_bool(
                    os.getenv(env.VENV_FORCE_UPDATE, "False"),
                ),
                extra_index_urls=extra_index_urls,
            )

            # Add dotenv variables to arguments for script
            self._script_arguments |= self._nova_server_env_to_arg()
            self._script_arguments.setdefault(
                "--shared_dir", os.getenv(env.NOVA_SERVER_TMP_DIR)
            )

            self.backend_handler.run_shell_script(
                self.run_script,
                script_kwargs=self._script_arguments,
            )

        else:
            raise ValueError(f"Unknown backend {self.backend}")

    def cancel(self):
        if self.backend == Backend.VENV:
            self.backend_handler.kill()

    @property
    @abstractmethod
    def run_script(self):
        pass

    @property
    @abstractmethod
    def module_name(self):
        pass


class NovaProcessHandler(ExecutionHandler):
    @property
    def module_name(self):
        tfp = self.script_arguments.get("--trainer_file_path")
        if tfp is None:
            raise ValueError("trainerFilePath not specified in request.")
        else:
            return PureWindowsPath(tfp).parent

    @property
    def run_script(self):
        return self.action.value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action = Action.PROCESS


class NovaTrainHandler(ExecutionHandler):
    @property
    def module_name(self):
        tfp = self.script_arguments.get("--trainer_file_path")
        if tfp is None:
            raise ValueError("trainerFilePath not specified in request.")
        else:
            return PureWindowsPath(tfp).parent

    @property
    def run_script(self):
        return self.action.value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action = Action.TRAIN
