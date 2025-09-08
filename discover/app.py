"""Standalone script for data predictions

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    06.09.2023

This script performs predictions for annotations in the NOVA database using a provided DISCOVER module for inference and saves the results to the NOVA-DB.

Args:
    --env (str, optional): Path to the environment file to read configuration from. Default: ''
    --host (str, optional): The host IP address for the server. Default: '0.0.0.0'
    --port (str, optional): The port on which the server will listen. Default: '8080'
    --cml_dir (str, optional): CML folder to read the training scripts from, same as in Nova. Default: 'cml'
    --data_dir (str, optional): Data folder to read the training scripts from, same as in Nova. Default: 'data'
    --cache_dir (str, optional): Cache folder where all large files (e.g., model weights) are cached. Default: 'cache'
    --tmp_dir (str, optional): Folder for temporary data storage. Default: 'tmp'
    --log_dir (str, optional): Folder for temporary data storage. Default: 'log'

Returns:
    None

Example:
    >>> app.py --host 0.0.0.0 --port 53771 --cml_dir "/path/to/my/cml" --data_dir "/path/to/my/data" --cache_dir "/path/to/my/cache" --tmp_dir "/path/to/my/tmp"
"""
import dotenv
import tempfile
import traceback
from werkzeug.exceptions import HTTPException
from flask import Flask, render_template
from discover import __version__
from discover.route.train import train
from discover.route.status import status
from discover.route.log import log
from discover.route.ui import ui
from discover.route.cml_info import cml_info
from discover.route.cancel import cancel
from discover.route.process import process
from discover.route.fetch_result import fetch_result
from discover.route.upload import upload
import argparse
import os
from pathlib import Path
#from waitress import serve
from cheroot.wsgi import Server as WSGIServer
from cheroot.ssl.builtin import BuiltinSSLAdapter
from discover.utils import env

print(f"Starting DISCOVER v{__version__}...")
app = Flask(__name__, template_folder="templates")
app.register_blueprint(train)
app.register_blueprint(process)
app.register_blueprint(log)
app.register_blueprint(status)
app.register_blueprint(ui)
app.register_blueprint(cancel)
app.register_blueprint(cml_info)
app.register_blueprint(fetch_result)
app.register_blueprint(upload)

parser = argparse.ArgumentParser(
    description="Commandline arguments to configure DISCOVER"
)
parser.add_argument(
    "--env",
    type=str,
    default="",
    help="Path to the environment file to read config from",
)
parser.add_argument("--host", type=str, default="0.0.0.0", help="The host ip address")
parser.add_argument(
    "--port", type=str, default="8080", help="The port the server listens on"
)
parser.add_argument(
    "--cml_dir",
    type=str,
    default="cml",
    help="Cml folder to read the training scripts from. Same as in Nova.",
)
parser.add_argument(
    "--data_dir",
    type=str,
    default="data",
    help="Data folder to read the training scripts from. Same as in Nova.",
)
parser.add_argument(
    "--cache_dir",
    type=str,
    default="cache",
    help="Cache folder where all large files (e.g. model weights) are cached.",
)

parser.add_argument(
    "--tmp_dir",
    type=str,
    default="tmp",
    help="Folder for temporary data storage.",
)
parser.add_argument(
    "--log_dir",
    type=str,
    default="log",
    help="Folder for temporary data storage.",
)

parser.add_argument(
    "--backend",
    type=str,
    default="venv",
    help="The backend used for processing requests",
)

parser.add_argument(
    "--video_backend",
    type=str,
    choices=["DECORD", "DECORDBATCH", "IMAGEIO", "MOVIEPY", "PYAV"],
    default="IMAGEIO",
    help="The backend used for reading videos requests",
)

parser.add_argument(
    "--use_tls",
    action="store_true",
    default=False,
    help="Enable TLS/SSL for HTTPS connections",
)


# Error Handling
@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    msg = traceback.format_exception(e, limit=0)
    
    # Sanitize the traceback before printing/returning
    sanitized_msg = []
    for line in msg:
        sanitized_line = _sanitize_traceback_line(line)
        sanitized_msg.append(sanitized_line)
    
    print(sanitized_msg)
    return sanitized_msg[0], 500


def _sanitize_traceback_line(line):
    """
    Sanitize a single traceback line to remove sensitive information like passwords.
    
    Args:
        line (str): The traceback line to sanitize.
        
    Returns:
        str: The sanitized traceback line.
    """
    import re
    
    # List of password-related patterns to sanitize
    password_patterns = [
        r'password["\']?\s*[:=]\s*["\']?([^"\',\s]+)["\']?',
        r'dbPassword["\']?\s*[:=]\s*["\']?([^"\',\s]+)["\']?', 
        r'db_password["\']?\s*[:=]\s*["\']?([^"\',\s]+)["\']?',
        r'--password\s+([^\s]+)',
        r'-p\s+([^\s]+)',
        r'PASSWORD["\']?\s*[:=]\s*["\']?([^"\',\s]+)["\']?',
    ]
    
    sanitized_line = line
    for pattern in password_patterns:
        sanitized_line = re.sub(pattern, lambda m: m.group(0).replace(m.group(1), "****"), sanitized_line, flags=re.IGNORECASE)
        
    return sanitized_line


