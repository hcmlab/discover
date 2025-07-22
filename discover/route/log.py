""" Blueprint for retrieving a job's log file

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    06.09.2023

This module defines a Flask Blueprint for retrieving a job's log file.

"""

from flask import Blueprint, request, jsonify, Response
from discover.utils import log_utils
from discover.utils.job_utils import get_job_id_from_request_form
from pathlib import Path


log = Blueprint("log", __name__)


@log.route("/log/<job_key>", methods=["GET"])
def get_log(job_key):
    """
    Retrieve the log file for a specific job via GET request.
    
    Args:
        job_key (str): The job identifier
        
    Returns:
        str: Raw log file content or error message
    """
    from discover.utils import job_utils
    try:
        log_path = job_utils.get_log_path(job_key)
        if log_path and Path(log_path).exists():
            with open(log_path, 'r') as f:
                log_content = f.read()
            return Response(log_content, mimetype='text/plain')
        else:
            return f"Log file not found for job {job_key}", 404
    except Exception as e:
        return f"Error retrieving log: {str(e)}", 500


@log.route("/log", methods=["POST"])
def log_thread():
    """
    Retrieve the log file for a specific job.

    This route allows retrieving the log file for a job by providing the job's unique identifier in the request.

    Returns:
        dict: A JSON response containing the log file content.

    Example:
        >>> POST /log
        >>> {"job_id": "12345"}
        {"message": "Log file content here..."}
    """
    if request.method == "POST":
        request_form = request.form.to_dict()
        log_key = get_job_id_from_request_form(request_form)
        if log_key in log_utils.LOGS:
            logger = log_utils.LOGS[log_key]
            path = logger.handlers[0].baseFilename
            with open(path) as f:
                f = f.readlines()
            output = ""
            for line in f:
                output += line
            return jsonify({"message": output})
        else:
            return jsonify({"message": "No log for the given parameters found."})
