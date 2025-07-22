from flask import Blueprint, render_template
from discover.utils import job_utils

ui = Blueprint("ui", __name__)
#TODO remove

@ui.route("/")
def index():
    jobs = job_utils.get_all_jobs()
    return render_template("index.html", title="Current Jobs", jobs=jobs)


@ui.route("/data")
def data():
    return {"data": job_utils.get_all_jobs()}
