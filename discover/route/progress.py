""" Blueprint for updating job progress

Author:
    Tobias Hallmen
Date:
    26.11.2025

This module defines a Flask Blueprint for updating job progress from subprocesses.

"""

from flask import Blueprint, request, jsonify
from discover.utils import job_utils

progress = Blueprint("progress", __name__)


@progress.route("/api/update_progress", methods=["POST"])
def update_job_progress():
    """
    Update the progress of a running job.

    This route allows subprocesses to update job progress by providing the job ID and progress value.

    Expected POST data:
        job_key (str): The unique identifier of the job
        progress (str): The progress value (e.g., "2/5")

    Returns:
        dict: A JSON response indicating success or failure.

    Example:
        >>> POST /api/update_progress
        >>> {"job_key": "12345", "progress": "2/5"}
        {"success": true}
    """
    if request.method == "POST":
        data = request.get_json() or {}
        job_key = data.get("job_key")
        progress_value = data.get("progress")

        if not job_key or not progress_value:
            return jsonify({"success": False, "error": "Missing job_key or progress"}), 400

        try:
            job_utils.update_progress(job_key, progress_value)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
