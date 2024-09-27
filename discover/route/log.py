""" Blueprint for retrieving a job's log file

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    06.09.2023

This module defines a Flask Blueprint for retrieving a job's log file.

"""

from flask import Blueprint, request, jsonify
from discover.utils import log_utils
from discover.utils.job_utils import get_job_id_from_request_form


log = Blueprint("log", __name__)


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
