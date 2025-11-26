""" Blueprint for canceling a job

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    06.09.2023

This module defines a Flask Blueprint for canceling a job.

"""

from flask import Blueprint, request, jsonify
from discover.utils import job_utils
from discover.utils.job_utils import get_job_id_from_request_form
from discover.utils.thread_utils import THREADS
from discover.utils.log_utils import LOGS


cancel = Blueprint("cancel", __name__)


@cancel.route("/cancel", methods=["POST"])
def complete_thread():
    """
    Cancel a running job.

    This route allows canceling a running job by providing the job's unique identifier in the request.

    Returns:
        dict: A JSON response indicating whether the cancelation was successful.

    Example:
        >>> POST /cancel
        >>> {"job_id": "12345"}
        {"success": "true"}
    """
    #TODO cancel job based on backend
    if request.method == "POST":
        request_form = request.form.to_dict()
        key = get_job_id_from_request_form(request_form)

        job = job_utils.get_job(key)
        if not job is None:
            job.was_canceled = True
            job.cancel()

        if key in THREADS:
            thread = THREADS[key]
            thread.raise_exception()
            job_utils.update_status(key, job_utils.JobStatus.CANCELED)
            if key in LOGS:
                log = LOGS[key]
                log.info("Action successfully canceled.")
            return jsonify({"success": "true"})
        else:
            if key in LOGS:
                log = LOGS[key]
                log.info("Cancel was not successful.")
            return jsonify({"success": "false"})
