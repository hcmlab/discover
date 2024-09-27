""" Blueprint for data extraction

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    06.09.2023

This module defines a Flask Blueprint for extracting data.

"""


from pathlib import Path
from flask import Blueprint, request, jsonify
from discover.utils.thread_utils import THREADS
from discover.utils.job_utils import get_job_id_from_request_form
from discover.utils import thread_utils, job_utils
from discover.utils import log_utils
from discover.exec.execution_handler import NovaExtractHandler

extract = Blueprint("extract", __name__)


@extract.route("/extract", methods=["POST"])
def predict_thread():
    """
    Start a data extraction job.

    This route allows starting a data extraction job by providing the required parameters in the request.

    Returns:
        dict: A JSON response indicating the success of the job initiation.

    Example:
        >>> POST /extract
        >>> {"param1": "value1", "param2": "value2"}
        {"success": "true"}
    """
    if request.method == "POST":
        request_form = request.form.to_dict()
        key = get_job_id_from_request_form(request_form)
        job_utils.add_new_job(key, request_form=request_form)
        thread = extract_data(request_form)
        thread.start()
        THREADS[key] = thread
        data = {"success": "true"}
        return jsonify(data)


@thread_utils.ml_thread_wrapper
def extract_data(request_form):
    """
    Extract data in a separate thread.

    Args:
        request_form (dict): A dictionary containing the request parameters.

    Returns:
        None

    This function runs the data extraction process in a separate thread.

    """
    job_id = get_job_id_from_request_form(request_form)

    job_utils.update_status(job_id, job_utils.JobStatus.RUNNING)
    logger = log_utils.get_logger_for_job(job_id)
    handler = NovaExtractHandler(request_form, logger=logger)

    # TODO replace .env with actual path
    dotenv_path = Path(".env").resolve()

    try:
        handler.run()
        job_utils.update_status(job_id, job_utils.JobStatus.FINISHED)
    except Exception as e:
        logger.critical(f"Job failed with exception {str(e)}")
        job_utils.update_status(job_id, job_utils.JobStatus.ERROR)
