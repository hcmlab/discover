"""Utility modules for NOVA-Server Logs

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    13.09.2023

"""

import logging
import threading
import os
from pathlib import Path
from discover.utils import job_utils, env

LOGS = {}

class SensitiveFormatter(logging.Formatter):
    """Formatter that removes sensitive information - now uses centralized sanitization."""
    def format(self, record):
        # Note: The sanitization is now handled at the data level via sanitize_sensitive_data()
        # This formatter is kept for compatibility but no longer needs regex filtering
        return logging.Formatter.format(self, record)

def sanitize_sensitive_data(data):
    """Sanitize sensitive information from any dictionary or request form"""
    import copy
    
    if not data:
        return data
        
    # Create a copy to avoid modifying original
    sanitized = copy.deepcopy(dict(data))
    
    # Replace known password keys with masked values  
    password_keys = ['password', 'dbPassword', 'db_password']
    for key in password_keys:
        if key in sanitized:
            sanitized[key] = "****"
    
    return sanitized

def get_log_conform_request(request_form):
    """Sanitize sensitive information from request form for logging"""
    return sanitize_sensitive_data(request_form)


def get_log_path_for_thread(job_id):
    log_dir = os.environ[env.DISCOVER_LOG_DIR]
    return Path(log_dir) / (job_id + ".log")


def init_logger(logger, job_id):
    print("Init logger" + str(threading.current_thread().name))
    try:
        log_path = get_log_path_for_thread(job_id)
        job_utils.set_log_path(job_id, log_path)
        file_handler = logging.FileHandler(log_path, "w")
        stream_handler = logging.getLogger().handlers[0]
        file_handler.setFormatter(
            SensitiveFormatter(
                fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        stream_handler.setFormatter(
            SensitiveFormatter(
                fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
        LOGS[job_id] = logger
        return logger
    except Exception as e:
        print(
            "Logger for {} could not be initialized.".format(
                str(threading.current_thread().name)
            )
        )
        raise e


def get_logger_for_job(job_id):
    logger = logging.getLogger(job_id)
    if not logger.handlers:
        logger = init_logger(logger, job_id)
    return logger


def remove_log_from_dict(job_id):
    LOGS.pop(job_id)
