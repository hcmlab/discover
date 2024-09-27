""" Blueprint for querying job statuses

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    06.09.2023

This module defines a Flask Blueprint for querying the current status of a specific job or all logged jobs.

"""


from flask import Blueprint, request, jsonify
from discover.utils.job_utils import JOBS, get_all_jobs, JobStatus
from discover.utils.job_utils import get_job_id_from_request_form

status = Blueprint("status", __name__)


@status.route("/job_status", methods=["POST"])
def job_status():
    """
    Query the status of a specific job.

    This route allows querying the status of a job by providing the job's unique identifier in the request.

    Returns:
        dict: A JSON response containing the status of the requested job.

    Example:
        >>> POST /job_status
        >>> {"job_id": "12345"}
        {"status": "RUNNING"}
    """
    if request.method == "POST":
        request_form = request.form.to_dict()
        status_key = get_job_id_from_request_form(request_form)

        if status_key in JOBS.keys():
            status = JOBS[status_key].status
            return jsonify({"status": status.value})
        else:
            return jsonify({"status": JobStatus.WAITING.value})


@status.route("/job_status_all", methods=["GET"])
def job_status_all():
    """
     Query the status of all jobs.

     This route allows querying the status of a job by providing the job's unique identifier in the request.

     Returns:
         dict: A JSON response containing the status of the requested job.

     Example:
         >>> POST /job_status
         >>> {"job_id": "12345"}
         [{
            start_time = '09/13/2023, 16:51:27'
            end_time = None
            progress = 'Predicting data'
            status = JobStatus.RUNNING
            job_key = 12345
            interactive_url = interactive_url
            log_path = /logs/12345.log
            details = {'user' : 'my_user', 'dataset' : 'test' ... }
         }, ...]
     """
    return jsonify(get_all_jobs())
