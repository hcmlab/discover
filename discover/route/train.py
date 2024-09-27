"""General process logic for train route

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    06.09.2023

"""


from pathlib import Path
from flask import Blueprint, request, jsonify
from discover.utils.thread_utils import THREADS
from discover.utils.job_utils import get_job_id_from_request_form
from discover.utils import thread_utils, job_utils
from discover.utils import log_utils
from discover.exec.execution_handler import NovaTrainHandler

train = Blueprint("train", __name__)


@train.route("/train", methods=["POST"])
def predict_thread():
    if request.method == "POST":
        request_form = request.form.to_dict()
        key = get_job_id_from_request_form(request_form)
        job_utils.add_new_job(key, request_form=request_form)
        thread = train_model(request_form)
        thread.start()
        THREADS[key] = thread
        data = {"success": "true"}
        return jsonify(data)


@thread_utils.ml_thread_wrapper
def train_model(request_form):
    key = get_job_id_from_request_form(request_form)

    job_utils.update_status(key, job_utils.JobStatus.RUNNING)
    logger = log_utils.get_logger_for_job(key)
    handler = NovaTrainHandler(request_form, logger=logger)

    # TODO replace .env with actual path
    dotenv_path = Path(".env").resolve()

    try:
        handler.run(dotenv_path)
        job_utils.update_status(key, job_utils.JobStatus.FINISHED)
    except:
        job_utils.update_status(key, job_utils.JobStatus.ERROR)
