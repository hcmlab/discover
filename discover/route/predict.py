""" Blueprint for data prediction

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    06.09.2023

This module defines a Flask Blueprint for predicting data.

"""


from pathlib import Path
from flask import Blueprint, request, jsonify
from discover.utils.thread_utils import THREADS
from discover.utils.job_utils import get_job_id_from_request_form
from discover.utils import thread_utils, job_utils
from discover.utils import log_utils
from discover.exec.execution_handler import NovaPredictHandler

predict = Blueprint("predict", __name__)


@predict.route("/predict", methods=["POST"])
def predict_thread():
    if request.method == "POST":
        request_form = request.form.to_dict()
        key = get_job_id_from_request_form(request_form)
        job_utils.add_new_job(key, request_form=request_form)
        thread = predict_data(request_form)
        thread.start()
        THREADS[key] = thread
        data = {"success": "true"}
        return jsonify(data)


@thread_utils.ml_thread_wrapper
def predict_data(request_form):
    job_id = get_job_id_from_request_form(request_form)

    job_utils.update_status(job_id, job_utils.JobStatus.RUNNING)
    logger = log_utils.get_logger_for_job(job_id)
    handler = NovaPredictHandler(request_form, logger=logger)

    try:
        handler.run()
        job_utils.update_status(job_id, job_utils.JobStatus.FINISHED)
    except Exception as e:
        logger.critical(f"Job failed with exception {str(e)}")
        job_utils.update_status(job_id, job_utils.JobStatus.ERROR)