def _run():

    # TODO: support multiple (data) directories
    args = parser.parse_args()
    default_args = parser.parse_args([])

    # Loading dot env file if provided
    env_path = Path(dotenv.find_dotenv())
    if args.env:
        env_path = Path(args.env)
        if not env_path.is_file():
            raise FileNotFoundError(f'.env file not found at {env_path} ')
    if env_path.is_file():
        print(f'Loading environment from {env_path.resolve()}')
        dotenv.load_dotenv(env_path, verbose=True, override=True)


    # Setting environment variables in the following priority from highest to lowest:
    # Provided commandline argument -> Dotenv environment variable -> System environment variable -> Default value

    def resolve_arg(arg_val, env_var, arg_default_val, create_directory=False):
        # Check if argument has been provided
        if not arg_val == arg_default_val:
            val = arg_val
        # Check if environment variable exists
        elif os.environ.get(env_var):
            val = os.environ[env_var]
        # Return default
        else:
            val = arg_default_val
        print(f"\t{env_var}: {val}")

        if create_directory:
            Path(val).mkdir(parents=False, exist_ok=True)

        return val

    print('\t#DISCOVER Config')
    os.environ[env.DISCOVER_HOST] = resolve_arg(
        args.host, env.DISCOVER_HOST, default_args.host
    )
    os.environ[env.DISCOVER_PORT] = resolve_arg(
        args.port, env.DISCOVER_PORT, default_args.port
    )

    os.environ[env.DISCOVER_CML_DIR] = resolve_arg(
        args.cml_dir, env.DISCOVER_CML_DIR, default_args.cml_dir
    )
    os.environ[env.DISCOVER_DATA_DIR] = resolve_arg(
        args.data_dir, env.DISCOVER_DATA_DIR, default_args.data_dir
    )
    os.environ[env.DISCOVER_CACHE_DIR] = resolve_arg(
        args.cache_dir,
        env.DISCOVER_CACHE_DIR,
        default_args.cache_dir,
        create_directory=True,
    )
    os.environ[env.DISCOVER_TMP_DIR] = resolve_arg(
        args.tmp_dir,
        env.DISCOVER_TMP_DIR,
        default_args.tmp_dir,
        create_directory=True,
    )
    os.environ[env.DISCOVER_LOG_DIR] = resolve_arg(
        args.log_dir,
        env.DISCOVER_LOG_DIR,
        default_args.log_dir,
        create_directory=True,
    )
    os.environ[env.DISCOVER_BACKEND] = resolve_arg(
        args.backend, env.DISCOVER_BACKEND, default_args.backend
    )

    os.environ[env.DISCOVER_VIDEO_BACKEND] = resolve_arg(
        args.video_backend, env.DISCOVER_VIDEO_BACKEND, default_args.video_backend
    )
    
    os.environ[env.DISCOVER_USE_TLS] = resolve_arg(
        str(args.use_tls), env.DISCOVER_USE_TLS, str(default_args.use_tls)
    )

    print('\n\t#Processing backend')

    os.environ[env.VENV_FORCE_UPDATE] = resolve_arg(
        "False", env.VENV_FORCE_UPDATE, "False"
    )
    os.environ[env.VENV_LOG_VERBOSE] = resolve_arg(
        "True", env.VENV_LOG_VERBOSE, "True"
    )

    print("...done")
    tempfile.tempdir = os.environ[env.DISCOVER_TMP_DIR]
    host = os.environ[env.DISCOVER_HOST]
    port = int(os.environ[env.DISCOVER_PORT])

    server = WSGIServer((host, port), app, numthreads=8)
    
    # Check if TLS is enabled
    use_tls = os.environ[env.DISCOVER_USE_TLS].lower() == 'true'
    
    if use_tls:
        ssl_cert = Path(__file__).parent / 'discover_cert.pem'
        ssl_key = Path(__file__).parent / 'discover_key.pem'
        
        if ssl_cert.exists() and ssl_key.exists():
            server.ssl_adapter = BuiltinSSLAdapter(str(ssl_cert), str(ssl_key))
            print(f"DISCOVER HTTPS server starting on {host}:{port}")
        else:
            print(f"SSL certificates not found at {ssl_cert} and {ssl_key}")
            print("To enable HTTPS, generate certificates with:")
            if host == '0.0.0.0':
                print("  For local access only:")
                print(f"    openssl req -x509 -newkey rsa:2048 -keyout {ssl_key} -out {ssl_cert} -days 365 -nodes -subj '/CN=localhost'")
                print("  For local + external access (replace YOUR_EXTERNAL_IP with actual server IP):")
                print(f"    openssl req -x509 -newkey rsa:2048 -keyout {ssl_key} -out {ssl_cert} -days 365 -nodes \\")
                print(f"      -subj '/CN=YOUR_EXTERNAL_IP' -addext 'subjectAltName=DNS:localhost,IP:127.0.0.1,IP:YOUR_EXTERNAL_IP'")
            else:
                print(f"  For configured host ({host}):")
                print(f"    openssl req -x509 -newkey rsa:2048 -keyout {ssl_key} -out {ssl_cert} -days 365 -nodes \\")
                print(f"      -subj '/CN={host}' -addext 'subjectAltName=DNS:localhost,IP:127.0.0.1,IP:{host}'")
            print(f"Aborting...")
            return
    else:
        print(f"DISCOVER HTTP server starting on {host}:{port}")
    
    server.start()

if __name__ == "__main__":
    _run()
