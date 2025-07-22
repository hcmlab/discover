""" Blueprint for data prediction

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    20.09.2023

This module defines a Flask Blueprint for predicting data.

"""
import os

from flask import Blueprint, request, jsonify
from discover.utils.thread_utils import THREADS
from discover.utils.job_utils import get_job_id_from_request_form
from discover.utils import thread_utils, job_utils, env
from discover.utils import log_utils
from discover.exec.execution_handler import NovaProcessHandler

process = Blueprint("process", __name__)


@process.route("/process", methods=["POST"])
def predict_thread():
    if request.method == "POST":
        request_form = request.form.to_dict()
        job_id = get_job_id_from_request_form(request_form)
        job_added = job_utils.add_new_job(job_id, request_form=request_form)
        thread = process_data(request_form, job_id)
        thread.start()
        THREADS[job_id] = thread
        data = {"success": str(job_added)}
        return jsonify(data)


@thread_utils.ml_thread_wrapper
def process_data(request_form, job_id):
    #job_id = get_job_id_from_request_form(request_form)
    job_utils.update_status(job_id, job_utils.JobStatus.RUNNING)
    logger = log_utils.get_logger_for_job(job_id)
    logger.info(log_utils.sanitize_sensitive_data(request_form))

    job = job_utils.get_job(job_id)
    job.execution_handler = NovaProcessHandler(request_form, logger=logger, backend=os.getenv(env.DISCOVER_BACKEND))

    try:
        job.run()
        job_utils.update_status(job_id, job_utils.JobStatus.FINISHED)
    except Exception as e:
        logger.critical(f"Job failed with exception {str(e)}")
        job_utils.update_status(job_id, job_utils.JobStatus.ERROR)
